FROM python:3.12-alpine

LABEL org.opencontainers.image.title="Climate Bridge"
LABEL org.opencontainers.image.description="Vendor-adapter bridge between proprietary HVAC systems and Home Assistant"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY VERSION version.py bridge.py configuration.py relay_manager.py mqtt_manager.py discovery_manager.py diagnostics_manager.py recovery_manager.py health_manager.py ./
COPY validate_config.py republish_discovery.py healthcheck.py container_qualification.py ./
COPY adapters ./adapters
COPY protocols ./protocols
COPY transport ./transport
COPY qualification_suite.py york_capture_importer.py york_decoder_qualification.py york_packet_classifier.py york_protocol_lab.py ./
COPY york_capture_probe.py york_replay_engine.py york_request_hunter.py york_relay_extraction_report.py ./
COPY york_native_capture_importer.py ./

RUN mkdir -p /reports

CMD ["sh", "-c", "python /app/validate_config.py && exec python /app/bridge.py /config/config.yml"]
