# Sprint 3.1.53 — Auto/FEEL Program and Indoor-Temperature Correction

Capture 7 was synchronized on 2026-08-08 while the unit remained in its
latched Auto/FEEL cold-room program. Home Assistant showed 27 °C while the
official SDK reported `indoorTemp=25`; the same raw status contained room
bytes `0x70 0x08` and Auto's separate program value of 23 °C.

## Official room-temperature conversion

The SDK uses integer division after combining both status bytes:

```text
((raw[17] * 4) + ((raw[18] >> 2) & 0x03) - 195) / 10
```

The division is integer/truncating. The conversion reproduces the captured
14, 15, 16, 17 and 25 °C SDK values. Alpha.81's byte-17-only approximation is
removed.

## Auto/FEEL program model

The equipment manual and live observation establish that Auto/FEEL selects a
program when entered, then controls that program thermostatically rather than
continuously changing bands:

| Entry ambient | Latched internal operation | Program value |
| --- | --- | ---: |
| Below 20 °C | Heat | 23 °C |
| 20–26 °C | Dry | 18 °C |
| Above 26 °C | Cool | 23 °C |

The earlier live 21 °C Auto result remains accepted as physically observed
evidence, but it is not treated as a universal default. All other synthetic
Auto values fail verification.

## Capture 7 qualification edge

Capture 7's exact offline official-SDK Cool command is:

```text
BB 00 01 03 19 01 00 44 03 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 EE
```

Alpha.82 admits it only from Power On / Auto/FEEL / 23 °C / Fan Auto / both
swing axes Off / Display On with Turbo, Eco and Health Off. A fresh
authenticated nine-field pre-read must match exactly. The result must be Cool
23 °C with the same preserved fields. The transaction performs one control
write, zero automatic retries, no fallback and delayed read-only verification;
unexpected Power Off remains a critical failure.

Auto 18 °C is a recognized program outcome but its Cool exit remains blocked
because no byte-exact official-SDK write has been captured for that source.
