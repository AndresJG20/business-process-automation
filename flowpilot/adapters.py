import json
import sqlite3

class LocalNotificationAdapter:
    """A durable simulated destination. Unique event IDs make delivery idempotent."""
    def __init__(self, path):
        self.path = path

    def send(self, payload, event_id):
        connection = sqlite3.connect(self.path)
        try:
            with connection:
                connection.execute("CREATE TABLE IF NOT EXISTS notifications(event_id TEXT PRIMARY KEY,payload TEXT NOT NULL)")
                connection.execute("INSERT OR IGNORE INTO notifications VALUES(?,?)",(event_id,json.dumps(payload)))
        finally:
            connection.close()
