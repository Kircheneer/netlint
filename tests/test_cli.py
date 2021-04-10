from pathlib import Path

import pytest
from click.testing import CliRunner

from netlint.main import cli

TESTS_DIR = Path(__file__).parent


def test_list():
    """Smoke test to test the list command of the CLI."""
    runner = CliRunner()

    runner.invoke(cli, ["list"])


@pytest.mark.parametrize("plain", [True, False])
def test_lint_basic(plain: bool):
    """Basic test for CLI linting functionality."""
    runner = CliRunner()

    cisco_ios_faulty_conf = TESTS_DIR / "cisco_ios" / "configurations" / "faulty.conf"

    commands = ["lint", "--nos", "cisco_ios", str(cisco_ios_faulty_conf)]

    if plain:
        commands.insert(0, "--plain")
    result = runner.invoke(cli, commands)

    # Assert the result did not error
    assert (
        not result.exception
    ), f"netlint {' '.join(commands)} produced: {result.stdout}"

    # Check for ANSI escape codes in the output if --plain is set
    if plain:
        assert "\x1b" not in result.output
