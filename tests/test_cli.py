import csv
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from netlint.cli.main import cli

TESTS_DIR = Path(__file__).parent


@pytest.mark.parametrize("plain", [True, False])
@pytest.mark.parametrize("format_", ["normal", "json", "csv"])
def test_lint_basic(plain: bool, format_: str):
    """Basic test for CLI linting functionality."""
    runner = CliRunner()

    cisco_ios_faulty_conf = TESTS_DIR / "configurations" / "cisco_ios" / "faulty.conf"

    commands = ["-i", str(cisco_ios_faulty_conf)]

    if plain:
        commands.insert(0, "--plain")
    commands.extend(["--format", format_])
    result = runner.invoke(cli, commands)

    # Assert the result contains an error
    if not result.exception:
        raise AssertionError("The result should contain errors here.")
    elif type(result.exception) != SystemExit:
        raise result.exception

    # Check for ANSI escape codes in the output if --quiet is set
    if plain:
        assert "\x1b" not in result.output

    if format_ == "json":
        result = json.loads(result.output)
        assert result
    elif format_ == "csv":
        result = list(csv.reader(result.output))
        assert result

    # Test if the result no longer contains an error with --exit-zero
    commands.append("--exit-zero")
    result = runner.invoke(cli, commands)
    assert not result.exception


def test_select_exclude_exclusivity():
    """Test that --select and --exclude don't work together each other."""
    runner = CliRunner()

    cisco_ios_faulty_conf = TESTS_DIR / "configurations" / "cisco_ios" / "faulty.conf"

    result = runner.invoke(
        cli, ["-i", str(cisco_ios_faulty_conf), "--select", "ABC", "--exclude", "XYZ"]
    )

    assert "mutually exclusive" in result.stdout
    assert result.exception


def test_config_file_not_found():
    """Assert an exception is raised for a non-existant config file."""
    runner = CliRunner()

    result = runner.invoke(cli, ["-c", "non-existent.toml"])

    assert isinstance(result.exception, SystemExit)


def test_input_dir():
    """Test if passing a dictionary for -i works."""
    runner = CliRunner()

    result = runner.invoke(
        cli, ["-i", str(TESTS_DIR / "configurations"), "--exit-zero"]
    )

    assert not result.exception, result.exception


def test_select_exclude(tmpdir: Path):
    """Test if the --select/--exclude options works correctly."""
    runner = CliRunner()

    config_file = tmpdir / "test.conf"

    with open(config_file, "w") as f:
        f.writelines(["ip http server"])

    commands = ["-i", str(tmpdir), "--exclude", "IOS101", "--exit-zero"]

    result = runner.invoke(cli, commands)

    assert not result.exception

    commands = ["-i", str(tmpdir), "--select", "IOS102", "--exit-zero"]

    result = runner.invoke(cli, commands)

    assert not result.exception

    commands = ["-i", str(tmpdir), "--exclude-tags", "security", "--exit-zero"]

    result = runner.invoke(cli, commands)

    assert not result.exception
