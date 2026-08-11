# Test Plan: `<short description>`

> Complete every required field before changing status to **Ready**. Preserve approved earlier revisions when procedure or acceptance boundaries change.

## Record control

| Field | Value |
| --- | --- |
| Test-plan ID | `<TP-AREA-NNN-short-description>` |
| Plan revision | `<revision>` |
| Repository revision | `<full commit SHA containing this plan>` |
| Status | `Planned` |
| Review route | `<Independent / Sole-maintainer exception>` |
| Plan owner / readiness approver | `<names or pending>` |
| Development / test planning / readiness approval / physical operation / evidence collection / result assessment / qualification assessment / publication approval roles | `<name or pending for each applicable role>` |
| Role-overlap disclosure | `<shared roles or none>` |
| Prepared / separate readiness-decision date | `<date + timezone / pending>` |
| Evidence reviewed for readiness | `<references>` |
| Known limitations / reduced-assurance statement | `<values; reduced assurance required for exception>` |
| Related issue/PR | `<reference or none>` |
| Supersedes | `<ID/revision or none>` |

Independent readiness review is preferred. A plan may also be marked `Ready`
through an expressly selected, separate and dated **Sole-maintainer readiness
approval**. The exception is never inferred from authorship: writing the plan
does not make it ready. It must disclose role overlap and reduced assurance and
must not be called independent review, independent validation, independently
verified, or independently qualified. Readiness does not validate results or
authorize runtime changes, release activity, or wider commands.

## Purpose, scope, and acceptance basis

Purpose: `<single behaviour or boundary>`

Included: `<scope>`

Excluded: `<nearby unsupported scope>`

| Repository reference | Evidence type | Supported claim |
| --- | --- | --- |
| `<path/issue/result>` | `<physical/protocol/code/decision>` | `<claim>` |

Uncertainties: `<not yet proven>`

## Exact test article

| Field | Required value |
| --- | --- |
| Repository | `damomay/York-Hybrid-Bridge` |
| Full commit SHA | `<40-character SHA>` |
| Reported version / branch or tag | `<version / reference>` |
| Package filename or image reference | `<identity>` |
| SHA-256 or immutable image digest | `<digest>` |
| Configuration profile | `<sanitized profile/revision>` |
| Device alias | `<non-sensitive alias>` |
| Home Assistant version | `<version or N/A>` |
| Bridge/container environment | `<version summary>` |

Do not record private IP or MAC addresses, device keys, credentials, tokens, or
raw packet secrets.

## Preconditions

- [ ] Exact test article is deployed and automated prerequisites are recorded.
- [ ] Operator can directly observe the physical unit.
- [ ] Required evidence collectors are ready before Step 1.
- [ ] Conflicting controllers/automations are inactive.
- [ ] Safe recovery is available and the test window is safe.

## Required starting state

| Field | Required physical state | Required reported state |
| --- | --- | --- |
| Power / mode / target temperature | `<state>` | `<state>` |
| Fan / vertical swing / horizontal swing | `<state>` | `<state>` |
| Turbo / Eco / Health / Display | `<state>` | `<state>` |
| Indoor temperature / other | `<observed or N/A>` | `<reported or N/A>` |

## Safety and command boundary

| Control | Requirement |
| --- | --- |
| Permitted command sources and targets | `<exact states>` |
| Required pre-read | `<fields/authentication/freshness>` |
| Writes / UDP sends / automatic retries per step | `<counts; retries normally zero>` |
| Fallback and delayed verification | `<none or exact behaviour/timing>` |
| Recovery | `<manual safe recovery; never assume automatic restore>` |

This plan does not authorize a new packet, transition, allowlist entry, retry,
or fallback unless separately reviewed and explicitly approved.

## Stop conditions

Stop immediately and preserve all evidence for any starting-state mismatch,
unavailable entity, failed pre-read, guard rejection, unexpected command/send/
retry count, power or state change, louver movement, reported/physical
disagreement, verification timeout, capture failure, missing required evidence,
or operator safety concern. Do not improvise more commands. Submit the actual
attempt for reviewer selection of `Failed` or `Inconclusive` and revise the plan
before retesting.

## Ordered procedure

| Step | Operator action | Expected physical result | Expected reported/protocol result | Evidence | Minimum wait/poll rule |
| ---: | --- | --- | --- | --- | --- |
| 0 | Confirm starting state | `<expected>` | `<expected>` | `<IDs>` | `<rule>` |
| 1 | `<exact action>` | `<expected>` | `<expected>` | `<IDs>` | `<rule>` |

## Evidence and automated prerequisites

| Evidence item | Required? | Sensitivity | Window | Repository reference |
| --- | --- | --- | --- | --- |
| Logs / HA history / physical media / PCAP / test output | `<yes/no>` | `<class>` | `<window>` | `<opaque ID + SHA-256>` |

Raw evidence belongs in the approved private location. Automated checks prove
software properties and cannot replace physical observation.

| Check | Command/workflow | Required result |
| --- | --- | --- |
| `<check>` | `<command>` | `<pass condition>` |

## Acceptance and result handling

- [ ] Exact starting state and article were confirmed.
- [ ] Every completed step matched physical and reported expectations.
- [ ] Send/retry counts matched; no stop condition occurred.
- [ ] Required evidence was captured, checksummed, and deviations recorded.

Create a new result for every passing, failed, stopped, incomplete, or
inconclusive attempt. Never overwrite an earlier run with a later pass. The
operator records observations. Only the later independent validation or
separate sole-maintainer result assessment assigns the accepted outcome.

## Separate readiness assessment

Confirm the exact candidate identity and scope, objectives and acceptance
criteria, prerequisites and starting state, safe operating boundaries, evidence
to capture, stop conditions, restoration or rollback, known limitations, role
overlap, and reduced assurance where applicable.

| Route (select exactly one) | Selected |
| --- | --- |
| Independent (preferred) | `[ ]` |
| Sole-maintainer exception | `[ ]` |

| Decision | Accountable person | Decision date | Evidence reviewed | Limitations / reduced assurance | Rationale |
| --- | --- | --- | --- | --- | --- |
| `<Ready / changes required / rejected>` | `<name>` | `<date + timezone>` | `<references>` | `<values>` | `<rationale>` |
