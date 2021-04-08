**Note: Still in active development - don't use this**

# Netlint

Performs static analysis on network device configuration files.

Linters have long since been a standard way of assessing code quality
in the software development world. This project aims to take that idea
and apply it to the world of network device configuration files.

## Example usage

Below is an example of how to use this based on one of the faulty test
configurations:

```
$ netlint --nos cisco_ios ./tests/cisco_ios/configurations/faulty.conf
A101 Console line unauthenticated
-> line con 0
A102 HTTP server not disabled
-> ip http server
-> ip http secure-server
A103 Plaintext user passwords in configuration.
-> username test password ing
```