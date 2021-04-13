"""CLI utilities."""
import contextlib
import sys
import typing
from enum import Enum

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


def style(message: str, quiet: bool, **kwargs: typing.Any) -> str:
    """Style a message with click.style if quiet is not set."""
    if quiet:
        return message
    else:
        return click.style(message, **kwargs)


class NOS(Enum):
    """Overview of different available NOSes."""

    CISCO_IOS = "cisco_ios"
    CISCO_NXOS = "cisco_nxos"


def detect_nos(configuration: typing.List[str]) -> NOS:
    """Automatically detect the NOS in the configuration.

    Very rudimentary as of now, will get more complex support for more NOSes is added.
    """
    for line in configuration:
        if "feature" in line:
            return NOS.CISCO_NXOS
    return NOS.CISCO_IOS
