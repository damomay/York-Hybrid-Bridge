# Checksum research

Earlier controlled changes caused a corresponding checksum change, confirming that at least part of each frame is integrity-protected.

The checksum algorithm and byte coverage are not yet verified in this repository.

Before implementation, collect several full frames where only one known state field changes, then test candidate algorithms against every sample. A checksum rule is accepted only if it explains all verified samples without exceptions.
