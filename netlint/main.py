import json
import sys
import typing
from enum import Enum
from pathlib import Path

import typer
from ciscoconfparse import CiscoConfParse

from netlint.checks import checker
from netlint.utils import smart_open

app = typer.Typer()


class JSONOutput(typing.TypedDict):
    text: str
    lines: typing.List[str]


class OutputFormat(str, Enum):
    json = "json"
    normal = "normal"


JSONOutputDict = typing.Dict[str, JSONOutput]
ConfigCheckResult = typing.Union[str, JSONOutputDict]


@app.command(name="list")
def list_() -> None:
    """List available checks."""
    for check in checker.checks:
        typer.echo(check)


@app.command(name="lint")
def lint(
    path: Path = typer.Argument(
        default=None,
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to configuration file or directory containing files.",
    ),
    glob: str = typer.Option(
        "*.conf", "--glob", help="Glob pattern to match files in the path with."
    ),
    prefix: str = typer.Option(
        "-> ", help="Prefix for configuration lines output to the CLI."
    ),
    output: typing.Optional[Path] = typer.Option(None, "-o", "--output", help="Optional output file."),
    format_: OutputFormat = typer.Option(OutputFormat.normal, "--format"),
    plain: bool = typer.Option(
        False, help="Un-styled CLI output (implicit --no-color)."
    ),
    color: bool = typer.Option(default=True, help="Use color in CLI output."),
) -> None:
    """Lint network device configuration files."""
    if plain:
        color = False

    if path.is_file():
        processed_config = check_config(color, format_, path, plain, prefix)
        assert isinstance(processed_config, str)
        with smart_open(output) as f:
            f.write(processed_config)
    elif path.is_dir():
        path_items = path.glob(glob)
        processed_configs: typing.Dict[str, typing.Union[str, JSONOutputDict]] = {}
        for item in path_items:
            processed_configs[str(item)] = check_config(
                color, format_, item, plain, prefix
            )
        with smart_open(output) as f:
            if format_ == OutputFormat.normal:
                for key, value in processed_configs.items():
                    assert isinstance(value, str)
                    f.write(
                        typer.style(
                            f"{'=' * 10} {key} {'=' * 10}\n", bold=True and plain
                        )
                    )
                    f.write(value)
            elif format_ == OutputFormat.json:
                json.dump(processed_configs, f)


def check_config(
    color: bool, format_: OutputFormat, path: Path, plain: bool, prefix: str
) -> ConfigCheckResult:
    """Run checks on config at a given path."""
    return_value: typing.Union[str, JSONOutputDict] = (
        "" if format_ == OutputFormat.normal else {}
    )

    with open(path, "r") as f:
        configuration = CiscoConfParse(f.readlines())
    checker.run_checks(configuration)

    for check, result in checker.check_results.items():
        if not result:
            continue
        if format_ == format_.normal:
            assert isinstance(return_value, str)
            return_value += typer.style(check, bold=not plain)
            return_value += " " + result.text + "\n"
            return_value += typer.style(
                prefix + prefix.join(result.lines),
                fg=typer.colors.BRIGHT_RED if color else None,
            )
        elif format_ == format_.json:
            assert isinstance(return_value, dict)
            return_value[check] = {
                "text": result.text,
                "lines": result.lines,
            }
    return return_value


def run() -> typing.Any:
    """Wrapper around app() to default to the 'lint' command."""
    try:
        if sys.argv[1] not in [command.name for command in app.registered_commands]:
            sys.argv.insert(1, "lint")
    except IndexError:
        pass
    return app()


if __name__ == "__main__":
    run()
