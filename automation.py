import sqlite3, json, argparse
from datetime import date, timedelta

def connect(path="workflow.db"):
    c=sqlite3.connect(path)
    c.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, owner TEXT, due TEXT, done INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS reminders(task_id INTEGER, stage INTEGER, sent_at TEXT, PRIMARY KEY(task_id,stage))")
    return c

def run(c,today):
    events=[]
    with c:
        for tid,owner,due in c.execute("SELECT id,owner,due FROM tasks WHERE done=0").fetchall():
            delay=(today-date.fromisoformat(due)).days
            for stage,threshold in [(1,0),(2,7)]:
                if delay>=threshold:
                    inserted=c.execute("INSERT OR IGNORE INTO reminders VALUES(?,?,?)",(tid,stage,today.isoformat())).rowcount
                    if inserted:
                        events.append({"task_id":tid,"owner":owner,"stage":stage,"overdue_days":delay})
    return events

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=["demo","run"])
    p.add_argument("--db",default="workflow.db")
    args=p.parse_args()
    with connect(args.db) as c:
        if args.command=="demo":
            c.execute("INSERT INTO tasks(owner,due) VALUES(?,?)",("demo@example.test",(date.today()-timedelta(days=8)).isoformat()))
        else:
            print(json.dumps(run(c,date.today()),indent=2))
