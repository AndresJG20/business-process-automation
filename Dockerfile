FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY flowpilot ./flowpilot
RUN mkdir /data && chown 10001:10001 /data
USER 10001:10001
ENV FLOWPILOT_DB=/data/flowpilot.db FLOWPILOT_NOTIFICATIONS=/data/notifications.db
CMD ["uvicorn","flowpilot.api:app","--host","0.0.0.0","--port","8000"]
