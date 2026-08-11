# Test Result: `<short description>`

> Create one record per attempt and preserve failed, stopped, incomplete, and inconclusive attempts.

## Record control

| Field | Value |
| --- | --- |
| Test-run ID | `<TR-YYYYMMDD-AREA-NNN-shortsha-Rn>` |
| Test-plan ID/revision/commit | `<exact reference>` |
| Record state / review outcome | `Awaiting review` / `Pending review` |
| Operator / run date-time | `<name / timestamp + timezone>` |
| Assessment route | `<Independent / Sole-maintainer exception>` |
| Accountable result assessor / decision date | `<name or pending / timestamp + timezone or pending>` |
| Development / test planning / readiness approval / physical operation / evidence collection / result assessment / qualification assessment / publication approval roles | `<name or pending for each applicable role>` |
| Role-overlap disclosure | `<shared roles or none>` |
| Evidence reviewed in assessment | `<references or pending>` |
| Known limitations / reduced-assurance statement | `<values; reduced assurance required for exception>` |
| Related issue/PR | `<reference or none>` |
| Retest of / followed by | `<run ID or none>` |

The operator's completion or submission must not select `Validated`, `Failed`,
or `Inconclusive`. A later preferred independent validation or an expressly
selected, separate and dated **Sole-maintainer result assessment** selects the
outcome. The exception must disclose role overlap and reduced assurance and
must not be called independent review, independent validation, independently
verified, or independently qualified. Retest relationships never replace the
facts of this run.

## Tested article

| Repository | Full commit SHA | Version / branch/tag | Package/image + SHA-256 | Configuration | Device alias | HA / environment |
| --- | --- | --- | --- | --- | --- | --- |
| `damomay/York-Hybrid-Bridge` | `<40-char SHA>` | `<values>` | `<identity + digest>` | `<sanitized revision>` | `<alias>` | `<versions>` |

Any identity difference from the approved plan is a stop requiring review.

## Pre-run checks and observed starting state

| Check | Result | Evidence | Notes |
| --- | --- | --- | --- |
| Article, prerequisites, capture, control isolation, recovery | `<pass/fail/not run>` | `<reference>` | `<notes>` |

| Field | Required | Physical observation | Authoritative reported state | Match? |
| --- | --- | --- | --- | --- |
| Power / mode / temperature / fan | `<state>` | `<observation>` | `<state>` | `<yes/no>` |
| Vertical/horizontal swing and protected features | `<state>` | `<observation>` | `<state>` | `<yes/no>` |
| Indoor temperature / other | `<state or N/A>` | `<observation>` | `<state or N/A>` | `<yes/no/N/A>` |

## Execution record

Record only actions actually performed; never mark skipped work as passed.

| Step | Timestamp | Action | Physical observation | Reported/protocol result | Writes / sends / retries | Evidence IDs | Result |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 0 | `<time>` | Starting state | `<actual>` | `<actual>` | `0 / 0 / 0` | `<IDs>` | `<result>` |
| 1 | `<time>` | `<actual action>` | `<actual>` | `<actual>` | `<n / n / n>` | `<IDs>` | `<pass/fail/stopped/inconclusive>` |

## Deviations and stop decision

| Step/time | Actual observation | Expected | Stop triggered? | Action taken |
| --- | --- | --- | --- | --- |
| `<value or none>` | `<actual>` | `<expected>` | `<yes/no>` | `<stopped and preserved evidence/etc.>` |

Never omit a mismatch because a later step or retest succeeded.

## Evidence manifest

| Evidence ID | Description | Original filename | SHA-256 | Sensitivity | Opaque private-store reference | Reviewed? |
| --- | --- | --- | --- | --- | --- | --- |
| `<ID>` | `<description>` | `<filename>` | `<64-hex digest>` | `<class>` | `<opaque reference>` | `<yes/no>` |

Exclude credentials, network identifiers, device keys, and unsanitized packet
content. Do not claim a hash match without access to the original.

## Automated results

| Check | Commit | Result | Reference | What it proves |
| --- | --- | --- | --- | --- |
| `<check>` | `<full SHA>` | `<result>` | `<reference>` | `<software property>` |

Automated results are not physical validation.

## Operator submission

Summary: `<what occurred, including stopped steps and missing evidence>`

- [ ] Exact article, starting state, and every performed command are recorded.
- [ ] Stop conditions were obeyed; failures and missing evidence are preserved.
- [ ] Evidence references/checksums are complete to the operator's knowledge.
- [ ] No sensitive raw material was copied into Git.

Submitted by/date: `<operator / date>`

## Separate result assessment and outcome

Assess exact plan revision/article, starting state, physical/reported agreement,
guardrails and counts, evidence completeness/hash match, deviations, precisely
supported scope, and explicit unsupported scope. Verify recorded steps against
the approved acceptance criteria, distinguish observations from interpretations,
and identify missing, ambiguous, contradictory, or safety-relevant evidence,
failures, and incomplete steps. Preserve raw-evidence provenance without
upgrading historical evidence. Do not weaken criteria or treat missing evidence
as a pass.

| Route (select exactly one) | Selected |
| --- | --- |
| Independent (preferred) | `[ ]` |
| Sole-maintainer exception | `[ ]` |

Select exactly one:

- [ ] **Validated** — complete evidence supports the criteria for this exact article and scope.
- [ ] **Failed** — required behaviour or a safety boundary was not met.
- [ ] **Inconclusive** — evidence or identity is incomplete, ambiguous, or contradictory.

Accountable assessor / decision date / evidence reviewed / limitations and
reduced assurance / rationale: `<required values>`

Validation applies only to the recorded article, plan revision, steps, and
scope. It does not authorize release, deployment, new packets, or wider command
boundaries.

| Follow-up | Decision/reference |
| --- | --- |
| Issue / retest relationship | `<reference or none>` |
| Command boundary | `<no, or separate approval>` |
| Qualification impact | `<candidate/requirement or none>` |
| Next permitted action | `<action>` |
