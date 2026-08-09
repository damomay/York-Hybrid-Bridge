# Sprint 3.1.54 — Official-SDK Cool 23 °C to 21 °C Fan Auto Qualification

Alpha.82 correctly stopped the grouped acceptance temperature request because
the live source used Fan Auto, while every earlier qualified temperature path
required Low fan or one of the captured Heat/Vertical shapes.

York Write Packet Lab Capture 8 read the exact source as Power On / native Cool
mode 3 / `temp=8` (23 °C) / `wind=0` (Fan Auto) / both swing axes Off / Display
On, with Turbo, Eco and Health Off. No generated packet was transmitted.

## Exact target frame

The official parser's generated whole-degree sequence establishes 20 °C as
`temp=11`, 22 °C as `temp=9`, and therefore 21 °C as `temp=10` (`0x0A`). The
isolated checksum-clean target frame is:

```text
BB 00 01 03 19 01 00 44 03 0A 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 EC
```

This changes only the target temperature. Fan Auto, both swing axes Off,
Display On and every optional field are preserved.

## Safety boundary

Alpha.83 authorizes only Cool 23 °C → Cool 21 °C from the exact nine-field
Capture 8 source. The authoritative state and a fresh authenticated device
pre-read must both match before the frame can enter the encrypted transport.
Every other Fan Auto source or target remains blocked before client creation.

The transaction uses one control write, zero automatic retries and no fallback.
Result verification compares all nine fields and may poll read-only for up to
30 seconds. Any unexpected Power Off is an immediate critical failure.
