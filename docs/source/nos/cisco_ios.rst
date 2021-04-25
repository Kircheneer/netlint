CISCO_IOS
=========

All checks applying to this NOS (including ones applying to multiple).


IOS101
------

Check if there are any plaintext passwords in the configuration.

**Tags**


* Security

IOS102
------

Check if the http server is enabled.

**Tags**


* Opinionated
* Security

IOS103
------

Check for authentication on the console line.

**Tags**


* Opinionated
* Security

IOS104
------

Check if strong password hash algorithms were used.

**Tags**


* Security

IOS105
------

Check if the switchport mode matches all config commands per interface.

**Tags**


* Hygiene

IOS106
------

Check for any ACLs that are used but never configured.

    Potential usages are:

    * Packet filtering
    * Rate limiting
    * Route maps
    

**Tags**


* Hygiene
* Security

IOS107
------

Check for any ACLs that are configured but never used.

    Potential usages are:

    * Packet filtering
    * Rate limiting
    * Route maps
    

**Tags**


* Hygiene

IOS108
------

Check if the switchport mode matches all config commands per interface.

**Tags**


* Hygiene

VAR101
------

Check for presence of default SNMP community strings.

**Tags**


* Security
