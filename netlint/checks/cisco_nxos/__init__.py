"""Checks for the Cisco NXOS NOS."""
import typing

from netlint.checks.checker import Checker
from netlint.checks.cisco_nxos.utils import _feature_enabled_but_not_configured
from netlint.checks.types import CheckResult

__all__ = [
    "check_telnet_enabled",
    "check_routing_protocol_enabled_and_used",
    "check_password_strength",
    "check_bogus_as",
    "check_lacp_feature_enabled_and_used",
    "check_vpc_feature_enabled_and_used",
    "check_fex_feature_set_installed_but_not_enabled",
    "check_switchport_mode_fex_fabric",
]

from netlint.checks.constants import bogus_as_numbers
from netlint.checks.utils import NOS, Tag, parse


@Checker.register(
    apply_to=[NOS.CISCO_NXOS], name="NXOS101", tags={Tag.SECURITY, Tag.OPINIONATED}
)
def check_telnet_enabled(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check if the telnet feature is explicitly enabled."""
    config = parse("\n".join(config))
    lines = config.find_lines("^feature telnet")
    if lines:
        return CheckResult(text="Feature telnet is enabled.", lines=lines)
    else:
        return None


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS102", tags={Tag.HYGIENE})
def check_routing_protocol_enabled_and_used(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if a routing protocol is actually used - should it be enabled."""
    config = parse("\n".join(config))
    for protocol in ["bgp", "ospf", "eigrp", "rip"]:
        feature_enabled = config.find_lines(f"^feature {protocol}")
        if not feature_enabled:
            return None

        feature_used = config.find_lines(f"^router {protocol}")
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
    config = parse("\n".join(config))
    disabled = config.find_lines("^no password strength-check")
    if disabled:
        return CheckResult(text="Password strength-check disabled.", lines=disabled)
    else:
        return None


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS104", tags={Tag.HYGIENE})
def check_bogus_as(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check if any bogus autonomous system is used in the configuration."""
    config = parse("\n".join(config))
    bgp_routers = config.find_lines("^router bgp")
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
    config = parse("\n".join(config))
    return _feature_enabled_but_not_configured(
        config, r"^feature vpc", r"^vpc domain", "vPC feature enabled but never used"
    )


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS106", tags={Tag.HYGIENE})
def check_lacp_feature_enabled_and_used(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if the LACP feature is actually used if it is enabled."""
    config = parse("\n".join(config))
    return _feature_enabled_but_not_configured(
        config,
        r"^feature lacp",
        r"^\s+channel-group \d+ mode active|passive",
        "LACP feature enabled but never used",
    )


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS107", tags={Tag.HYGIENE})
def check_fex_feature_set_installed_but_not_enabled(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if the fex feature-set is installed but not enabled."""
    config = parse("\n".join(config))
    return _feature_enabled_but_not_configured(
        config,
        r"^install feature-set fex",
        r"^feature-set fex",
        "Feature-set fex installed but not enabled.",
    )


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS108", tags={Tag.HYGIENE})
def check_switchport_mode_fex_fabric(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if any interface in switchport mode fex-fabric has a fex-id associated."""
    config = parse("\n".join(config))
    interfaces = config.find_objects_w_child("^interface", "switchport mode fex-fabric")
    faulty_lines = []
    for interface in interfaces:
        current_lines = [interface.text]
        for line in interface.children:
            current_lines.append(line.text)
            if line.text.strip().startswith("fex associate"):
                break
        else:
            faulty_lines.extend(current_lines)
    if faulty_lines:
        return CheckResult(
            text="Interface in switchport mode fex-fabric without associated fex.",
            lines=faulty_lines,
        )
    else:
        return None


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS109", tags={Tag.HYGIENE})
def check_fex_feature_enabled_and_used(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check whether an enabled fex feature is actually used."""
    config = parse("\n".join(config))
    return _feature_enabled_but_not_configured(
        config,
        r"^feature-set fex",
        r"^fex id",
        "Feature-set fex enabled but never used.",
    )


@Checker.register(apply_to=[NOS.CISCO_NXOS], name="NXOS110", tags={Tag.HYGIENE})
def check_fex_without_interface(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check whether every configured fex id also has an associated interface."""
    config = parse("\n".join(config))
    configured_fex_ids = config.find_lines(r"^fex id")
    faulty_fex_ids = []
    for line in configured_fex_ids:
        fex_id = line.split()[2]
        has_interface = config.find_lines(r"^\s+fex associate {}".format(fex_id))
        if not has_interface:
            faulty_fex_ids.append(line)
    if faulty_fex_ids:
        return CheckResult(
            text="FEX without associated interface configured.", lines=faulty_fex_ids
        )
    else:
        return None
