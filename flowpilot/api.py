import os
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from .database import initialize
from .repository import Repository
from .schemas import WorkflowInput, TaskInput
from .engine import enqueue, dispatch, utcnow
from .adapters import LocalNotificationAdapter

def create_app(path=None, notification_path=None):
    path = path or os.getenv("FLOWPILOT_DB","flowpilot.db")
    notification_path = notification_path or os.getenv("FLOWPILOT_NOTIFICATIONS","notifications.db")
    repo = Repository(path)
    @asynccontextmanager
    async def lifespan(app):
        initialize(path)
        yield
    app = FastAPI(title="FlowPilot", version="0.2.0", lifespan=lifespan)

    @app.get("/health")
    def health():
        return {"status":"ok"}

    @app.post("/workflows", status_code=201)
    def create_workflow(data: WorkflowInput):
        try:
            return {"id":repo.create_workflow(data.name)}
        except sqlite3.IntegrityError:
            raise HTTPException(409,"El flujo de trabajo ya existe")

    @app.get("/workflows")
    def workflows():
        return repo.list_workflows()

    @app.post("/tasks", status_code=201)
    def create_task(data: TaskInput):
        try:
            return {"id":repo.create_task(data)}
        except sqlite3.IntegrityError:
            raise HTTPException(422,"Flujo de trabajo no encontrado")

    @app.get("/tasks")
    def tasks():
        return repo.list_tasks()

    @app.post("/tasks/{task_id}/complete")
    def complete(task_id: int):
        if not repo.complete(task_id):
            raise HTTPException(404,"Tarea no encontrada")
        return {"completed":True}

    @app.post("/runs")
    def execute():
        now = utcnow()
        count = enqueue(path,now)
        result = dispatch(path,LocalNotificationAdapter(notification_path),now)
        return {"queued":count,**result}

    @app.get("/events")
    def events():
        return repo.events()
    return app

app = create_app()
