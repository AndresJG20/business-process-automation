# FlowPilot — Business Process Automation
Motor de seguimiento de tareas con recordatorios idempotentes y almacenamiento SQLite. Demo con datos ficticios.

## Ejecutar
Python 3.11+ (sin dependencias externas).
```bash
python automation.py demo
python automation.py run
python -m unittest discover -v
```
La salida es JSON: simula notificaciones, no envía correos. Un registro único por tarea y etapa evita duplicados. El siguiente paso es integrar un proveedor de correo y un scheduler.
