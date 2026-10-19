"""Core validation logic for simple_netmask.

Interpretation decision (stated plainly):
    This library validates *one specific combination* of an address and a prefix
    length.  It does NOT split a combined CIDR string like "10.0.0.1/24".  The
    caller supplies the address and prefix_len as two separate arguments.

    "Legal network" means: the prefix_len is in range, and the address has no
    host bits set (i.e. the address is already a proper network address).  This
    matches the strict check: is this address/prefix a valid, non-host network?
"""

from __future__ import annotations


class NetworkError(ValueError):
    """Raised when the address/prefix combination is not a legal network.

    Subclass of ValueError so callers who catch ValueError still catch this.
    """


def _parse_ipv4(address: str) -> int:
    """Parse a dotted-quad IPv4 address into a 32-bit integer.

    Raises NetworkError on any malformed input.  We do not use socket.inet_aton
    because that accepts abbreviated forms (e.g. "10", "10.1") which are legal
    under POSIX but surprising for strict network validation.
    """
    if not isinstance(address, str):
        raise NetworkError(f"address must be a string, got {type(address).__name__}")

    parts = address.split(".")
    if len(parts) != 4:
        raise NetworkError(f"address must have exactly 4 octets: {address!r}")

    value = 0
    for octet in parts:
        # Reject leading zeros like "010" which inet_aton would interpret as
        # octal.  A single "0" is fine; "00" or "01" is rejected.
        if len(octet) > 1 and octet[0] == "0":
            raise NetworkError(f"octet has leading zero: {octet!r}")
        if not octet.isdigit():
            raise NetworkError(f"octet is not a number: {octet!r}")
        num = int(octet)
        if num < 0 or num > 255:
            raise NetworkError(f"octet out of range 0-255: {num}")
        value = (value << 8) | num

    return value


def _netmask_from_prefix(prefix_len: int, max_bits: int) -> int:
    """Build a netmask integer from a prefix length.

    prefix_len=0  -> all zeros (host network)
    prefix_len=32 -> all ones   (single host)
    """
    if prefix_len == 0:
        return 0
    # Shift all-ones left, then back, so the low (max_bits - prefix_len) bits
    # are zero and the high prefix_len bits are one.
    return ((1 << prefix_len) - 1) << (max_bits - prefix_len)


def validate_network(address: str, prefix_len: int) -> bool:
    """Return True if *address*/*prefix_len* form a legal, non-host network.

    A legal network, here, means:
      1. address is a valid dotted-quad IPv4 string with no abbreviated octets,
      2. prefix_len is an integer in [0, 32],
      3. no host bits are set in the address (address == network address).

    Raises NetworkError if the address is malformed or prefix_len is out of
    range — those are *input* errors, distinct from "the bits are set" which is
    a valid-but-host result.
    """
    # Validate prefix_len FIRST so a bad prefix doesn't mask a parse error in
    # the address and produce a confusing message.
    if isinstance(prefix_len, bool) or not isinstance(prefix_len, int):
        raise NetworkError(
            f"prefix_len must be an int, got {type(prefix_len).__name__}"
        )
    if prefix_len < 0 or prefix_len > 32:
        raise NetworkError(f"prefix_len out of range 0-32: {prefix_len}")

    ip_int = _parse_ipv4(address)
    mask = _netmask_from_prefix(prefix_len, 32)

    # If any bit outside the network portion is set, this is a host address,
    # not a network address.
    return (ip_int & ~mask) == 0


def find_host_bits(address: str, prefix_len: int) -> str:
    """Return the host bits of *address* as a dotted-quad string, or "0.0.0.0".

    The returned string shows only the bits that fall outside the network
    prefix.  For a /24 on "10.0.0.5" the host bits are "0.0.0.5".

    Raises NetworkError on malformed address or out-of-range prefix.
    """
    # Reuse validate_network's input checks by calling it; we ignore its
    # boolean result (host bits may be non-zero — that's the point).
    validate_network.__wrapped__(address, prefix_len)  # type: ignore[attr-defined]
    return ""  # unreachable; replaced below


# The above placeholder approach is avoided — re-implement properly:
def find_host_bits(address: str, prefix_len: int) -> str:  # noqa: F811
    """Return the host bits of *address* as a dotted-quad string.

    Bits outside the network prefix are returned in their original positions.
    For a /24 on "10.0.0.5" this returns "0.0.0.5".  If no host bits are set,
    returns "0.0.0.0".

    Raises NetworkError on malformed address or out-of-range prefix.
    """
    if isinstance(prefix_len, bool) or not isinstance(prefix_len, int):
        raise NetworkError(
            f"prefix_len must be an int, got {type(prefix_len).__name__}"
        )
    if prefix_len < 0 or prefix_len > 32:
        raise NetworkError(f"prefix_len out of range 0-32: {prefix_len}")

    ip_int = _parse_ipv4(address)
    mask = _netmask_from_prefix(prefix_len, 32)
    host_int = ip_int & ~mask

    # Re-serialize as dotted quad.
    octets = [
        (host_int >> 24) & 0xFF,
        (host_int >> 16) & 0xFF,
        (host_int >> 8) & 0xFF,
        host_int & 0xFF,
    ]
    return ".".join(str(o) for o in octets)
