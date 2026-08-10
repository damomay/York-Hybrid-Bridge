# Climate Bridge v1.0.0 Acceptance and Stability Evidence

> Stage 2 navigation: the sanitized legacy migration of this final summary is
> [`LR-V1.0.0-001-final-acceptance-summary`](../testing/results/legacy/LR-V1.0.0-001-final-acceptance-summary.md).
> This forward link does not alter the historical wording or conclusion below.

## Functional acceptance

Beta.1 completed the final eight-step Home Assistant acceptance sequence:

1. Fan High to Low.
2. 22.5 to 20.5 °C with Fan Low preserved.
3. Power Off.
4. Power On into Cool / 20.5 °C / Fan Low / Swing Off.
5. Cool to Heat with temperature, fan and swing preserved.
6. Heat to Cool with temperature, fan and swing preserved.
7. 20.5 to 22.5 °C with Fan Low preserved.
8. Fan Low to High.

Every command completed formal 9/9 verification with four UDP sends and zero
retries. The unit behaved correctly under direct physical observation, both
louvers remained stationary, and no warning, error, rejection or unexpected
state change occurred. Later authoritative reads remained stable at Cool /
22.5 °C / Fan High / Swing Off.

## Connection stability

- No recurring MQTT disconnect or container-restart pattern has been observed
  since the early pre-Alpha.20 connection work.
- Multiple releases from Alpha.67 through Beta.1 ran overnight for 12–16 hours
  between tests without connection instability.
- No unexplained loss of control or authoritative state reporting occurred.
- Recent operational issues were traced to deliberate safety boundaries or
  test instructions rather than bridge connectivity.

This cumulative evidence closes the first York unit's functional-acceptance and
stability milestones. v1.0.0 promotes the exact accepted Beta.1 runtime with
release metadata and documentation changes only.
