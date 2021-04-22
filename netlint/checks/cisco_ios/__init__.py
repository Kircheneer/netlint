"""Checks for the Cisco IOS NOS."""
import re
import typing

from ciscoconfparse import CiscoConfParse

from netlint.checks import constants as c
from netlint.checks.checker import CheckResult, Checker

__all__ = [
    "check_plaintext_passwords",
    "check_console_password",
    "check_ip_http_server",
    "check_password_hash_strength",
]

from netlint.checks.utils import (
    get_password_hash_algorithm,
    NOS,
    Tag,
    get_access_list_usage,
    get_access_list_definitions,
    get_name_from_acl_definition,
)


@Checker.register(apply_to=[NOS.CISCO_IOS], name="IOS101", tags={Tag.SECURITY})
def check_plaintext_passwords(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check if there are any plaintext passwords in the configuration."""
    parsed_config = CiscoConfParse(config)
    lines = parsed_config.find_lines("^username.*password")
    if lines:
        # If `service password-encryption` is configured, users are saved to the
        # config like `username test password 7 $ENCRYPTED. The following for-loop
        # checks for that.
        for line in lines:
            has_hash_algorithm = get_password_hash_algorithm(line)
            if not has_hash_algorithm:
                break
        else:
            # If the for loop wasn't exited prematurely, no plaintext passwords
            # are present.
            return None
        return CheckResult(
            text="Plaintext user passwords in configuration.", lines=lines
        )
    else:
        return None


@Checker.register(
    apply_to=[NOS.CISCO_IOS], name="IOS102", tags={Tag.SECURITY, Tag.OPINIONATED}
)
def check_ip_http_server(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check if the http server is enabled."""
    parsed_config = CiscoConfParse(config)
    lines = parsed_config.find_lines("^ip http")
    if lines:
        return CheckResult(text="HTTP server not disabled.", lines=lines)
    else:
        return None


@Checker.register(
    apply_to=[NOS.CISCO_IOS], name="IOS103", tags={Tag.SECURITY, Tag.OPINIONATED}
)
def check_console_password(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check for authentication on the console line."""
    parsed_config = CiscoConfParse(config)
    line_con_config = parsed_config.find_all_children("^line con 0")
    if len(line_con_config) == 0:
        return None  # TODO: Log this?

    login = False
    password = False
    for line in line_con_config:
        if "login" in line:
            login = True
        if "password" in line:
            password = True

    if not login or not password:
        return CheckResult(text="Console line unauthenticated.", lines=line_con_config)
    else:
        return None


@Checker.register(apply_to=[NOS.CISCO_IOS], name="IOS104", tags={Tag.SECURITY})
def check_password_hash_strength(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if strong password hash algorithms were used."""
    parsed_config = CiscoConfParse(config)
    lines_with_passwords = parsed_config.find_lines(r"^.*(password|secret)\s\d.*$")
    bad_lines = []
    for line in lines_with_passwords:
        hash_algorithm = get_password_hash_algorithm(line)
        if hash_algorithm in c.bad_hash_algorithms:
            bad_lines.append(line)
    if bad_lines:
        return CheckResult("Insecure hash algorithms in use.", lines=bad_lines)
    else:
        return None


@Checker.register(apply_to=[NOS.CISCO_IOS], name="IOS105", tags={Tag.HYGIENE})
def check_switchport_trunk_config(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if the switchport mode matches all config commands per interface."""
    parsed_config = CiscoConfParse(config)
    interfaces = parsed_config.find_objects_w_child(
        r"^interface", r"^\s+switchport mode trunk"
    )
    bad_lines = []
    for interface in interfaces:
        bad_lines_per_interface = [interface.text]
        switchport_config_lines = list(
            filter(lambda l: re.match(r"^\s+switchport", l.text), interface.children)
        )
        for line in switchport_config_lines:
            if line.text.strip().startswith("switchport access"):
                bad_lines_per_interface.append(line.text)
        if len(bad_lines_per_interface) > 1:
            bad_lines.extend(bad_lines_per_interface)
    if bad_lines:
        return CheckResult(
            "Access port config present on trunk interfaces.", lines=bad_lines
        )
    else:
        return None


@Checker.register(
    apply_to=[NOS.CISCO_IOS],
    name="IOS106",
    tags={Tag.HYGIENE, Tag.SECURITY},
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


@Checker.register(apply_to=[NOS.CISCO_IOS], name="IOS107", tags={Tag.HYGIENE})
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


@Checker.register(apply_to=[NOS.CISCO_IOS], name="IOS108", tags={Tag.HYGIENE})
def check_switchport_access_config(
    config: typing.List[str],
) -> typing.Optional[CheckResult]:
    """Check if the switchport mode matches all config commands per interface."""
    parsed_config = CiscoConfParse(config)
    interfaces = parsed_config.find_objects_w_child(
        r"^interface", r"^\s+switchport mode access"
    )
    bad_lines = []
    for interface in interfaces:
        bad_lines_per_interface = [interface.text]
        switchport_config_lines = list(
            filter(lambda l: re.match(r"^\s+switchport", l.text), interface.children)
        )
        for line in switchport_config_lines:
            if line.text.strip().startswith("switchport trunk"):
                bad_lines_per_interface.append(line.text)
        if len(bad_lines_per_interface) > 1:
            bad_lines.extend(bad_lines_per_interface)
    if bad_lines:
        return CheckResult(
            "Trunk port config present on access interfaces.", lines=bad_lines
        )
    else:
        return None
