# LR-V1.0.0-001: Final acceptance summary

## Record control

| Field | Value |
| --- | --- |
| Legacy record ID | `LR-V1.0.0-001-final-acceptance-summary` |
| Record classification | `Legacy record — accepted historically` |
| Source | [`docs/history/V1_0_0_ACCEPTANCE_AND_STABILITY_EVIDENCE.md`](../../../history/V1_0_0_ACCEPTANCE_AND_STABILITY_EVIDENCE.md) |
| Cross-reference | [`docs/V1_0_0_RELEASE_AND_UPGRADE_GUIDE.md`](../../../V1_0_0_RELEASE_AND_UPGRADE_GUIDE.md) |
| Exact test date | `Not recorded` |
| Package identity and hash | `Not recorded` |
| Commit SHA | `Not recorded` |
| Configuration identity | `Not recorded` |
| Device alias | `Not recorded` |
| Operator | `Not recorded` |
| Reviewer | `Not recorded` |
| Raw-evidence reference | `Unavailable in repository evidence` |
| Evidence checksum | `Unavailable in repository evidence — not hashed` |
| Modern result validation | `Not retrospectively verified` |

## Migrated historical conclusion

The authoritative source records that Beta.1 completed this eight-step Home
Assistant acceptance sequence:

1. Fan High to Low.
2. 22.5 to 20.5 °C with Fan Low preserved.
3. Power Off.
4. Power On into Cool / 20.5 °C / Fan Low / Swing Off.
5. Cool to Heat with temperature, fan, and swing preserved.
6. Heat to Cool with temperature, fan, and swing preserved.
7. 20.5 to 22.5 °C with Fan Low preserved.
8. Fan Low to High.

The source records formal 9/9 verification for every command, four UDP sends
and zero retries, direct physical observation, stationary louvers, and no
warnings, errors, rejections, or unexpected state changes. It records later
authoritative reads as stable at Cool / 22.5 °C / Fan High / Swing Off.

The same source records no recurring MQTT disconnect or container-restart
pattern since early pre-Alpha.20 work; multiple Alpha.67 through Beta.1 releases
running overnight for 12–16 hours between tests without connection instability;
no unexplained loss of control or authoritative state reporting; and recent
operational issues attributed to deliberate safety boundaries or test
instructions rather than bridge connectivity.

Its historical conclusion is that V1.0.0 promoted the exact accepted Beta.1
runtime with release metadata and documentation changes only.

## Migration limitations

This Stage 2 record migrates only the final V1 acceptance summary. The source's
underlying raw evidence was not available, imported, hashed, or independently
reviewed during migration. Missing modern metadata remains explicitly missing;
no normal `TR` identity and no retrospective V1.0.0 qualification are created.
The original historical document remains the authority for its wording and
conclusion.
