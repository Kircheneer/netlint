"""Implement the Checker class to run the checks."""
import functools
import typing

from ciscoconfparse import CiscoConfParse

from netlint.checks.types import CheckResult, CheckFunction
from netlint.checks.utils import NOS, Tag


class Check:
    """Class to represent a check function.

    Auto-generated when @Checker.register() is used on a function.
    """

    def __init__(
        self,
        check_function: CheckFunction,
        apply_to: typing.List[NOS],
        name: str,
        tags: typing.Set[Tag],
    ) -> None:
        self.check_function = check_function
        self.apply_to = apply_to
        self.name = name
        self.tags = tags
        self.function_doc = check_function.__doc__

    def __call__(self, configuration: typing.List[str]) -> typing.Optional[CheckResult]:
        """Call the underlying function."""
        return self.check_function(configuration)


class Checker:
    """Class to handle check execution."""

    # Map NOSes to applicable checks
    checks: typing.Dict[NOS, typing.List[Check]] = {}

    def __init__(self) -> None:
        pass

    @classmethod
    def register(
        cls, apply_to: typing.List[NOS], name: str, tags: typing.Set[Tag]
    ) -> typing.Callable[
        [typing.Callable[[typing.List[str]], typing.Optional[CheckResult]]],
        Check,
    ]:
        """Decorate a function to register it as a check with any Checker instance.

        :param apply_to: List of NOSes to apply the check for.
        :param name: Name of the check.
        :param tags: A list of check tags that apply to this check.
        """

        def decorator(
            function: typing.Callable[[typing.List[str]], typing.Optional[CheckResult]],
        ) -> Check:
            @functools.wraps(function)
            def wrapper(config: typing.List[str]) -> typing.Optional[CheckResult]:
                return function(config)

            check = Check(
                check_function=wrapper, apply_to=apply_to, name=name, tags=tags
            )
            for nos in apply_to:
                if nos in cls.checks:
                    cls.checks[nos].append(check)
                else:
                    cls.checks[nos] = [check]
            return check

        return decorator

    def run_checks(
        self, configuration: typing.List[str], nos: NOS
    ) -> typing.Dict[str, typing.Optional[CheckResult]]:
        """
        Run all the registered checks on the configuration.

        :param configuration: The configuration to check.
        :param nos: The NOS the configuration is for.
        :return: The check results.
        """
        output = {}
        # Convert configuration to CiscoConfParse object if applicable.
        if nos in [NOS.CISCO_IOS, NOS.CISCO_NXOS]:
            configuration = CiscoConfParse(configuration)
        for check in self.checks[nos]:
            output[check.name] = check(configuration)
        return output
