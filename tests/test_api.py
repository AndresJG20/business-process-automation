from fastapi.testclient import TestClient
from flowpilot.api import create_app

def test_workflow_api(tmp_path):
    with TestClient(create_app(tmp_path/"flow.db",tmp_path/"destination.db")) as c:
        wid=c.post("/workflows",json={"name":"Onboarding"}).json()["id"]
        assert c.post("/workflows",json={"name":"Onboarding"}).status_code==409
        response=c.post("/tasks",json={"workflow_id":wid,"owner":"demo@example.test","title":"Review request","due":"2020-01-01"})
        assert response.status_code==201
        assert c.post("/runs").json()["sent"]==2
        assert c.post("/runs").json()["sent"]==0
        assert c.post("/tasks/"+str(response.json()["id"])+"/complete").status_code==200


def test_invalid_task_requests(tmp_path):
    with TestClient(create_app(tmp_path/"flow.db", tmp_path/"destination.db")) as c:
        payload = {"workflow_id":999,"owner":"demo@example.test","title":"Revisar solicitud","due":"2026-01-01"}
        assert c.post("/tasks", json=payload).status_code == 422
        assert c.post("/tasks", json={**payload,"due":"fecha incorrecta"}).status_code == 422
        assert c.post("/tasks/999/complete").status_code == 404
