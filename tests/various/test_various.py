from pathlib import Path

import pytest

from netlint.checks import various
from tests.utils import get_method

CONFIG_DIR = Path(__file__).parent / "configurations"
CHECKS = [method for method in dir(various) if method.startswith("check")]


@pytest.mark.parametrize("check", CHECKS)
def test_basic_faulty(check: str):
    configuration = CONFIG_DIR / (check + "_faulty.conf")
    method = get_method(check, various)
    if not method:
        return
    bad_result = method(configuration)
    assert bad_result is not None


@pytest.mark.parametrize("check", CHECKS)
def test_basic_good(check: str):
    configuration = CONFIG_DIR / (check + "_good.conf")
    method = get_method(check, various)
    if not method:
        return
    good_result = method(configuration)
    assert good_result is None
