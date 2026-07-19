FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bridge.py configuration.py relay_manager.py mqtt_manager.py discovery_manager.py diagnostics_manager.py recovery_manager.py health_manager.py ./
COPY validate_config.py republish_discovery.py healthcheck.py ./

CMD ["sh", "-c", "python /app/validate_config.py && exec python /app/bridge.py /config/config.yml"]
