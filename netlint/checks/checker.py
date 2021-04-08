import typing

from ciscoconfparse import CiscoConfParse


class CheckResult(typing.NamedTuple):
    text: str
    lines: typing.List[str]


CheckFunction = typing.Callable[[CiscoConfParse], typing.Optional[CheckResult]]


class CheckFunctionTuple(typing.NamedTuple):
    name: str
    function: CheckFunction


class Checker:
    """Class to handle check execution."""

    def __init__(self) -> None:
        # Map NOSes to applicable checks
        self.checks: typing.Dict[str, CheckFunctionTuple] = {}

        # Map check name to check result (NOS-agnostic)
        self.check_results: typing.Dict[str, typing.Optional[CheckResult]] = {}

    def register(self, check: CheckFunctionTuple, apply_to: typing.List[str]) -> None:
        """
        Register a check in the checker instance.
        :param name: The name of the check (like A101)
        :param check: The function doing the actual checking.
        :param apply_to: List of NOSes to apply this check to.
        :return: None.
        """
        for nos in apply_to:
            self.checks[nos] = check

    def run_checks(self, configuration: CiscoConfParse) -> bool:
        """
        Run all the registered checks on the configuration.
        :param configuration: The configuration to check.
        :return: True if all checks succeed, False otherwise.
        """
        for name, check in self.checks.items():
            self.check_results[name] = check.function(configuration)
        return not any(self.check_results.values())
