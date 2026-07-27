"""York adapter-specific exceptions."""


class YorkProtocolError(RuntimeError):
    """Base exception for York protocol failures."""


class YorkProtocolNotReady(YorkProtocolError, NotImplementedError):
    """Raised when a protocol operation is intentionally not enabled yet."""


class YorkFrameError(YorkProtocolError):
    """Raised when a received frame is malformed or unsupported."""
