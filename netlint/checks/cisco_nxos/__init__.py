"""Checks for the Cisco NXOS NOS."""
import typing

from ciscoconfparse import CiscoConfParse

from netlint.checks.checker import CheckResult, Checker

__all__ = [
    "check_telnet_enabled",
    "check_routing_protocol_enabled_and_used",
    "check_password_strength",
    "check_bogus_as",
    "check_lacp_feature_enabled_and_used",
    "check_vpc_feature_enabled_and_used",
]

from netlint.checks.constants import bogus_as_numbers
from netlint.checks.utils import NOS, Tag


@Checker.register(
    apply_to=[NOS.CISCO_NXOS], name="NXOS101", tags={Tag.SECURITY, Tag.OPINIONATED}
)
def check_telnet_enabled(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check if the telnet feature is explicitly enabled."""
    parsed_config = CiscoConfParse(config)
    lines = parsed_config.find_lines("^feature telnet")
    if lines:
        return CheckResult(text="Feature telnet is enabled.", lines=lines)
    else:
        return None


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS102", tags={Tag.HYGIENE})
def check_routing_protocol_enabled_and_used(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if a routing protocol is actually used - should it be enabled."""
    parsed_config = CiscoConfParse(config)
    for protocol in ["bgp", "ospf", "eigrp", "rip"]:
        feature_enabled = parsed_config.find_lines(f"^feature {protocol}")
        if not feature_enabled:
            return None

        feature_used = parsed_config.find_lines(f"^router {protocol}")
        if not feature_used:
            return CheckResult(
                text=f"{protocol.upper()} enabled but never used.",
                lines=feature_enabled + feature_used,
            )
    return None


@Checker.register(
    apply_to=[NOS.CISCO_NXOS], name="NXOS103", tags={Tag.SECURITY, Tag.OPINIONATED}
)
def check_password_strength(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check if the password strength check has been disabled."""
    parsed_config = CiscoConfParse(config)
    disabled = parsed_config.find_lines("^no password strength-check")
    if disabled:
        return CheckResult(text="Password strength-check disabled.", lines=disabled)
    else:
        return None


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS104", tags={Tag.HYGIENE})
def check_bogus_as(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check if any bogus autonomous system is used in the configuration."""
    parsed_config = CiscoConfParse(config)
    bgp_routers = parsed_config.find_lines("^router bgp")
    bad_lines = []
    for line in bgp_routers:
        as_number = int(line[11:])
        if as_number in bogus_as_numbers:
            bad_lines.append(line)

    if bad_lines:
        return CheckResult(text="Bogus AS number in use", lines=bad_lines)
    else:
        return None


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS105", tags={Tag.HYGIENE})
def check_vpc_feature_enabled_and_used(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if the vPC feature is actually used if it is enabled."""
    parsed_config = CiscoConfParse(config)
    feature_enabled = parsed_config.find_lines(r"^feature vpc")
    feature_configured = parsed_config.find_lines(r"^vpc domain")
    if feature_enabled and not feature_configured:
        return CheckResult(
            text="vPC feature enabled but never used",
            lines=feature_enabled + feature_configured,
        )
    return None


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS106", tags={Tag.HYGIENE})
def check_lacp_feature_enabled_and_used(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if the LACP feature is actually used if it is enabled."""
    parsed_config = CiscoConfParse(config)
    feature_enabled = parsed_config.find_lines(r"^feature lacp")
    feature_configured = parsed_config.find_lines(
        r"^\s+channel-group \d+ mode active|passive"
    )
    if feature_enabled and not feature_configured:
        return CheckResult(
            text="LACP feature enabled but never used",
            lines=feature_enabled + feature_configured,
        )
    return None
