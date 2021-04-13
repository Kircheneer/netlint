"""Configuration checking utitilites."""
import re
import typing

from ciscoconfparse import CiscoConfParse


def get_password_hash_algorithm(config_line: str) -> typing.Optional[int]:
    """Extract the number of the password hash algorithm from a config line.

    :param config_line: The configuration line that potentially contains the number.
    :return: If present, the integer identifying the algorithm.
    """
    match = re.match(r"^.*(password|secret)\s\d\s\S+$", config_line)
    if not match:
        return None
    integer = re.search(r"\s\d\s", match[0], flags=re.MULTILINE)
    if not integer:
        return None
    else:
        # Guaranteed to be a string containing a single digit because of
        # 1) the re.match
        # 2) the fact that bool(match) == True
        return int(integer[0])


def get_access_list_usage(
    config: CiscoConfParse, name: typing.Optional[str] = None
) -> typing.List[str]:
    """Return lines that use access lists.

    :param config: The config to filter in.
    :param name: Optionally filter for a specific ACL name.
    """
    access_list_usage = "(ip)? access-(group|class)"
    if name:
        access_list_usage += " " + name
    return config.find_lines(access_list_usage)


def get_access_list_definitions(config: CiscoConfParse) -> typing.List[str]:
    """Return all lines where access lists are defined."""
    return config.find_lines(r"^ip(v6)?\saccess-list\s(standard|extended)")
