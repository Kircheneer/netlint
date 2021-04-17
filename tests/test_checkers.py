import typing
from pathlib import Path

import pytest

from netlint.checks.checker import Checker, Check
from netlint.checks.utils import NOS

CONFIG_DIR = Path(__file__).parent / "configurations"

# Build a list of tuples to allow for precise parametrization of the
# test function.
checks: typing.List[typing.Tuple[NOS, Check]] = []
for nos, check_list in Checker.checks.items():
    for check in check_list:
        checks.append((nos, check))


def name_for_check_parameter(parameter: typing.List[typing.Tuple[NOS, Check]]) -> str:
    """Output nice name for the test naming with `pytest -v`."""
    nos_instance, check_instance = parameter
    return f"{str(nos_instance)}/{check_instance.check_function.__name__}"


@pytest.mark.parametrize("state", ["faulty", "good"])
@pytest.mark.parametrize("check_tuple", checks, ids=name_for_check_parameter)
def test_basic(state: str, check_tuple: typing.List[typing.Tuple[NOS, Check]]):
    """Runs basic tests for checker functions.

    This depends on the Checker class. All checks registered with Checker.register
    will be processed by this test. The process goes as follows:
    -   If the check applies to a single NOS, check
        ``tests/configurations/$NOS/$CHECK_FUNCTION_NAME_(faulty|good).conf``
        for the configuration file.
    -   If the check applies to multiple NOSes, check
        ``tests/configurations/$CHECK_FUNCTION_NAME_(faulty|good).conf``
        for the configuration file.
    -   Read the file, run the check against it, and check whether the output
        corresponds to the state.
    """
    nos_instance, check_instance = check_tuple
    config_suffix = f"_{state}.conf"
    configuration_file = None
    if len(check_instance.apply_to) == 1:
        # If the check only applies to a single NOS, use the NOS specific
        # configurations folder
        configuration_file = (
            CONFIG_DIR
            / str(nos_instance).lower()  # noqa: W503
            / (check_instance.check_function.__name__ + config_suffix)  # noqa: W503
        )
    elif len(check_instance.apply_to) >= 1:
        # If the check applies to multiple NOSes, use the parent configurations folder
        configuration_file = CONFIG_DIR / (
            check_instance.check_function.__name__ + config_suffix
        )
    else:
        AssertionError(
            f"Check {check_instance.check_function.__name__} doesn't apply to any NOS"
        )
    # The checker is ran right here (through the __call__ function of the
    # Checker instance)
    result = check_instance(configuration_file)
    if state == "good":
        assert result is None
    elif state == "faulty":
        assert result is not None
