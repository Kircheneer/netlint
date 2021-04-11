"""Checks for the Cisco NXOS NOS."""
import typing

from ciscoconfparse import CiscoConfParse

from netlint.checks.checker import CheckResult, Checker

__all__ = ["check_telnet_enabled", "check_bgp_enabled_and_used"]


@Checker.register(apply_to=["cisco_nxos"], name="NXOS101")
def check_telnet_enabled(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check if the telnet feature is explicitly enabled."""
    parsed_config = CiscoConfParse(config)
    lines = parsed_config.find_lines("^feature telnet")
    if lines:
        return CheckResult(text="Feature telnet is enabled.", lines=lines)
    else:
        return None


@Checker.register(apply_to=["cisco_nxos"], name="NXOS102")
def check_bgp_enabled_and_used(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if BGP is actually used - should it be enabled."""
    parsed_config = CiscoConfParse(config)
    bgp_enabled = parsed_config.find_lines("^feature bgp")
    if not bgp_enabled:
        return None

    bgp_used = parsed_config.find_lines("^router bgp")
    if not bgp_used:
        return CheckResult(
            text="BGP enabled but never used.", lines=bgp_enabled + bgp_used
        )
    else:
        return None
