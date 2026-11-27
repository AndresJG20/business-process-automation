import sqlite3
from datetime import datetime, timezone, timedelta, date
from flowpilot.database import initialize
from flowpilot.repository import Repository
from flowpilot.schemas import TaskInput
from flowpilot.engine import enqueue, dispatch
from flowpilot.adapters import LocalNotificationAdapter

def setup(tmp_path):
    path=tmp_path/"workflow.db"
    initialize(path)
    repo=Repository(path)
    wid=repo.create_workflow("Demo")
    tid=repo.create_task(TaskInput(workflow_id=wid,owner="demo@example.test",title="Demo task",due=date(2026,1,1)))
    return path,repo,tid

def test_idempotency(tmp_path):
    path,repo,_=setup(tmp_path)
    now=datetime(2026,1,8,tzinfo=timezone.utc)
    assert enqueue(path,now)==2
    assert enqueue(path,now)==0
    dest=tmp_path/"notifications.db"
    assert dispatch(path,LocalNotificationAdapter(dest),now)["sent"]==2
    assert dispatch(path,LocalNotificationAdapter(dest),now)["sent"]==0
    with sqlite3.connect(dest) as db:
        assert db.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]==2

def test_retry_and_dead_letter(tmp_path):
    path,repo,_=setup(tmp_path)
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    enqueue(path,now)
    class Broken:
        def send(self,payload,event_id):
            raise RuntimeError("simulated")
    assert dispatch(path,Broken(),now)["retried"]==1
    assert dispatch(path,Broken(),now)["retried"]==0
    assert dispatch(path,Broken(),now+timedelta(minutes=4))["retried"]==1
    assert dispatch(path,Broken(),now+timedelta(minutes=12))["failed"]==1
    assert repo.events()[0]["state"]=="FAILED"

def test_cancel(tmp_path):
    path,repo,tid=setup(tmp_path)
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    enqueue(path,now)
    assert repo.complete(tid)
    assert repo.events()[0]["state"]=="CANCELLED"
    assert enqueue(path,now+timedelta(days=9))==0
