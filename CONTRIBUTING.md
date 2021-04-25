# Contributing

Thanks for considering a contribution! The following are multiple
ways you could go about your contribution for which you can find
further explanation further below:

- Adding new checks
- Add documentation or tutorials
- Reporting bugs

When contributing any code make sure to run
- flake8
- mypy
- black

on the code and ensure the documentation builds and the tests pass.
A `.pre-commit-config.yaml` configuration file is available if you
want to use git pre-commit hooks.

## Setup

Before you can contribute any code, you will need to set up your
development environment properly by following the instructions
below.

1. **Fork Netlint**. In GitHub, fork the Netlint repository to a new
repository under your name. This will allow you to propose changes
to the main Netlint repository through a pull request. For more
information on how to do this, [refer to GitHub's documentation on how to fork a repository](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo).
2. **Clone Netlint Fork**. Clone your fork of the Netlint repository
into your development environment. [Refer to GitHub's documentation on how to clone a repository](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).
3. **Install Poetry**. Netlint utilizes [Poetry](https://python-poetry.org/)
for Python packaging and dependency management. In order to contribute
code, you will need to follow [Poetry's installation instructions](https://python-poetry.org/docs/#installation)
for your operating system of choice.
4. **Install Dependencies with Poetry**. Use the `poetry install` command
within the clone of your fork of the Netlint repository to install
Netlint's dependencies within your development environment.

Your development environment is now set up to contribute to Netlint!

## Adding new checks

Right now the main thing that is missing is the implementation of
various configuration checks. A good check must have the following
properties:

### Independence from state

A check has to work on just the textual configuration of the device.
It may not depend on any state such as the operative status of an
interface or the up/down status of a routing protocol neighbor.

### Generality

A check must always be applicable to all of its assigned network
operating systems (NOSes) regardless the context.

### Usefulness

A check must always fulfill any of the following use cases:

- Indicate redundant or unused configuration such as a feature that
  is enabled but never used or an access list that is configured but
  never applied
- Indicate a security issue such as leaving telnet enabled

## Write documentation or tutorials

The latest documentation is always present
[here](https://netlint.readthedocs.io). Take a look and see if you can
find any typos, logical issues or unclear passages - contributions of
any size are very welcome.

## Reporting bugs

You can report issues
[here](https://github.com/Kircheneer/netlint/issues/new).