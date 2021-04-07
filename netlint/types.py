import typing


class JSONOutput(typing.TypedDict):
    text: str
    lines: typing.List[str]


JSONOutputDict = typing.Dict[str, JSONOutput]
ConfigCheckResult = typing.Union[str, JSONOutputDict]
