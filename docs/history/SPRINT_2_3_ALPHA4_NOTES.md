# Sprint 2.3 — alpha.4 health and terminology baseline

This release replaces the York Hybrid Bridge-era relay health check with a Climate Bridge core health check.

Docker health requires:

1. the Climate Bridge Python process to be running as PID 1;
2. the bridge to have completed MQTT initialization and created its READY marker; and
3. the main polling loop heartbeat to be no more than 120 seconds old.

Transport failure remains visible through Home Assistant diagnostics and device availability, but a temporary relay failure no longer causes Synology to describe the whole container as `Unhealthy: relay`.
