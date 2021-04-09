from netlint.checks.checker import Checker, CheckResult

checker = Checker()

# Import all the checks in order for the decorators to execute
from netlint.checks.cisco_ios import *
from netlint.checks.cisco_nxos import *
