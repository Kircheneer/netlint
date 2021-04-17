**Note: Still in active development and potentially subject to major changes - keep this in mind when using this.**

# Netlint

![Build workflog](https://github.com/Kircheneer/netlint/actions/workflows/main.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/netlint/badge/?version=latest)](https://netlint.readthedocs.io/en/latest/?badge=latest)

Performs static analysis on network device configuration files.

Linters have long since been a standard way of assessing code quality
in the software development world. This project aims to take that idea
and apply it to the world of network device configuration files.

Find the latest copy of the documentation [here](https://netlint.readthedocs.io).

Potential uses of this tool are

- Linting network device configurations generated in
  CI/CD automation pipelines
- Assistance when building out new configurations for
  both traditional and automated deployment
- Basic security auditing of configuration files

## Example usage

Below is an example of how to use this based on one of the faulty test
configurations (executed from the project root):

```
$  netlint tests/configurations/cisco_ios/faulty.conf
IOS101 Plaintext user passwords in configuration.
-> username test password ing
IOS102 HTTP server not disabled
-> ip http server
-> ip http secure-server
IOS103 Console line unauthenticated
-> line con 0

```

## Installation

There are multiple ways of installing this software.

A package is available on [PyPI](https://pypi.org/project/netlint/),
therefore you can simply install with `pip install netlint` and
then simply run `netlint`.

If you prefer to install directly from
GitHub, here is how you would go about that.

```bash
$ git clone https://github.com/Kircheneer/netlint.git
$ cd netlint
$ pip install .
$ netlint --help
Usage: netlint [OPTIONS] COMMAND [ARGS]...

  Lint network device configuration files.

  [...]
```
