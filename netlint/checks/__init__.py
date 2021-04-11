"""The actual checking logics as well as checks are implemented in this module."""

# Import all the checks in order for the decorators to execute
from netlint.checks.cisco_ios import *  # noqa
from netlint.checks.cisco_nxos import *  # noqa
from netlint.checks.various import *  # noqa
