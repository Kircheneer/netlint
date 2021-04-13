"""CLI entrypoint to netlint."""
import json
import typing
from pathlib import Path

import click
import toml

from netlint.checks.checker import Checker
from netlint.types import JSONOutputDict
from netlint.utils import smart_open, style, detect_nos, NOS

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
DEFAULT_CONFIG = "pyproject.toml"


def configure(
    ctx: click.Context, _: typing.Union[click.Option, click.Parameter], filename: str
) -> None:
    """Evaluate the config file and set the default_map accordingly.

    Used as a callback from a click option.
    """
    configuration_file = Path(filename).absolute()
    configuration_dict = {}
    if configuration_file.exists():
        if filename == DEFAULT_CONFIG:
            try:
                configuration_dict = toml.load(configuration_file)["tool"]["netlint"]
            except KeyError:
                # If the user uses a pyproject.toml file but chooses not to configure
                # netlint there, we don't want to output anything.
                return
        else:
            try:
                configuration_dict = toml.load(configuration_file)["netlint"]
            except KeyError:
                click.secho(
                    f"Configuration file '{configuration_file} doesn't contain"
                    f"a [netlint] section."
                )
        ctx.default_map = configuration_dict
    elif filename != DEFAULT_CONFIG:
        # If the the configuration location is not the default and
        # it doesn't exist, quit.
        click.secho(
            f"Configuration file '{configuration_file}' doesn't exist.", err=True
        )
        ctx.exit(-1)
    else:
        # The pyproject.toml file is the configuration file but doesn't exist.
        return


@click.command(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)  # type: ignore
@click.argument(
    "path",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True
    ),
)
@click.option(
    "--glob",
    default="*.conf",
    show_default=True,
    help="Glob pattern to match files in the path with.",
)
@click.option(
    "--prefix",
    default="-> ",
    show_default=True,
    help="Prefix for configuration lines output to the CLI.",
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
    help="The format of the output data (--format json implies --quiet).",
)
@click.option(
    "--select",
    type=str,
    help="Comma-separated list of check names to include"
    " (mutually exclusive with --exclude).",
)
@click.option(
    "--exclude",
    type=str,
    help="Comma-separated list of check names to exclude"
    " (mutually exclusive with --select).",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    default=False,
    type=bool,
    help="Don't output non-errors.",
)
@click.option(
    "--color/--no-color",
    default=True,
    type=bool,
    help="Show colored output.",
    envvar="NO_COLOR",
)
@click.option(
    "-c",
    "--config",
    default="pyproject.toml",
    type=click.Path(file_okay=True, dir_okay=False),
    callback=configure,
    is_eager=True,
    show_default=True,
    help="Path to TOML configuration file.",
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
    select: typing.Optional[str],
    exclude: typing.Optional[str],
    quiet: bool,
    color: bool,
    config: str,
    exit_zero: bool,
) -> None:
    """Perform static analysis on network device configuration files."""
    if select and exclude:
        click.echo("Error: --select and --exclude are mutually exclusive.")
        ctx.exit(-1)

    # Assume the user doesn't want any unnecessary output when outputting JSON
    if format_ == "json":
        quiet = True

    has_errors = False

    checker_instance = Checker()

    configurations: typing.Dict[str, typing.List[str]] = {"default": []}

    input_path = Path(path)
    nos_mapping = {"default": None}
    if input_path.is_file():
        with open(input_path) as f:
            configurations["default"] = f.readlines()
        nos_mapping["default"] = detect_nos(configurations["default"])
    elif input_path.is_dir():
        path_items = input_path.glob(glob)
        for item in path_items:
            dict_key = str(item)
            with open(item) as f:
                configurations[dict_key] = f.readlines()
            nos_mapping[dict_key] = detect_nos(configurations[dict_key])

    if select:
        selected_checks = []
        for check in checker_instance.checks[nos_mapping["default"]]:
            if check.name in select.split(","):
                selected_checks.append(check)
        checker_instance.checks[nos_mapping["default"]] = selected_checks
    elif exclude:
        excluded_checks = []
        # Iterate over each unique NOS
        for nos in set(nos_mapping.values()):
            for check in checker_instance.checks[nos]:
                if check.name in exclude.split(","):
                    excluded_checks.append(check)
        for check in excluded_checks:
            checker_instance.checks[nos_mapping["default"]].remove(check)

    if input_path.is_file():
        processed_config = check_config(
            checker_instance, configurations["default"], nos_mapping["default"]
        )
        if processed_config:
            has_errors = True
        with smart_open(output) as f:
            if format_ == "normal":
                f.write(checks_to_string(processed_config, quiet, color, prefix))
            elif format_ == "json":
                json.dump(processed_config, f)
    elif input_path.is_dir():
        path_items = input_path.glob(glob)
        processed_configs: typing.Dict[str, JSONOutputDict] = {}
        for item in path_items:
            processed_configs[str(item)] = check_config(
                checker_instance, configurations[str(item)], nos_mapping[str(item)]
            )
        if processed_configs:
            has_errors = True
        with smart_open(output) as f:
            if format_ == "normal":
                for key, value in processed_configs.items():
                    if not value:
                        f.write("\n")  # Newline
                        continue
                    f.write(
                        style(
                            f"{'=' * 10} {key} {'=' * 10}\n",
                            quiet=quiet,
                            bold=True,
                        )
                    )
                    f.write(checks_to_string(value, quiet, color, prefix))

            elif format_ == "json":
                json.dump(processed_configs, f)

    if not has_errors and not quiet:
        click.secho("No problems found!", bold=True)

    if has_errors and not exit_zero:
        ctx.exit(-1)
    else:
        ctx.exit(0)


def check_config(
    checker_instance: Checker, configuration: typing.List[str], nos: NOS
) -> JSONOutputDict:
    """Run checks on config at a given path."""
    return_value: JSONOutputDict = {}

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
    check_result_dict: JSONOutputDict, plain: bool, color: bool, prefix: str
) -> str:
    """Convert a check result to its string representation."""
    return_value = ""
    for check, result in check_result_dict.items():
        return_value += style(check, plain, bold=True)
        return_value += " " + result["text"] + "\n"
        return_value += style(
            prefix + prefix.join(result["lines"]),
            plain,
            fg="red" if color else None,
        )
    return return_value


if __name__ == "__main__":
    cli()
