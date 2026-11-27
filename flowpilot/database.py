import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS workflows (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, enabled INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS tasks (
 id INTEGER PRIMARY KEY, workflow_id INTEGER NOT NULL REFERENCES workflows(id),
 owner TEXT NOT NULL, title TEXT NOT NULL, due TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS outbox (
 id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL REFERENCES tasks(id),
 stage INTEGER NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'PENDING',
 attempts INTEGER NOT NULL DEFAULT 0, available_at TEXT NOT NULL, error TEXT,
 UNIQUE(task_id, stage)
);
CREATE INDEX IF NOT EXISTS idx_outbox_pending ON outbox(state, available_at);
CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(completed, due);
"""

@contextmanager
def transaction(path):
    connection = sqlite3.connect(path, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()

def initialize(path):
    with transaction(path) as connection:
        connection.executescript(SCHEMA)
