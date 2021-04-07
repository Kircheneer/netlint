import json
import typing
from pathlib import Path

import click
from ciscoconfparse import CiscoConfParse
from click_default_group import DefaultGroup  # type: ignore

from netlint.checks import checker
from netlint.types import JSONOutputDict, ConfigCheckResult
from netlint.utils import smart_open


@click.group(cls=DefaultGroup, default="lint", default_if_no_args=True)
@click.option(
    "-p",
    "--plain",
    is_flag=True,
    default=False,
    type=bool,
    help="Un-styled CLI output (implicit --no-color).",
)
@click.option("--color", default=True, help="Use color in CLI output.")
@click.pass_context
def cli(ctx: click.Context, plain: bool, color: bool) -> None:
    """Lint network device configuration files."""
    ctx.ensure_object(dict)
    ctx.obj["plain"] = plain
    if plain:
        ctx.obj["color"] = False
    else:
        ctx.obj["color"] = color


@cli.command()
@click.argument(
    "path",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True
    ),
)
@click.option(
    "--glob", default="*.conf", help="Glob pattern to match files in the path with."
)
@click.option(
    "--prefix", default="-> ", help="Prefix for configuration lines output to the CLI."
)
@click.option(
    "-o", "--output", type=click.Path(writable=True), help="Optional output file."
)
@click.option(
    "--format",
    "format_",
    default="normal",
    type=click.Choice(["json", "normal"], case_sensitive=False),
)
@click.pass_context
def lint(
    ctx: click.Context,
    path: str,
    glob: str,
    prefix: str,
    output: str,
    format_: str,
) -> None:
    """Lint network device configuration files."""

    if ctx.invoked_subcommand:
        return

    input_path = Path(path)

    if input_path.is_file():
        processed_config = check_config(
            ctx.obj["color"], format_, input_path, ctx.obj["plain"], prefix
        )
        assert isinstance(processed_config, str)
        with smart_open(output) as f:
            f.write(processed_config)
    elif input_path.is_dir():
        path_items = input_path.glob(glob)
        processed_configs: typing.Dict[str, typing.Union[str, JSONOutputDict]] = {}
        for item in path_items:
            processed_configs[str(item)] = check_config(
                ctx.obj["color"], format_, item, ctx.obj["plain"], prefix
            )
        with smart_open(output) as f:
            if format_ == "normal":
                for key, value in processed_configs.items():
                    assert isinstance(value, str)
                    f.write(
                        click.style(
                            f"{'=' * 10} {key} {'=' * 10}\n",
                            bold=True and ctx.obj["plain"],
                        )
                    )
                    f.write(value)
            elif format_ == "json":
                json.dump(processed_configs, f)


@cli.command(name="list")
def list_() -> None:
    """List configuration checks."""
    for command in checker.checks:
        click.echo(command)


def check_config(
    color: bool, format_: str, path: Path, plain: bool, prefix: str
) -> ConfigCheckResult:
    """Run checks on config at a given path."""
    return_value: typing.Union[str, JSONOutputDict] = "" if format_ == "normal" else {}

    with open(path, "r") as f:
        configuration = CiscoConfParse(f.readlines())
    checker.run_checks(configuration)

    for check, result in checker.check_results.items():
        if not result:
            continue
        if format_ == "normal":
            assert isinstance(return_value, str)
            return_value += click.style(check, bold=not plain)
            return_value += " " + result.text + "\n"
            return_value += click.style(
                prefix + prefix.join(result.lines),
                fg="red" if color else None,
            )
        elif format_ == "json":
            assert isinstance(return_value, dict)
            return_value[check] = {
                "text": result.text,
                "lines": result.lines,
            }
    return return_value


if __name__ == "__main__":
    cli(obj={})
