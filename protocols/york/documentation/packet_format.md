# Packet format — working notes

## Known boundary

Captured device data frames begin with:

```text
BB
```

Climate Bridge currently validates this header only. It does not yet assume field offsets, length semantics, sequence values or checksum rules.

## Decoder policy

The York decoder must follow this order:

1. Validate frame presence and `0xBB` header.
2. Preserve the full raw frame.
3. Validate length and checksum only after those rules are proven from captures.
4. Decode fields only when mappings are backed by multiple labelled captures.
5. Return unknown values rather than guessing.

## Encoder policy

The encoder must never synthesize a packet from partially understood fields. During qualification it may replay only a complete verified request frame from the packet library.
