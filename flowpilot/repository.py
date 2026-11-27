from .database import transaction

class Repository:
    def __init__(self, path):
        self.path = path

    def create_workflow(self, name):
        with transaction(self.path) as db:
            cursor = db.execute("INSERT INTO workflows(name) VALUES(?)", (name,))
            return cursor.lastrowid

    def create_task(self, data):
        with transaction(self.path) as db:
            cursor = db.execute(
                "INSERT INTO tasks(workflow_id,owner,title,due) VALUES(?,?,?,?)",
                (data.workflow_id,data.owner,data.title,data.due.isoformat()))
            return cursor.lastrowid

    def list_tasks(self):
        with transaction(self.path) as db:
            return [dict(row) for row in db.execute("SELECT * FROM tasks ORDER BY id DESC")]

    def list_workflows(self):
        with transaction(self.path) as db:
            return [dict(row) for row in db.execute("SELECT * FROM workflows ORDER BY id")]

    def complete(self, task_id):
        with transaction(self.path) as db:
            changed = db.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,)).rowcount
            db.execute("UPDATE outbox SET state='CANCELLED' WHERE task_id=? AND state='PENDING'", (task_id,))
            return bool(changed)

    def events(self):
        with transaction(self.path) as db:
            return [dict(row) for row in db.execute("SELECT * FROM outbox ORDER BY id DESC LIMIT 200")]
