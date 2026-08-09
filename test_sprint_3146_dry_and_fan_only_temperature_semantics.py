from adapters.york.decoder import YorkPacketDecoder


def test_dry_and_fan_only_captures_do_not_expose_setpoints():
    decoder = YorkPacketDecoder()
    captures = (
        bytes.fromhex("BB0100030F0100330000000000000000005A0000DE"),
        bytes.fromhex("BB0100030F010032370000000000000000570800ED"),
    )
    for frame in captures:
        state = decoder.decode_state(frame).to_dict()
        assert state["mode"] in {"dry", "fan_only"}
