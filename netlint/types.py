import typing

import typing_extensions


class JSONOutput(typing_extensions.TypedDict):
    text: str
    lines: typing.List[str]


JSONOutputDict = typing.Dict[str, JSONOutput]
ConfigCheckResult = typing.Union[str, JSONOutputDict]
