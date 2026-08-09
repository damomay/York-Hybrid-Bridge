# Sprint 3.1.7 — Guarded Power Off from Heat Control

Alpha.36 integrates the physically qualified `off-heat` command into normal
Home Assistant MQTT control.

## Qualified transition

- Before: On / Heat / 25 °C / Fan High / Swing Vertical
- Result: Off / Heat / 25 °C / Fan High / Swing Vertical
- Exact frame: 31 bytes
- Source: Relay v2 transaction #7 on 2026-07-30
- Live qualification: Alpha.35, `MATCH (9/9)`

## Safety boundary

- `direct_control.power_enabled` remains an explicit opt-in.
- The Relay state selects between the distinct Cool-off and Heat-off fixtures.
- The direct pre-read must match the selected nine-field starting state.
- Each eligible request performs one write and zero automatic retries.
- The direct post-read must match all nine expected fields.
- Any unqualified state or direct failure falls back to Relay v2 when enabled.
- No native Heat/Cool mode-change support is added in this sprint.
