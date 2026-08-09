# Sprint 3.1.34 — Fan High / Swing Off Qualification

Alpha.63 introduces one narrowly guarded qualification at the physically
verified handoff state: On / Heat / 22.5 °C / Fan Low / Swing Off.

## Evidence boundary

- The canonical Heat / 22.5 °C / Low / Off frame is already physically proven.
- The qualified Vertical fan transition changes command byte 10 from `0x3A`
  (Low) to `0x3D` (High), an isolated delta of `0x03`.
- Applying only that fan delta to the proven Low/Off byte `0x02` produces the
  Alpha.63 High/Off candidate byte `0x05`.
- Mode, temperature, half-degree flag, swing, feature flags and checksum shape
  remain unchanged.

This is a candidate combination, not a promoted general encoding. It is kept
outside the immutable captured replay allowlist and validated by a separate
case-specific client.

## Runtime boundary

- Exact source: On / Heat / 22.5 °C / Low / Off / features disabled.
- Exact target: On / Heat / 22.5 °C / High / Off / features disabled.
- The exact Low return frame is available only from the matching High/Off state.
- A fresh authenticated nine-field pre-read must match before the write.
- One write uses four UDP sends and zero retries.
- A delayed nine-field post-read reports whether Fan High and Swing Off were
  physically accepted.
- Every nearby mode, setpoint, swing, fan or feature state remains a zero-write
  safe-stop.

## Physical acceptance

Deploy Alpha.63 at Heat / 22.5 °C / Fan Low / Swing Off. Request Fan High once
through Home Assistant. Confirm the physical airflow increases while the
setpoint and both louvre axes remain unchanged. Do not repeat automatically if
verification fails.
