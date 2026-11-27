# FlowPilot | Automatización de procesos

![Pruebas](https://github.com/AndresJG20/business-process-automation/actions/workflows/ci.yml/badge.svg)

Proyecto de portafolio para organizar tareas y automatizar el seguimiento de sus fechas de vencimiento. Busca resolver un problema frecuente: realizar recordatorios manualmente sin contar con un registro de los envíos ni de los errores.

## Funcionamiento

Se registra un flujo de trabajo y se crean tareas con un responsable y una fecha de vencimiento. El motor genera un recordatorio al llegar esa fecha y otro siete días después. Cada evento se almacena de forma independiente para evitar duplicados. Si la entrega falla, el motor vuelve a intentarlo con una espera creciente, hasta un máximo de tres intentos.

El destino de las notificaciones es una base de datos local de demostración; no se envían correos reales.

## Tecnologías

Python, FastAPI, SQLite, Docker Compose, pytest y GitHub Actions.

## Instalación en Windows

Desde PowerShell, con Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn flowpilot.api:app
```

Abre http://localhost:8000/docs para interactuar con la API.

## Ejemplo de uso

1. Ejecuta POST /workflows con {"name":"Seguimiento de solicitudes"}.
2. Ejecuta POST /tasks con el identificador del flujo creado y una fecha vencida. Por ejemplo:

```json
{
  "workflow_id": 1,
  "owner": "analista@example.test",
  "title": "Revisar solicitud de prueba",
  "due": "2025-01-01"
}
```

3. Ejecuta POST /runs para procesar los recordatorios.
4. Consulta GET /events para comprobar los resultados.
5. Vuelve a ejecutar POST /runs: no deben generarse recordatorios duplicados.
6. Marca la tarea como completada con POST /tasks/{task_id}/complete.

Para ejecutar el proceso periódicamente, abre otra terminal con el mismo entorno virtual y ejecuta:

```bash
python -m flowpilot.worker
```

También puedes iniciar ambos servicios con docker compose up --build.

## Organización del código

| Archivo o carpeta | Responsabilidad |
| --- | --- |
| flowpilot/api.py | Rutas de la API |
| flowpilot/database.py | Esquema y transacciones |
| flowpilot/repository.py | Consultas y cambios en la base |
| flowpilot/engine.py | Generación, entrega y reintentos |
| flowpilot/adapters.py | Destino simulado de notificaciones |
| flowpilot/worker.py | Ejecución periódica |
| tests/ | Pruebas de reglas e integración |

## Pruebas

```bash
python -m pytest -q
```

Las pruebas cubren la prevención de duplicados, los reintentos, la cancelación y el recorrido de la API.

## Alcance

Demostración local con datos ficticios. No incluye autenticación, integración real con correo, editor gráfico ni procesamiento distribuido. No se recomienda exponer la API a Internet.

Más información: [arquitectura](docs/architecture.md).
