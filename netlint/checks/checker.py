import typing

from ciscoconfparse import CiscoConfParse


class CheckResult(typing.NamedTuple):
    text: str
    lines: typing.List[str]


CheckFunction = typing.Callable[[CiscoConfParse], typing.Optional[CheckResult]]


class Checker:
    """Class to handle check execution."""

    def __init__(self) -> None:
        self.checks: typing.Dict[str, CheckFunction] = {}
        self.check_results: typing.Dict[str, typing.Optional[CheckResult]] = {}

    def register(self, name: str, check: CheckFunction) -> None:
        """
        Register a check in the checker instance.
        :param name: The name of the check (like A101)
        :param check: The function doing the actual checking.
        :return: None.
        """
        self.checks[name] = check

    def run_checks(self, configuration: CiscoConfParse) -> bool:
        """
        Run all the registered checks on the configuration.
        :param configuration: The configuration to check.
        :return: True if all checks succeed, False otherwise.
        """
        for name, check in self.checks.items():
            self.check_results[name] = check(configuration)
        return not any(self.check_results.values())
