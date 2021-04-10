import typing
from types import ModuleType

import click

from netlint.checks.checker import CheckFunction


def get_method(check: str, module: ModuleType) -> typing.Optional[CheckFunction]:
    """Get a check method from a module."""
    method = getattr(module, check)
    # Check is method is registered with any Checker (and therefore has to be tested)
    registered = getattr(method, "test", False)
    if registered:
        return method
    else:
        return None


def style(message: str, plain: bool, **kwargs) -> str:
    if plain:
        return message
    else:
        return click.style(message, **kwargs)
