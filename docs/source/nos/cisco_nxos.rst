CISCO_NXOS
==========

All checks applying to this NOS (including ones applying to multiple).


NXOS101
-------

Check if the telnet feature is explicitly enabled.

**Tags**


* Opinionated
* Security

NXOS102
-------

Check if a routing protocol is actually used - should it be enabled.

**Tags**


* Hygiene

NXOS103
-------

Check if the password strength check has been disabled.

**Tags**


* Opinionated
* Security

NXOS104
-------

Check if any bogus autonomous system is used in the configuration.

**Tags**


* Hygiene

NXOS105
-------

Check if the vPC feature is actually used if it is enabled.

**Tags**


* Hygiene

NXOS106
-------

Check if the LACP feature is actually used if it is enabled.

**Tags**


* Hygiene

NXOS107
-------

Check if the fex feature-set is installed but not enabled.

**Tags**


* Hygiene

NXOS108
-------

Check if any interface in switchport mode fex-fabric has a fex-id associated.

**Tags**


* Hygiene

NXOS109
-------

Check whether an enabled fex feature is actually used.

**Tags**


* Hygiene

NXOS110
-------

Check whether every configured fex id also has an associated interface.

**Tags**


* Hygiene

VAR101
------

Check for presence of default SNMP community strings.

**Tags**


* Security
