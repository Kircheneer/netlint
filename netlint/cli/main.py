"""CLI entrypoint to netlint."""
import csv
import json
import os
import typing
from pathlib import Path

import click
import napalm  # type: ignore
import toml
from rich.console import Console

from netlint.checks.checker import Checker
from netlint.checks.utils import NOS, detect_nos, Tag
from netlint.cli.types import JSONOutputDict
from netlint.cli.utils import smart_open, style, optional

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


@click.group(
    invoke_without_command=True, context_settings=CONTEXT_SETTINGS, no_args_is_help=True
)  # type: ignore
@click.option(
    "-i",
    "--input",
    "input_path",
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
    type=click.Choice(["json", "normal", "csv"]),
    help="The format of the output data.",
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
    "--exclude-tags", type=str, help="Comma-separated list of check tags to exclude."
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
    "-p", "--plain", is_flag=True, default=False, type=bool, help="Plain output."
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
    input_path: typing.Optional[str],
    glob: str,
    prefix: str,
    output: typing.Optional[str],
    format_: str,
    select: typing.Optional[str],
    exclude: typing.Optional[str],
    exclude_tags: typing.Optional[str],
    quiet: bool,
    color: bool,
    plain: bool,
    config: str,
    exit_zero: bool,
) -> None:
    """Perform static analysis on network device configuration files."""
    ctx.ensure_object(dict)

    if select and exclude:
        click.echo("Error: --select and --exclude are mutually exclusive.")
        ctx.exit(-1)

    # Assume the user doesn't want any unnecessary output when not outputting
    # normally or outputting to a file.
    if format_ != "normal" or output:
        quiet = True
        plain = True

    # Save the settings into the context
    ctx.obj["quiet"] = quiet
    ctx.obj["plain"] = plain
    ctx.obj["color"] = color
    ctx.obj["prefix"] = prefix
    ctx.obj["output"] = output
    ctx.obj["format"] = format_
    ctx.obj["input_path"] = input_path
    ctx.obj["checker"] = Checker()
    ctx.obj["console"] = Console()

    # Abort execution of the group if there is a subcommand
    if ctx.invoked_subcommand is not None:
        return

    has_errors = False

    configurations: typing.Dict[str, typing.List[str]] = {"default": []}

    if not input_path:
        click.echo(
            "Error: You need to pass -i/--input if you aren't using a"
            "subcommand to supply the configuration."
        )
        ctx.exit(1)

    path = Path(input_path)

    nos_mapping: typing.Dict[str, NOS] = {}
    if path.is_file():
        with open(path) as f:
            configurations["default"] = f.readlines()
        nos_mapping["default"] = detect_nos(configurations["default"])
    elif path.is_dir():
        path_items = path.glob(glob)
        for item in path_items:
            dict_key = str(item)
            with open(item) as f:
                configurations[dict_key] = f.readlines()
            nos_mapping[dict_key] = detect_nos(configurations[dict_key])

    excluded_tags = set()
    try:
        if exclude_tags:
            excluded_tags = {Tag[name.upper()] for name in exclude_tags.split(",")}
    except KeyError as e:
        click.echo(f"Error: Unknown tag key {e}. Aborting.", err=True)
        ctx.exit(1)
    if select or exclude or excluded_tags:
        selected_checks = []
        excluded_checks = []
        checks_to_select = frozenset(select.split(",")) if select else set()
        checks_to_exclude = frozenset(exclude.split(",")) if exclude else set()
        for nos in set(nos_mapping.values()):
            for check in ctx.obj["checker"].checks[nos]:
                if check.name in checks_to_select:
                    selected_checks.append(check)
                elif (
                    excluded_tags.intersection(check.tags)
                    or check.name in checks_to_exclude
                ):
                    excluded_checks.append(check)
            if checks_to_select:
                ctx.obj["checker"].checks[nos] = selected_checks
            for check in excluded_checks:
                if check in ctx.obj["checker"].checks[nos]:
                    ctx.obj["checker"].checks[nos].remove(check)

    if path.is_file():
        processed_config = check_config(
            ctx.obj["checker"], configurations["default"], nos_mapping["default"]
        )
        if processed_config:
            has_errors = True
        write_output(ctx, processed_config)
    elif path.is_dir():
        path_items = path.glob(glob)
        processed_configs: typing.Dict[str, JSONOutputDict] = {}
        for item in path_items:
            processed_configs[str(item)] = check_config(
                ctx.obj["checker"], configurations[str(item)], nos_mapping[str(item)]
            )
        if processed_configs:
            has_errors = True
        newline = "" if format_ == "csv" else os.linesep
        with smart_open(output, newline=newline) as f:
            if format_ == "normal":
                for key, value in processed_configs.items():
                    f.write(
                        style(
                            f"{'=' * 10} {key}\n",
                            plain=plain,
                            bold=True,
                        )
                    )
                    results_as_string = checks_to_string(value, plain, color, prefix)
                    if results_as_string:
                        f.write(results_as_string)
                    elif not quiet:
                        click.secho("No problems found!", bold=not plain)
            elif format_ == "json":
                json.dump(processed_configs, f)
            elif format_ == "csv":
                writer = csv.writer(f)
                # Find every unique check that is not filtered
                all_checks: typing.List[str] = []
                for checks in ctx.obj["checker"].checks.values():
                    all_checks.extend(map(lambda c: c.name, checks))
                sorted_unique_checks = sorted(set(all_checks))
                writer.writerow(["Device"] + sorted_unique_checks)

                for key, value in processed_configs.items():
                    row = [key]
                    row.extend(["Passed"] * len(sorted_unique_checks))
                    for name, result in value.items():
                        if result:
                            index = sorted_unique_checks.index(name)
                            row[index + 1] = "Failed"
                    writer.writerow(row)

    if not has_errors and not quiet:
        click.secho("No problems found!", bold=not plain)

    if has_errors and not exit_zero:
        ctx.exit(-1)
    else:
        ctx.exit(0)


