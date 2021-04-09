import functools
import typing

RT = typing.TypeVar("RT")


class CheckResult(typing.NamedTuple):
    text: str
    lines: typing.List[str]


CheckFunction = typing.Callable[[typing.List[str]], typing.Optional[CheckResult]]


class CheckFunctionTuple(typing.NamedTuple):
    name: str
    function: CheckFunction


class Checker:
    """Class to handle check execution."""

    def __init__(self) -> None:
        # Map NOSes to applicable checks
        self.checks: typing.Dict[str, typing.List[CheckFunctionTuple]] = {}

        # Map check name to check result (NOS-agnostic)
        self.check_results: typing.Dict[str, typing.Optional[CheckResult]] = {}

    def register(
        self, apply_to: typing.List[str], name: str
    ) -> typing.Callable[[typing.Callable[..., RT]], typing.Callable[..., RT]]:
        """Decorator to register a check with the Checker instance.

        :param apply_to: List of NOSes to apply the check for.
        :param name: Name of the check.
        """
        def decorator(
            function: typing.Callable[..., RT],
        ) -> typing.Callable[..., RT]:
            # Extend the docstring to include the decorator metadata
            function.__doc__ += "\n" * 2
            function.__doc__ += "Metadata:\n"
            function.__doc__ += f"Check {name}, applies to:\n"
            function.__doc__ += "\n  - ".join(apply_to)

            # Set an attribute on the function in order to indicate its status as a check
            # to the testing suite.
            function.test = True
            check_function_tuple = CheckFunctionTuple(
                function=function, name=name
            )
            for nos in apply_to:
                if nos in self.checks:
                    self.checks[nos].append(check_function_tuple)
                else:
                    self.checks[nos] = [check_function_tuple]


            @functools.wraps(function)
            def wrapper(*args: typing.Any, **kwargs: typing.Any) -> RT:
                return function(*args, **kwargs)

            return wrapper

        return decorator

    def run_checks(self, configuration: typing.List[str], nos: str) -> bool:
        """
        Run all the registered checks on the configuration.
        :param configuration: The configuration to check.
        :param nos: The NOS the configuration is for.
        :return: True if all checks succeed, False otherwise.
        """
        for check in self.checks[nos]:
            self.check_results[check.name] = check.function(configuration)
        return not any(self.check_results.values())
