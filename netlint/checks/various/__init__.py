"""Checks that apply to more than one NOS."""
import typing

from netlint.checks.checker import Checker
from netlint.checks.types import CheckResult

from netlint.checks.utils import (
    NOS,
    Tag,
    parse,
)

__all__ = [
    "check_default_snmp_communities",
]


@Checker.register(
    apply_to=[NOS.CISCO_IOS, NOS.CISCO_NXOS], name="VAR101", tags={Tag.SECURITY}
)
def check_default_snmp_communities(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check for presence of default SNMP community strings."""
    config = parse("\n".join(config))
    snmp_communities = config.find_lines("^snmp-server community")
    for community in snmp_communities:
        if community.startswith("snmp-server community public") or community.startswith(
            "snmp-server community private"
        ):
            return CheckResult(
                text="Default SNMP communities present.", lines=snmp_communities
            )

    return None
