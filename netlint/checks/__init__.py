from netlint.checks import cisco_ios, cisco_nxos
from netlint.checks.checker import Checker, CheckFunctionTuple

checker = Checker()

# IOS
checker.register(
    CheckFunctionTuple(name="A101", function=cisco_ios.check_console_password),
    apply_to=["cisco_ios"],
)
checker.register(
    CheckFunctionTuple(name="A102", function=cisco_ios.check_ip_http_server),
    apply_to=["cisco_ios"],
)
checker.register(
    CheckFunctionTuple(name="A103", function=cisco_ios.check_plaintext_passwords),
    apply_to=["cisco_ios"],
)

# NXOS
checker.register(
    CheckFunctionTuple(name="B101", function=cisco_nxos.check_telnet_enabled),
    apply_to=["cisco_nxos"],
)
checker.register(
    CheckFunctionTuple(name="B102", function=cisco_nxos.check_bgp_enabled_and_used),
    apply_to=["cisco_nxos"],
)
