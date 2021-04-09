from netlint.checks.checker import Checker

checker_instance: Checker = Checker()

# Import all the checks in order for the decorators to execute
from netlint.checks.cisco_ios import *  # noqa
from netlint.checks.cisco_nxos import *  # noqa
