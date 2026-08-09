# Sprint 3.2.0 — Capability Audit and Beta Scope

Beta.1 freezes the first York unit's physically qualified native boundary. It
does not add new packet encodings or widen any transport allowlist.

## Home Assistant controls retained

- Power On/Off where the complete current state matches a qualified shape.
- Cool and Heat mode changes across qualified canonical shapes.
- Dry, Fan Only and Auto/FEEL only through the exact official-SDK mode-loop
  source states already qualified in Alpha.75–85.
- Cool target temperature 16.0–31.0 °C in 0.5 °C steps while Swing is Off and
  Fan is Auto, Low or High.
- Previously qualified Heat temperature shapes.
- Fan Low/High changes through the guarded allowlist. Auto is reported and
  preserved, but changing to Auto from Home Assistant is not qualified.
- Swing modes through their existing guarded Heat/Dry source shapes.

## Controls removed from discovery

- Fan Medium.
- Turbo, Eco, Health, Display and Sleep switches.

Those fields remain decoded and verified so an unrelated physical change still
stops a transaction. Removing their command controls does not weaken the
nine-field safety boundary.

## Explicitly outside beta scope

- General Auto/FEEL setpoint writes.
- General Dry or Fan Only setpoint writes.
- Fan Auto selection from Low or High.
- Arbitrary swing changes outside their qualified Heat/Dry shapes.
- Timer and other OEM-only features.
- A second York unit or non-York adapters.

## Safety invariants retained

- Fresh authenticated source read before every command.
- Exact source-shape selection and canonical target frames.
- One write, four UDP sends, zero automatic retries and no fallback.
- Immediate and delayed verification.
- Critical stop on unexpected Power Off.
- Unqualified commands rejected before transmission.
