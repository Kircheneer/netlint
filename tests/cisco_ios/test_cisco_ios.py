from pathlib import Path

import pytest
from ciscoconfparse import CiscoConfParse

from netlint.checks import cisco_ios

CONFIG_DIR = Path(__file__).parent / "configurations"
CHECKS = [method for method in dir(cisco_ios) if method.startswith("check")]



@pytest.fixture
def faulty_conf() -> CiscoConfParse:
    with open(CONFIG_DIR / "faulty.conf") as f:
        return CiscoConfParse(f.readlines())


@pytest.fixture
def good_conf() -> CiscoConfParse:
    with open(CONFIG_DIR / "good.conf") as f:
        return CiscoConfParse(f.readlines())


@pytest.mark.parametrize("check", CHECKS)
def test_check_callable(check: str):
    method = getattr(cisco_ios, check)
    assert callable(method), f"Method {method} is not callable"


@pytest.mark.parametrize("check", CHECKS)
def test_basic_faulty(check: str, faulty_conf: CiscoConfParse):
    method = getattr(cisco_ios, check)
    bad_result = method(faulty_conf)
    assert bad_result is not None


@pytest.mark.parametrize("check", CHECKS)
def test_basic_good(check: str, good_conf: CiscoConfParse):
    method = getattr(cisco_ios, check)
    good_result = method(good_conf)
    assert good_result is None
