Implementing checks
===================

This section explains how to implement checks. This can be both applied
to development in the core ``netlint`` repository as well as external
collections of checks.

Implementation
--------------

The ``Checker`` class implements a decorator to decorate checks
with. That decorator does two things:

* Register the check with the ``Checker`` class
* Append metadata from the decorator to the docstring of check

In practice that might look like this::

  from netlint.checks.checker import Checker, CheckResult

  @Checker.register(apply_to=["NOS_A", "NOS_B"], name="NOS_A101, tags={Tag.Hygiene})
  def check_example(
      configuration: typing.List[str]
  ) -> typing.Optional[CheckResult]:
      for line in configuration:
          if "bad_thing" in line:
              return CheckResult(
                  text="Found bad thing in the configuration",
                  lines=[line]
              )
      return None

Tests
-----

Your new checker will automatically be registered for the basic
pytest test. Put at least one configuration that does not contain
the thing your are checking for at
``tests/configurations/$NOS/$CHECK_NAME_good-0.conf``
and one that does contain it at
``tests/configurations/$NOS/$CHECK_NAME_faulty-0.conf``.
Feel free to add more each time incrementing the index at the end
so that all files are tested against.

.. NOTE::
   If your check has ``apply_to`` set to more than one NOS, put
   the configuration files directly at ``tests/configurations``.

