# Sprint 3.1.25 — Native Heat Horizontal Axis Control

Alpha.54 promotes the two Alpha.53 transitions physically qualified at
On / Heat / 21.5 °C / Fan Low into normal guarded Home Assistant control:

- Swing Off → Horizontal
- Swing Horizontal → Off

The native path uses the exact Relay v2 frames qualified in Alpha.53. Each
eligible request requires matching nine-field Relay state and live direct
pre-read, performs one write through four UDP sends with zero retries, and
requires a matching nine-field post-read.

Every other Horizontal or Both request safely retains Relay v2 fallback. The
existing parameterised Heat Off ↔ Vertical path and Dry / 21 °C / Fan Low
Vertical ↔ Both path are unchanged. Alpha.53's one-shot qualification tool is
removed from the executable container.
