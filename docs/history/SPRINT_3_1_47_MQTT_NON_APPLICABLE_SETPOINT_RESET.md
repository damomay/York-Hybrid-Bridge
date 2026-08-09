# Sprint 3.1.47 — MQTT Non-applicable Setpoint Reset

## Live defect

Alpha.75 correctly decoded Dry with no target temperature, but skipped the
MQTT target-temperature publication when the normalized value was `None`.
Home Assistant therefore retained the earlier Fan-only placeholder of 23 °C.
The activity formatter then attempted to render the `23 → None` transition as
a numeric temperature and raised `NoneType.__format__` on every poll.

## Alpha.76 correction

- Publish the literal retained payload `None` on the MQTT climate target-state
  topic whenever the authoritative mode is Dry or Fan-only. This is Home
  Assistant's documented setpoint-reset payload.
- Publish the reset on every non-applicable state, including the first poll
  after a bridge or broker restart, so an older retained Heat/Cool value cannot
  survive.
- Treat numeric-to-`None` as a semantic transition without passing `None` to a
  numeric formatter.
- Clear the retained target-temperature activity value when entering a
  non-setpoint mode.
- Restore the real numeric setpoint automatically on return to Heat or Cool.
- Continue publishing authoritative `indoorTemp` as current temperature.
- Keep target-temperature commands blocked in Dry and Fan-only.

## Safety boundary

The official-SDK Dry → Fan-only path remains unchanged: one control write,
zero retries, eight applicable verification fields, delayed read-only polling,
and immediate critical failure on unexpected Power Off. Fan-only exits and the
retired Alpha.71 frame remain disabled.
