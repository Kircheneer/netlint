"""Implement the Checker class to run the checks."""
import functools
import typing

from netlint.utils import NOS


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


class Checker:
    """Class to handle check execution."""

    # Map NOSes to applicable checks
    checks: typing.Dict[NOS, typing.List[CheckFunctionTuple]] = {}

    def __init__(self) -> None:
        # Map check name to check result (NOS-agnostic)
        self.check_results: typing.Dict[str, typing.Optional[CheckResult]] = {}

    @classmethod
    def register(
        cls, apply_to: typing.List[NOS], name: str
    ) -> typing.Callable[
        [typing.Callable[[typing.List[str]], typing.Optional[CheckResult]]],
        typing.Callable[[typing.List[str]], typing.Optional[CheckResult]],
    ]:
        """Decorate a function to register it as a check with any Checker instance.

        :param apply_to: List of NOSes to apply the check for.
        :param name: Name of the check.
        """

        def decorator(
            function: typing.Callable[[typing.List[str]], typing.Optional[CheckResult]],
        ) -> typing.Callable[[typing.List[str]], typing.Optional[CheckResult]]:
            # Extend the docstring to include the decorator metadata
            heading = f"**{name}**\n\n"
            if function.__doc__:
                function.__doc__ = heading + function.__doc__
            else:
                function.__doc__ = heading
            function.__doc__ += "\n\n"
            function.__doc__ += "Applies to:"
            function.__doc__ += "\n" * 2
            for nos in apply_to:
                function.__doc__ += f"* {nos}"
                function.__doc__ += "\n"
            function.__doc__ += "\n"

            # Set an attribute on the function in order to indicate its status as
            # a check to the testing suite.
            function.test = True  # type: ignore
            check_function_tuple = CheckFunctionTuple(function=function, name=name)
            for nos in apply_to:
                if nos in cls.checks:
                    cls.checks[nos].append(check_function_tuple)
                else:
                    cls.checks[nos] = [check_function_tuple]

            @functools.wraps(function)
            def wrapper(config: typing.List[str]) -> typing.Optional[CheckResult]:
                return function(config)

            return wrapper

        return decorator

    def run_checks(self, configuration: typing.List[str], nos: NOS) -> bool:
        """
        Run all the registered checks on the configuration.

        :param configuration: The configuration to check.
        :param nos: The NOS the configuration is for.
        :return: True if all checks succeed, False otherwise.
        """
        for check in self.checks[nos]:
            self.check_results[check.name] = check.function(configuration)
        return not any(self.check_results.values())
