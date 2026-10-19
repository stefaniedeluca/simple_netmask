"""simple_netmask: validate that an address and prefix length form a legal network.

Public API:
    - validate_network(address, prefix_len)
    - find_host_bits(address, prefix_len)
    - NetworkError (exception raised on invalid input)
"""

from simple_netmask.core import NetworkError, find_host_bits, validate_network

__all__ = ["NetworkError", "find_host_bits", "validate_network"]
