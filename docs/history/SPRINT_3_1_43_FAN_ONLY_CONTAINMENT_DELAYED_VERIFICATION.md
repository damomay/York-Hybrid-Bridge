# Sprint 3.1.43 — Fan-only Containment and Delayed Verification

## Live evidence

Alpha.71 transmitted the historically labelled Fan-only frame from the live
Dry / 21 °C / Fan Auto / Swing Off state. The immediate read remained stale in
Dry, then the physical unit and authoritative state changed to Power Off about
22 seconds after the request. The frame is therefore unsafe for this unit and
must not be reused.

## Containment

- The historical Fan-only bytes remain only as rejected forensic evidence.
- The builder refuses to create a Fan-only candidate.
- The production Broadlink client refuses those bytes before opening a socket.
- Dry → Fan-only and Fan-only → Heat are absent from the active mode matrix.
- A Fan-only request creates no client and sends zero packets.
- Fan-only remains paused until a fresh labelled TFIAC command and its eventual
  authoritative state are captured.

## Delayed verification

The retained Auto → Cool, Cool → Dry and Heat → Auto edges keep one exact
control write with zero write retries. After the initial configured delay, the
client performs read-only state checks every five seconds through at least 30
seconds from the write. Verification stops as soon as all nine guarded fields
match. If no state matches, the final state produces a verification failure.

Any read showing Power Off when the target requires Power On raises an
immediate critical verification error and stops further polling.

## Qualification

- Focused containment and delayed-verification tests: 72 passed.
- Full regression suite: 804 passed.
- Retired Fan-only transport rejection is covered through the production
  client constructor.
- Late success, full-window timeout and critical Power Off paths are covered
  through authenticated production-client sessions.
