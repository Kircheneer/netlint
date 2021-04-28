**Note: Still in active development and potentially subject to major changes - keep this in mind when using this.**

# Netlint

![Build workflow](https://github.com/Kircheneer/netlint/actions/workflows/main.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/netlint/badge/?version=latest)](https://netlint.readthedocs.io/en/latest/?badge=latest)

Performs static analysis on network device configuration files.

Linters have long since been a standard way of assessing code quality
in the software development world. This project aims to take that idea
and apply it to the world of network device configuration files.

Find the latest copy of the documentation [here](https://netlint.readthedocs.io).

## Example usage

Below is an example of how to use this based on one of the faulty test
configurations (executed from the project root):

```
$  netlint -i tests/configurations/cisco_ios/faulty.conf
IOS101 Plaintext user passwords in configuration.
-> username test password ing
IOS102 HTTP server not disabled
-> ip http server
-> ip http secure-server
IOS103 Console line unauthenticated
-> line con 0

```

## Scope

Some potential use cases of `netlint` are the following:

- Linting network device configurations generated in
  CI/CD automation pipelines
- Assistance when building out new configurations for
  both traditional and automated deployment
- Basic security auditing of configuration files
- Validating configuration hygiene such as references to
undefined configuration items (e.g. ACLs)

The following things are explicitly not in scope of `netlint`:

- Correlation of configurations (for example answering the question of
whether two BGP neighbors might come up or not)
- Validation of syntactic configuration correctness
- Analysis of network device state that requires connections to the
devices such as interface error counters (`netlint` does however
support getting the configuration from the devices with `netlint get`)

## Installation

There are multiple ways of installing this software.

A package is available on [PyPI](https://pypi.org/project/netlint/),
therefore you can simply install with `pip install netlint` and
then simply run `netlint`.

If you prefer to install directly from
GitHub, here is how you would go about that.

```bash
$ git clone https://github.com/Kircheneer/netlint.git
$ git checkout $TAG  # Optionally checkout a specific tag
$ cd netlint
$ pip install .
$ netlint --help
Usage: netlint [OPTIONS] COMMAND [ARGS]...

  Lint network device configuration files.

  [...]
```
