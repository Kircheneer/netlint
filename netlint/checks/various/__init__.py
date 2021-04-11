import typing

from ciscoconfparse import CiscoConfParse

from netlint.checks import checker_instance
from netlint.checks.checker import CheckResult

__all__ = ["check_default_snmp_communities"]


@checker_instance.register(apply_to=["cisco_ios", "cisco_nxos"], name="VAR101")
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
