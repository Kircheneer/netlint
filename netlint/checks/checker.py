"""Implement the Checker class to run the checks."""
import functools
import typing

from netlint.checks.utils import NOS


class CheckResult(typing.NamedTuple):
    """Result of a single check."""

    text: str
    lines: typing.List[str]


# Signature of a check function taking in a list of strings (the configuration)
# and returning a CheckResult.
CheckFunction = typing.Callable[[typing.List[str]], typing.Optional[CheckResult]]


class CheckFunctionTuple(typing.NamedTuple):
    """Represent check functions along with any metadata."""

    name: str
    function: CheckFunction


class Check:
    """Class to represent a check function.

    Auto-generated when @Checker.register() is used on a function.
    """

    def __init__(
        self, check_function: CheckFunction, apply_to: typing.List[NOS], name: str
    ) -> None:
        self.check_function = check_function
        self.apply_to = apply_to
        self.name = name
        self.function_doc = check_function.__doc__

    def __call__(self, configuration: typing.List[str]) -> typing.Optional[CheckResult]:
        """Call the underlying function."""
        return self.check_function(configuration)


class Checker:
    """Class to handle check execution."""

    # Map NOSes to applicable checks
    checks: typing.Dict[NOS, typing.List[Check]] = {}

    def __init__(self) -> None:
        # Map check name to check result (NOS-agnostic)
        self.check_results: typing.Dict[str, typing.Optional[CheckResult]] = {}

    @classmethod
    def register(
        cls, apply_to: typing.List[NOS], name: str
    ) -> typing.Callable[
        [typing.Callable[[typing.List[str]], typing.Optional[CheckResult]]],
        Check,
    ]:
        """Decorate a function to register it as a check with any Checker instance.

        :param apply_to: List of NOSes to apply the check for.
        :param name: Name of the check.
        """

        def decorator(
            function: typing.Callable[[typing.List[str]], typing.Optional[CheckResult]],
        ) -> Check:
            @functools.wraps(function)
            def wrapper(config: typing.List[str]) -> typing.Optional[CheckResult]:
                return function(config)

            check = Check(check_function=wrapper, apply_to=apply_to, name=name)
            for nos in apply_to:
                if nos in cls.checks:
                    cls.checks[nos].append(check)
                else:
                    cls.checks[nos] = [check]
            return check

        return decorator

    def run_checks(self, configuration: typing.List[str], nos: NOS) -> bool:
        """
        Run all the registered checks on the configuration.

        :param configuration: The configuration to check.
        :param nos: The NOS the configuration is for.
        :return: True if all checks succeed, False otherwise.
        """
        for check in self.checks[nos]:
            self.check_results[check.name] = check(configuration)
        return not any(self.check_results.values())
