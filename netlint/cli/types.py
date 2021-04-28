"""Collection of custom types used."""
import typing

import typing_extensions


class JSONOutput(typing_extensions.TypedDict):
    """Represents a single check on a single configuration."""

    text: str
    lines: typing.List[str]


# Represents all checks on a single configuration.
JSONOutputDict = typing.Dict[str, typing.Optional[JSONOutput]]
