"""Configuration checking utitilites."""
import re
import typing
from enum import Enum

from ciscoconfparse import CiscoConfParse

from netlint.checks.constants import acl_regex


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
    :return: A list of configuration lines that use this ACL.
    """
    all_usages = []

    # Find all access lists used in packet filtering
    access_list_usage_in_filtering_regex = r"(ip)? access-(group|class)"
    if name:
        access_list_usage_in_filtering_regex += " " + name
    all_usages.extend(config.find_lines(access_list_usage_in_filtering_regex))
    access_list_usage_in_filtering_evaluate_regex = r"^\s+evaluate"
    if name:
        access_list_usage_in_filtering_evaluate_regex += " " + name
    all_usages.extend(
        config.find_children_w_parents(
            r"ip(v6)?\saccess-list\sextended",
            access_list_usage_in_filtering_evaluate_regex,
        )
    )

    # Find all access lists used in route-maps
    access_list_usage_in_route_map_regex = r"^\s+match ip \S+"
    if name:
        access_list_usage_in_route_map_regex += " " + name
    all_usages.extend(
        config.find_children_w_parents(
            r"^route-map", access_list_usage_in_route_map_regex
        )
    )

    # Find all access lists used in rate-limiting
    access_list_usage_in_rate_limiting_regex = r"^\s+rate-limit\soutput\saccess-group"
    if name:
        access_list_usage_in_rate_limiting_regex += " " + name
    all_usages.extend(
        config.find_children_w_parents(
            r"^interface", access_list_usage_in_rate_limiting_regex
        )
    )

    return all_usages


def get_access_list_definitions(config: CiscoConfParse) -> typing.List[str]:
    """Return all lines where access lists are defined."""
    # Definitions of extended ACLs
    extended_acls = config.find_lines(acl_regex)

    # Definitions of standard ACLs
    standard_acls = config.find_lines(r"^access-list")

    # Definition of reflexive ACLs
    reflected_definitions = config.find_children_w_parents(
        acl_regex, r"^.*reflect\s(\S+|\d+)"
    )
    return extended_acls + standard_acls + reflected_definitions


class NOS(Enum):
    """Overview of different available NOSes."""

    CISCO_IOS = "cisco_ios"
    CISCO_NXOS = "cisco_nxos"

    def __str__(self) -> str:
        """Overwrite __str__ to prettify the documentation."""
        return self.name

    @staticmethod
    def from_napalm(driver: str) -> "NOS":
        if driver == "ios":
            return NOS.CISCO_IOS
        elif driver == "nxos":
            return NOS.CISCO_NXOS
        else:
            raise ValueError(f"No NOS mapping found for NAPALM driver name {driver}.")


def detect_nos(configuration: typing.List[str]) -> NOS:
    """Automatically detect the NOS in the configuration.

    Very rudimentary as of now, will get more complex support for more NOSes is added.
    """
    for line in configuration:
        if "feature" in line:
            return NOS.CISCO_NXOS
    return NOS.CISCO_IOS


def get_name_from_acl_definition(acl: str) -> str:
    """Extract the ACL name from a ACL definition."""
    if "reflect" in acl:
        name = re.findall(r"^.*reflect\s(\S+)", acl)[0]
    elif acl.startswith("access-list"):
        _, name, _ = acl.split(maxsplit=2)
    else:
        _, _, _, name = acl.strip().split(" ", maxsplit=4)
    return name
