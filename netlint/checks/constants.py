"""Provide constants for checks across vendors.

These might come from standards, but they don't have to.
"""

bogus_as_numbers = [0, 23456, 4294967295]  # RFC6483, RFC7607  # RFC6793  # RFC7300
bogus_as_numbers += list(range(64496, 64511 + 1))  # RFC5398
bogus_as_numbers += list(range(65536, 65551 + 1))  # RFC4893, RFC5398

# Cisco password hash algorithms
bad_hash_algorithms = [0, 5, 7]
