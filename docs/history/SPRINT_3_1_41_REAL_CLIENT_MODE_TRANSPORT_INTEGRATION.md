# Sprint 3.1.41 — Real-Client Mode Transport Integration

Alpha.69 safely stopped the first Auto-to-Cool command because the validated
remaining-mode candidate was not accepted by the production Broadlink client
constructor. Alpha.70 closes that integration gap without widening any older
allowlist.

The five candidates remain in `QUALIFIED_REMAINING_MODE_COMMANDS`, separate
from immutable captures and general parameterised power frames. The production
client accepts only exact members of that set and checks the same boundary
again while constructing the encrypted write packet.

The live sequence remains Auto → Cool → Dry → Fan-only → Heat → Auto.
Every edge requires an authenticated fresh pre-read, one exact write, a delayed
post-read, nine-field verification, four UDP sends, zero retries and no
fallback. Auto/FEEL temperature remains a bounded dynamic ambient field.
