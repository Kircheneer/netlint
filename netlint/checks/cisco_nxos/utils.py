"""Utilities for NXOS checks."""

import typing

from netlint.checks.types import CheckResult
from netlint.checks.utils import NetlintConfParse


def _feature_enabled_but_not_configured(
    config: NetlintConfParse,
    feature_regex: str,
    configured_regex: str,
    failure_text: str,
) -> typing.Optional[CheckResult]:
    """Wrap common code for feature_enabled_and_used type checks."""
    feature_enabled = config.find_lines(feature_regex)
    feature_configured = config.find_lines(configured_regex)
    if feature_enabled and not feature_configured:
        return CheckResult(
            text=failure_text,
            lines=feature_enabled + feature_configured,
        )
    return None
