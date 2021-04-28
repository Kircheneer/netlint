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
    nos_dir = CONFIG_DIR / str(nos_instance).lower()
    check_name = check_instance.check_function.__name__
    configuration_name_template = "{check}_{state}-{index}.conf"

    # Execute while new configurations files remain (iterating over the index
    # in the filename of the configuration files.
    index = 0
    while True:
        filename = configuration_name_template.format(
            check=check_name, state=state, index=index
        )
        configuration_file = None
        if len(check_instance.apply_to) == 1:
            # If the check only applies to a single NOS, use the NOS specific
            # configurations folder
            configuration_file = nos_dir / filename
        elif len(check_instance.apply_to) >= 1:
            # If the check applies to multiple NOSes, use the parent
            # configurations folder
            configuration_file = CONFIG_DIR / filename
        else:
            AssertionError(f"Check {check_name} doesn't apply to any NOS")

        if not configuration_file.is_file():
            if index == 0:
                # Fail if there is not a single configuration file for any given check
                pytest.fail(
                    f"No configuration file {configuration_file} found for"
                    f"check {check_name}."
                )
            else:
                # If one configuration file was already processed, finish the test
                return

        # The checker is ran right here (through the __call__ function of the
        # Checker instance)
        with open(configuration_file) as f:
            result = check_instance(f.readlines())
        if state == "good":
            assert result is None, f"Failed for {configuration_file.name}"
        elif state == "faulty":
            assert result is not None, f"Failed for {configuration_file.name}"

        index += 1
