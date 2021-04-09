import typing
from pathlib import Path

import pytest

from netlint.checks import cisco_nxos
from tests.utils import get_method

CONFIG_DIR = Path(__file__).parent / "configurations"
CHECKS = [method for method in dir(cisco_nxos) if method.startswith("check")]


@pytest.fixture
def faulty_conf() -> typing.List[str]:
    with open(CONFIG_DIR / "faulty.conf") as f:
        return f.readlines()


@pytest.fixture
def good_conf() -> typing.List[str]:
    with open(CONFIG_DIR / "good.conf") as f:
        return f.readlines()


@pytest.mark.parametrize("check", CHECKS)
def test_basic_faulty(check: str, faulty_conf: typing.List[str]):
    method = get_method(check, cisco_nxos)
    if not method:
        return
    bad_result = method(faulty_conf)
    assert bad_result is not None


@pytest.mark.parametrize("check", CHECKS)
def test_basic_good(check: str, good_conf: typing.List[str]):
    method = get_method(check, cisco_nxos)
    if not method:
        return
    good_result = method(good_conf)
    assert good_result is None
