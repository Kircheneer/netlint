"""Checks that apply to more than one NOS."""

import typing

from ciscoconfparse import CiscoConfParse

from netlint.checks.checker import CheckResult, Checker

__all__ = ["check_default_snmp_communities", "check_unused_access_lists"]

from netlint.utils import NOS


@Checker.register(apply_to=[NOS.CISCO_IOS, NOS.CISCO_NXOS], name="VAR101")
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


@Checker.register(apply_to=[NOS.CISCO_IOS, NOS.CISCO_NXOS], name="VAR102")
def check_unused_access_lists(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check for any ACLs that are configured but never used."""
    parsed_config = CiscoConfParse(config)
    access_lists = parsed_config.find_lines(
        r"^ip(v6)?\saccess-list\s(standard|extended)"
    )
    unused_acls = []
    for acl in access_lists:
        _, _, _, name = acl.split(" ", maxsplit=4)
        usages = parsed_config.find_lines("(ip)? access-(group|class) {}".format(name))
        if not usages:
            unused_acls.append(acl)
    if unused_acls:
        return CheckResult(text="Unused ACLs configured", lines=unused_acls)
    else:
        return None
