# simple_netmask

Validate that an IPv4 address and prefix length form a legal network, and
report which host bits are set.

```python
from simple_netmask import validate_network, find_host_bits, NetworkError

try:
    is_net = validate_network("10.0.0.5", 24)   # False (host bits set)
    host   = find_host_bits("10.0.0.5", 24)     # "0.0.0.5"
except NetworkError:
    pass  # malformed address or prefix out of range
```

## Why

The standard library `ipaddress` module is heavy and permissive — it happily
parses abbreviated octets and host/network combinations.  This library is the
strict alternative for a single job: confirm that an address and prefix form a
proper network (no host bits set), and extract the host bits when they don't.

The trade-off: `simple_netmask` only validates IPv4 and only accepts
fully-qualified dotted-quad addresses with exactly four octets.  Abbreviated
forms like `"10"` or `"10.1"` and leading-zero octets like `"010"` are rejected
outright, even though `socket.inet_aton` would accept them.  This catches
typos that POSIX permissiveness would hide.

## Awkward edge

The prefix length is a separate integer argument, not part of the address
string.  A combined CIDR string like `"10.0.0.0/24"` is **not** accepted — pass
`("10.0.0.0", 24)` as two arguments.  `True`/`False` are rejected as prefix
lengths even though they are technically `int` in Python, because a boolean
prefix is almost certainly a bug.

## Exports

- `validate_network(address: str, prefix_len: int) -> bool` — True if the
  combination is a legal, non-host network.
- `find_host_bits(address: str, prefix_len: int) -> str` — the host bits as a
  dotted-quad string (e.g. `"0.0.0.5"`), or `"0.0.0.0"` if none are set.
- `NetworkError` — subclass of `ValueError`, raised on malformed input.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

