import json
import typing
from pathlib import Path

import click

from netlint.checks import checker_instance
from netlint.types import JSONOutputDict
from netlint.utils import smart_open, style

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)  # type: ignore
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
    "--exit-zero",
    is_flag=True,
    default=False,
    help="Exit code 0 even if errors are found.",
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
    help="Comma-separated list of check names to include"
    "(mutually exclusive with --exclude).",
)
@click.option(
    "--exclude",
    type=str,
    help="Comma-separated list of check names to exclude"
    "(mutually exclusive with --select).",
)
@click.option(
    "-p",
    "--plain",
    is_flag=True,
    default=False,
    type=bool,
    help="Un-styled CLI output.",
    envvar="NO_COLOR",
)
# Passing None as the first parameter leads to autodiscovery via setuptools
@click.version_option(None, "-V", "--version", message="%(version)s")
@click.pass_context
def cli(
    ctx: click.Context,
    path: str,
    glob: str,
    prefix: str,
    output: typing.Optional[str],
    format_: str,
    nos: str,
    select: typing.Optional[str],
    exclude: typing.Optional[str],
    plain: bool,
    exit_zero: bool,
) -> None:
    """Performs static analysis on network device configuration files."""

    if select and exclude:
        click.echo("Error: --select and --exclude are mutually exclusive.")
        ctx.exit(-1)

    has_errors = False

    if select:
        selected_checks = []
        for check in checker_instance.checks[nos]:
            if check.name in select.split(","):
                selected_checks.append(check)
        checker_instance.checks[nos] = selected_checks
    elif exclude:
        excluded_checks = []
        for check in checker_instance.checks[nos]:
            if check.name in exclude.split(","):
                excluded_checks.append(check)
        for check in excluded_checks:
            checker_instance.checks[nos].remove(check)

    input_path = Path(path)

    if input_path.is_file():
        processed_config = check_config(input_path, nos)
        # assert isinstance(processed_config, str)
        if processed_config:
            has_errors = True
        with smart_open(output) as f:
            if format_ == "plain":
                f.write(checks_to_string(processed_config, plain, prefix))
            elif format_ == "json":
                json.dump(processed_config, f)
    elif input_path.is_dir():
        path_items = input_path.glob(glob)
        processed_configs: typing.Dict[str, JSONOutputDict] = {}
        for item in path_items:
            processed_configs[str(item)] = check_config(item, nos)
        if processed_configs:
            has_errors = True
        with smart_open(output) as f:
            if format_ == "normal":
                for key, value in processed_configs.items():
                    f.write(
                        style(
                            f"{'=' * 10} {key} {'=' * 10}\n",
                            plain=plain,
                            bold=True,
                        )
                    )
                    f.write(checks_to_string(value, plain, prefix))

            elif format_ == "json":
                json.dump(processed_configs, f)

    if has_errors and not exit_zero:
        ctx.exit(-1)
    else:
        ctx.exit(0)


def check_config(path: Path, nos: str) -> JSONOutputDict:
    """Run checks on config at a given path."""
    return_value: JSONOutputDict = {}

    with open(path, "r") as f:
        configuration = f.readlines()
    checker_instance.run_checks(configuration, nos)

    for check, result in checker_instance.check_results.items():
        if not result:
            continue
        return_value[check] = {
            "text": result.text,
            "lines": result.lines,
        }
    return return_value


def checks_to_string(
    check_result_dict: JSONOutputDict, plain: bool, prefix: str
) -> str:
    """Convert a check result to its string representation."""
    return_value = ""
    for check, result in check_result_dict.items():
        return_value += style(check, plain, bold=True)
        return_value += " " + result["text"] + "\n"
        return_value += style(
            prefix + prefix.join(result["lines"]),
            plain,
            fg="red",
        )
    return return_value


if __name__ == "__main__":
    cli()
