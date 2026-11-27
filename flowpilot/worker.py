import os
import time
import logging
from .database import initialize
from .engine import enqueue, dispatch, utcnow
from .adapters import LocalNotificationAdapter

def main():
    path = os.getenv("FLOWPILOT_DB","flowpilot.db")
    adapter = LocalNotificationAdapter(os.getenv("FLOWPILOT_NOTIFICATIONS","notifications.db"))
    interval = max(5,int(os.getenv("FLOWPILOT_INTERVAL","60")))
    logging.basicConfig(level=logging.INFO)
    initialize(path)
    while True:
        try:
            now = utcnow()
            count = enqueue(path,now)
            logging.info("eventos_generados=%s resultados=%s",count,dispatch(path,adapter,now))
        except Exception:
            logging.exception("Error durante el ciclo de procesamiento")
        time.sleep(interval)

if __name__ == "__main__":
    main()
