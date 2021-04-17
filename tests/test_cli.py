import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from netlint.main import cli

TESTS_DIR = Path(__file__).parent


@pytest.mark.parametrize("quiet", [True, False])
@pytest.mark.parametrize("format_", ["normal", "json"])
def test_lint_basic(quiet: bool, format_: str):
    """Basic test for CLI linting functionality."""
    runner = CliRunner()

    cisco_ios_faulty_conf = TESTS_DIR / "configurations" / "cisco_ios" / "faulty.conf"

    commands = [str(cisco_ios_faulty_conf)]

    if quiet:
        commands.insert(0, "--quiet")
    commands.extend(["--format", format_])
    result = runner.invoke(cli, commands)

    # Assert the result contains an error
    if not result.exception:
        raise AssertionError("The result should contain errors here.")
    elif type(result.exception) != SystemExit:
        raise result.exception

    # Check for ANSI escape codes in the output if --quiet is set
    if quiet:
        assert "\x1b" not in result.output

    if format_ == "json":
        result = json.loads(result.output)
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
        cli, [str(cisco_ios_faulty_conf), "--select", "ABC", "--exclude", "XYZ"]
    )

    assert "mutually exclusive" in result.stdout
    assert result.exception
