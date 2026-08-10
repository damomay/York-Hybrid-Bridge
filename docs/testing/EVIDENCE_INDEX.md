# Sanitized evidence index

Raw evidence remains in an approved private location. Git contains only
sanitized metadata sufficient to identify, relate, and integrity-check an item
without exposing where private material is stored. An opaque private-store
reference identifies the item to its custodian without containing a local path,
share link, credential, network identifier, or other location secret.

Do not claim a hash is verified unless the corresponding original was actually
available and hashed. Use `Not available — not hashed` when it was not.

## Sensitivity classifications

- `Public` — approved for public repository disclosure.
- `Sanitized` — sensitive details were removed and the remainder is approved.
- `Sensitive` — access-controlled operational or device evidence.
- `Restricted` — highest-control evidence, including material whose disclosure
  could enable access, control, or identification.

## Index

| Evidence ID | Related plan/result/qualification | Evidence type | Capture date and timezone | Device alias | Sensitivity classification | Opaque private-store reference | SHA-256 | Custodian | Availability or retention status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _No Stage 2 evidence indexed_ | — | — | — | — | — | — | — | — | — | Historical raw evidence was not imported or hashed during Stage 2. |

Never add private IP or MAC addresses, device keys, credentials, tokens, raw
packets containing sensitive identifiers, private-storage paths, exposing share
links, or unsanitized logs, screenshots, PCAPs, APKs, ZIPs, or generated
packages to this index or repository.
