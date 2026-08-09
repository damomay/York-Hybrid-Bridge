# Sprint 3.1.40 — Auto/FEEL Dynamic Ambient Mode Matrix

Alpha.69 corrects the remaining Auto/FEEL assumption exposed during the
Alpha.68 physical test. The authoritative Auto status changed from 22 °C to
23 °C when the room temperature changed, while remote comfort adjustments did
not change that field. The decoded Auto temperature is therefore treated as a
dynamic ambient/status value, not a user target.

## Guarded behaviour

- Auto → Cool accepts a freshly decoded Auto temperature from 16.0 through
  31.5 °C in 0.5 °C increments.
- Heat → Auto accepts the same bounded dynamic temperature in its verification
  read.
- Power, mode, fan, swing, turbo, eco, health and display remain exact on both
  Auto endpoints.
- Cool, Dry, Fan-only and Heat temperatures remain exact.
- The canonical captured Auto command remains unchanged at its 22 °C command
  encoding; this correction changes status validation only.
- Auto temperature commands remain unsupported.

Each ordered edge still requires a fresh direct pre-read, one write, a delayed
direct post-read, four UDP sends, zero retries and no fallback. Invalid Auto
temperatures, altered non-temperature fields, skipped edges and non-Auto
temperature mismatches stop before transmission wherever possible.

## Physical acceptance sequence

1. Auto/FEEL → Cool
2. Cool → Dry
3. Dry → Fan-only
4. Fan-only → Heat
5. Heat → Auto/FEEL

The expected non-Auto targets are unchanged from Alpha.68. The initial and
final Auto temperatures must agree with the live room-dependent value shown by
the authoritative read; they are not required to equal 22 °C.
