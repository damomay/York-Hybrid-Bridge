# State mapping worksheet

| Climate Bridge field | Candidate packet location | Status | Evidence required |
|---|---|---|---|
| power | byte 7 bit or nibble | observed only | paired off/on full frames |
| target_temperature | byte 9 or related field | observed only | captures across integer and half-degree values |
| mode | unknown | unresolved | labelled auto/cool/dry/fan/heat captures |
| fan_mode | unknown | unresolved | labelled fan-speed captures |
| swing_mode | unknown | unresolved | swing off/on and position captures |
| current_temperature | unknown | unresolved | compare packet values against known room temperature |
| eco | unknown | unresolved | labelled eco toggle captures |
| turbo | unknown | unresolved | labelled turbo toggle captures |
| sleep | unknown | unresolved | labelled sleep toggle captures |

This table is intentionally conservative. Candidate locations are not executable mappings.
