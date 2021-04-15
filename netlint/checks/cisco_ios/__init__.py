"""Checks for the Cisco IOS NOS."""
import typing

from ciscoconfparse import CiscoConfParse

from netlint.checks.checker import CheckResult, Checker
from netlint.checks import constants as c

__all__ = [
    "check_plaintext_passwords",
    "check_console_password",
    "check_ip_http_server",
    "check_password_hash_strength",
]

from netlint.checks.utils import get_password_hash_algorithm
from netlint.utils import NOS


@Checker.register(apply_to=[NOS.CISCO_IOS], name="IOS101")
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


@Checker.register(apply_to=[NOS.CISCO_IOS], name="IOS102")
def check_ip_http_server(config: typing.List[str]) -> typing.Optional[CheckResult]:
    """Check if the http server is enabled."""
    parsed_config = CiscoConfParse(config)
    lines = parsed_config.find_lines("^ip http")
    if lines:
        return CheckResult(text="HTTP server not disabled.", lines=lines)
    else:
        return None


@Checker.register(apply_to=[NOS.CISCO_IOS], name="IOS103")
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


@Checker.register(apply_to=[NOS.CISCO_IOS], name="IOS104")
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
