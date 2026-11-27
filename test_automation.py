import unittest
from datetime import date
from automation import connect,run

class WorkflowTests(unittest.TestCase):
    def test_idempotence(self):
        c=connect(":memory:")
        c.execute("INSERT INTO tasks(owner,due) VALUES('demo','2026-01-01')")
        self.assertEqual(len(run(c,date(2026,1,1))),1)
        self.assertEqual(run(c,date(2026,1,1)),[])
        self.assertEqual(len(run(c,date(2026,1,8))),1)
        c.close()
    def test_closed(self):
        c=connect(":memory:")
        c.execute("INSERT INTO tasks(owner,due,done) VALUES('demo','2026-01-01',1)")
        self.assertEqual(run(c,date(2026,2,1)),[])
        c.close()
