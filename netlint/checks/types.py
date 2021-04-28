"""Custom types for the checker code."""

import typing


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
