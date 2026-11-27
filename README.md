# FlowPilot — Business Process Automation
![CI](https://github.com/AndresJG20/business-process-automation/actions/workflows/ci.yml/badge.svg)

A modular automation engine with REST API, persistent tasks, scheduled worker, transactional outbox, duplicate suppression, retries, dead-letter state and cancellation. Uses fictional data and a simulated notification destination.

## Start
Python 3.12:
```bash
pip install -r requirements-dev.txt
python -m uvicorn flowpilot.api:app
```
Open http://localhost:8000/docs. Create a workflow, create a task with a past due date, then POST /runs and GET /events. Run python -m flowpilot.worker in another terminal to process periodically. Or use docker compose up --build.

## Tests
python -m pytest -q

## Architecture
See [design](docs/architecture.md). Modules separate API, validation, persistence, engine, adapters and worker. No external email, authentication, visual workflow editor or distributed queue yet. Do not expose this local demo to the internet.
