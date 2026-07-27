# Capture import area

Place original York Protocol Explorer logs and normalized request/response captures here.

Recommended names:

```text
YYYYMMDD_device_action_sequence.txt
YYYYMMDD_state_poll_request.bin
YYYYMMDD_state_poll_response.bin
```

For each capture, also add a JSON metadata record containing:

- timestamp and timezone;
- device model/type;
- direction (`controller_to_device` or `device_to_controller`);
- action or known HVAC state;
- full frame hex;
- source tool/log filename;
- redactions performed;
- verification status.

Do not include passwords, cloud tokens, IMEI values, serial numbers or private MQTT credentials.
