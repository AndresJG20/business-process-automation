import json
from datetime import datetime, date, timedelta, timezone
from .database import transaction

def utcnow():
    return datetime.now(timezone.utc)

def enqueue(path, now):
    created = 0
    with transaction(path) as db:
        rows = db.execute("""SELECT t.* FROM tasks t JOIN workflows w ON w.id=t.workflow_id
                             WHERE t.completed=0 AND w.enabled=1""").fetchall()
        for row in rows:
            delay = (now.date() - date.fromisoformat(row["due"])).days
            for stage, threshold in ((1,0),(2,7)):
                if delay < threshold:
                    continue
                payload = json.dumps({"task_id":row["id"],"owner":row["owner"],
                                      "title":row["title"],"stage":stage})
                cursor = db.execute("""INSERT OR IGNORE INTO outbox(task_id,stage,payload,available_at)
                                       VALUES(?,?,?,?)""",(row["id"],stage,payload,now.isoformat()))
                created += cursor.rowcount
    return created

def dispatch(path, adapter, now, limit=100, max_attempts=3):
    """Single local worker; database transaction serializes event claims."""
    results = {"sent":0,"retried":0,"failed":0}
    for _ in range(limit):
        with transaction(path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""SELECT * FROM outbox WHERE state='PENDING'
                               AND available_at<=? ORDER BY id LIMIT 1""",(now.isoformat(),)).fetchone()
            if row is None:
                break
            attempts = row["attempts"] + 1
            try:
                adapter.send(json.loads(row["payload"]), str(row["id"]))
            except Exception as exc:
                terminal = attempts >= max_attempts
                db.execute("UPDATE outbox SET attempts=?,state=?,available_at=?,error=? WHERE id=?",
                           (attempts,"FAILED" if terminal else "PENDING",
                            (now+timedelta(minutes=2**attempts)).isoformat(),
                            type(exc).__name__,row["id"]))
                results["failed" if terminal else "retried"] += 1
            else:
                db.execute("UPDATE outbox SET attempts=?,state='SENT',error=NULL WHERE id=?",(attempts,row["id"]))
                results["sent"] += 1
    return results
