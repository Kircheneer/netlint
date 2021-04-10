import json
import typing
from pathlib import Path

import click
from click_default_group import DefaultGroup  # type: ignore

from netlint.checks import checker_instance
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
    type=click.Choice(["json", "normal"]),
    help="The format of the output data.",
)
@click.option(
    "--nos",
    type=click.Choice(["cisco_ios", "cisco_nxos"]),
    help="The NOS the configuration(s) is/are for.",
)
@click.option(
    "--select",
    type=str,
    help="Comma-separated list of check names to include."
)
@click.pass_context
def lint(
    ctx: click.Context,
    path: str,
    glob: str,
    prefix: str,
    output: typing.Optional[str],
    format_: str,
    nos: str,
    select: typing.Optional[str]
) -> None:
    """Lint network device configuration files."""

    if ctx.invoked_subcommand:
        return

    if select:
        selected_checks = []
        for check in checker_instance.checks[nos]:
            if check.name in select.split(","):
                selected_checks.append(check)
        checker_instance.checks[nos] = selected_checks

    input_path = Path(path)

    if input_path.is_file():
        processed_config = check_config(
            ctx.obj["color"], format_, input_path, ctx.obj["plain"], prefix, nos
        )
        assert isinstance(processed_config, str)
        with smart_open(output) as f:
            f.write(processed_config)
    elif input_path.is_dir():
        path_items = input_path.glob(glob)
        processed_configs: typing.Dict[str, typing.Union[str, JSONOutputDict]] = {}
        for item in path_items:
            processed_configs[str(item)] = check_config(
                ctx.obj["color"], format_, item, ctx.obj["plain"], prefix, nos
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
@click.pass_context
def list_(ctx: click.Context) -> None:
    """List configuration checks."""
    for nos, checks in checker_instance.checks.items():
        click.secho(f"{'=' * 10} {nos} {'=' * 10}", bold=not ctx.obj["plain"])
        for check in checks:
            click.secho(check.name)


def check_config(
    color: bool, format_: str, path: Path, plain: bool, prefix: str, nos: str
) -> ConfigCheckResult:
    """Run checks on config at a given path."""
    return_value: typing.Union[str, JSONOutputDict] = "" if format_ == "normal" else {}

    with open(path, "r") as f:
        configuration = f.readlines()
    checker_instance.run_checks(configuration, nos)

    for check, result in checker_instance.check_results.items():
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
