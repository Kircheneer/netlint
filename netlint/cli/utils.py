"""CLI utilities."""
import contextlib
import sys
import typing

import click


@contextlib.contextmanager
def smart_open(
    filename: typing.Optional[str] = None,
) -> typing.Generator[typing.TextIO, None, None]:
    """Return a file handler for filename or sys.stdout if filename is None."""
    if filename and filename != "-":
        fh = open(filename, "w")
    else:
        fh = sys.stdout
    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def style(message: str, plain: bool, **kwargs: typing.Any) -> str:
    """Style a message with click.style if quiet is not set."""
    if plain:
        return message
    else:
        return click.style(message, **kwargs)


@contextlib.contextmanager
def optional(
    condition: bool, context_manager: typing.ContextManager
) -> typing.Generator:
    """Apply the content manager if condition evaluates to True."""
    if condition:
        with context_manager:
            yield
    else:
        yield
