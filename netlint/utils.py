import contextlib
import sys
import typing
from pathlib import Path


@contextlib.contextmanager
def smart_open(
    filename: typing.Optional[Path] = None,
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