@cli.command()
@click.pass_context
@click.option(
    "-d",
    "--driver",
    "driver_name",
    type=str,
    help="Name of the NAPALM driver to connect with.",
)
@click.option("-u", "--username", prompt=True)
@click.option("-p", "--password", prompt=True, hide_input=True)
@click.argument("hostname", type=str)
def get(
    ctx: click.Context, driver_name: str, username: str, password: str, hostname: str
) -> None:
    """Get live configuration off of devices."""
    driver = napalm.get_network_driver(driver_name)
    status_color = "[bold green]" if ctx.obj["color"] else ""
    with optional(
        not ctx.obj["plain"] or ctx.obj["quiet"],
        ctx.obj["console"].status(f"{status_color}Retrieving the configuration..."),
    ) as _:
        with driver(
            hostname=hostname, username=username, password=password
        ) as connection:
            configuration = connection.get_config(retrieve="running")["running"]
    processed_config = check_config(
        ctx.obj["checker"], configuration.splitlines(), NOS.from_napalm(driver_name)
    )

    write_output(ctx, processed_config)

    if not processed_config and not ctx.obj["quiet"]:
        click.secho("No problems found!\n", bold=not ctx.obj["plain"])


def write_output(ctx: click.Context, processed_config: JSONOutputDict) -> None:
    """Write the output for a processed configuration.

    :param ctx: The click context where ctx.obj contains the necessary settings.
    :param processed_config: The Check output dictionary.
    :return: None
    """
    newline = "" if ctx.obj["format"] == "csv" else os.linesep
    with smart_open(ctx.obj["output"], newline=newline) as f:
        if ctx.obj["format"] == "normal":
            f.write(
                checks_to_string(
                    processed_config,
                    ctx.obj["plain"],
                    ctx.obj["color"],
                    ctx.obj["prefix"],
                )
            )
        elif ctx.obj["format"] == "json":
            json.dump(processed_config, f)
        elif ctx.obj["format"] == "csv":
            writer = csv.writer(f)
            headers = ["Device"]
            headers.extend(processed_config.keys())
            writer.writerow(headers)
            values = [ctx.obj["input_path"]]
            values.extend(
                ["Failed" if value else "Passed" for value in processed_config.values()]
            )
            writer.writerow(values)


def check_config(
    checker_instance: Checker, configuration: typing.List[str], nos: NOS
) -> JSONOutputDict:
    """Run checks on config at a given path."""
    return_value: JSONOutputDict = {}

    results = checker_instance.run_checks(configuration, nos)

    for check, result in results.items():
        if not result:
            return_value[check] = None
        else:
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
        if not result:
            continue
        lines = [line.strip() for line in result["lines"]]
        return_value += style(check, plain, bold=True)
        return_value += " " + result["text"] + "\n"
        return_value += style(
            prefix + f"\n{prefix}".join(lines),
            plain,
            fg="red" if color else None,
        )
        return_value += "\n"
    return return_value


if __name__ == "__main__":
    cli(obj={})
