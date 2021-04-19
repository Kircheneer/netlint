Getting started
===============

The following section describes how to use ``netlint``.

Configuration
-------------

Configuration is available through

* Command line parameters (see :doc:`/cli`)
* The ``[tool.netlint]`` section of the ``pyproject.toml`` file

  * Available options mirror the command line parameters
  * The config file location is configurable with ``-c/--config``.
    If the name of the config file is not ``pyproject.toml`` the
    ``[netlint]`` section is expected instead

Usage in Python code
--------------------

If you want to integrate ``netlint`` into your Python application,
you need to import the ``Checker`` class from ``netlint.checks.checker``::

  from application import do_stuff

  from netlint.checks.checker import Checker

  configuration = [
    "feature ssh",
    "feature bgp",
    "hostname test.local"
  ]

  checker = Checker()

  checker.run_checks(configuration)

  # Check checker.check_results for the results of the checks
  for check, result in checker.items()
      do_stuff(result)

