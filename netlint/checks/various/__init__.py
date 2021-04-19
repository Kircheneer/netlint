"""Checks that apply to more than one NOS."""
import re
import typing

from ciscoconfparse import CiscoConfParse

from netlint.checks.checker import CheckResult, Checker

from netlint.checks.utils import (
    get_access_list_usage,
    get_access_list_definitions,
    NOS,
    get_name_from_acl_definition,
    Tag,
)

__all__ = [
    "check_default_snmp_communities",
    "check_unused_access_lists",
    "check_used_but_unconfigured_access_lists",
]


@Checker.register(
    apply_to=[NOS.CISCO_IOS, NOS.CISCO_NXOS], name="VAR101", tags=[Tag.SECURITY]
)
def check_default_snmp_communities(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check for presence of default SNMP community strings."""
    parsed_config = CiscoConfParse(config)
    snmp_communities = parsed_config.find_lines("^snmp-server community")
    for community in snmp_communities:
        if community.startswith("snmp-server community public") or community.startswith(
            "snmp-server community private"
        ):
            return CheckResult(
                text="Default SNMP communities present.", lines=snmp_communities
            )

    return None


@Checker.register(
    apply_to=[NOS.CISCO_IOS, NOS.CISCO_NXOS], name="VAR102", tags=[Tag.HYGIENE]
)
def check_unused_access_lists(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check for any ACLs that are configured but never used.

    Potential usages are:

    * Packet filtering
    * Rate limiting
    * Route maps
    """
    parsed_config = CiscoConfParse(config)
    access_lists = get_access_list_definitions(parsed_config)
    unused_acls = []
    for acl in access_lists:
        name = get_name_from_acl_definition(acl)
        usages = get_access_list_usage(parsed_config, name=name)
        if not usages:
            unused_acls.append(acl)
    if unused_acls:
        return CheckResult(text="Unused ACLs configured", lines=unused_acls)
    else:
        return None


@Checker.register(
    apply_to=[NOS.CISCO_IOS, NOS.CISCO_NXOS],
    name="VAR103",
    tags=[Tag.HYGIENE, Tag.SECURITY],
)
def check_used_but_unconfigured_access_lists(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check for any ACLs that are used but never configured.

    Potential usages are:

    * Packet filtering
    * Rate limiting
    * Route maps
    """
    parsed_config = CiscoConfParse(config)
    access_list_usages = get_access_list_usage(parsed_config)
    access_list_definitions = get_access_list_definitions(parsed_config)
    defined_access_lists = []
    undefined_but_used_access_lists = []
    for definition in access_list_definitions:
        name = get_name_from_acl_definition(definition)
        defined_access_lists.append(name)
    for usage in access_list_usages:
        # Get acl name/number from the configuration line for packet filtering usages
        # Standard use
        acl_in_filtering = re.findall(r"access-(class|group)\s(\S+|\d+)", usage)
        if acl_in_filtering and acl_in_filtering[0][1] not in defined_access_lists:
            undefined_but_used_access_lists.append(usage)
        # Evaluated in other ACLs
        acl_evaluated = re.findall(r"^\s+evaluate\s(\S+|\d+)", usage)
        if acl_evaluated and acl_evaluated[0] not in defined_access_lists:
            undefined_but_used_access_lists.append(usage)

        # Get acl name/number from the configuration line for route-map usages
        acl_in_route_map = re.findall(r"\s+match\sip\s\S+\s(\S+|\d+)", usage)
        if acl_in_route_map and acl_in_route_map[0][1] not in defined_access_lists:
            undefined_but_used_access_lists.append(usage)
    if undefined_but_used_access_lists:
        return CheckResult(
            text="Access lists used but never defined.",
            lines=undefined_but_used_access_lists,
        )
    else:
        return None
