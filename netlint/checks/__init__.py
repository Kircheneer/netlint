from netlint.checks import cisco_ios
from netlint.checks.checker import Checker

checker = Checker()

checker.register("A101", cisco_ios.check_console_password)
checker.register("A102", cisco_ios.check_ip_http_server)
checker.register("A103", cisco_ios.check_plaintext_passwords)
