FROM python:3.12-alpine

ARG BUILD_DATE="unknown"
ARG VCS_REF="local"
LABEL org.opencontainers.image.title="Climate Bridge" \
      org.opencontainers.image.description="Home Assistant MQTT bridge for York/TCL TFIAC type 20014 air conditioners" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.created="$BUILD_DATE" \
      org.opencontainers.image.revision="$VCS_REF"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY VERSION version.py bridge.py configuration.py mqtt_manager.py discovery_manager.py diagnostics_manager.py recovery_manager.py health_manager.py direct_read_manager.py direct_temperature_manager.py direct_power_manager.py direct_fan_manager.py direct_swing_manager.py ./
COPY transport ./transport
COPY adapters ./adapters
COPY protocols ./protocols
COPY validate_config.py republish_discovery.py healthcheck.py container_qualification.py qualification_suite.py york_decoder_qualification.py york_capture_importer.py york_protocol_lab.py york_packet_classifier.py york_request_hunter.py york_replay_engine.py york_one_shot_write_qualification.py york_heat_one_shot_write_qualification.py york_dynamic_temperature_qualification.py york_uncaptured_temperature_qualification.py york_power_one_shot_qualification.py york_mode_one_shot_qualification.py york_temperature_one_shot_qualification.py york_low_vertical_temperature_qualification.py york_low_vertical_temperature_range_qualification.py release_verifier.py ./

RUN mkdir -p /app/protocols/york/qualification-reports /app/protocols/york/dashboard

CMD ["sh", "-c", "mkdir -p /reports /config/york_protocol/captures /config/york_protocol/packet_library /config/york_protocol/reports /config/york_protocol/timelines /config/york_protocol/statistics /config/york_protocol/qualification-reports /config/york_protocol/dashboard && python /app/validate_config.py && exec python /app/bridge.py /config/config.yml"]
