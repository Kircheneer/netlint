Oxidized hooks
==============

This document describes how to integrate `Oxidized <https://github.com/ytti/oxidized>`_ with ``netlint``.

.. NOTE::
   This tutorial assumes that you are using oxidized with git-based storage rather than file-based storage.

Installation
------------

#. Create a folder to keep the hooks in. For the purposes of this example that shall be ``/opt/nettools/``.
#. Copy ``contrib/oxidized/cfgchanged.sh`` and ``contrib/oxidized/validate_config.sh`` to said folder and make sure they
   are executable.

Configuration
-------------

#. In the oxidized config file ``.config/oxidized/config`` add the following to fire ``/opt/nettools/cfgchanged.sh`` on
   every config change oxidized finds in it's targets::

     hooks:
       conf_changed:
         type: exec
         events: [post_store]
         cmd: '/opt/nettools/cfgchanged.sh $OX_EVENT $OX_NODE_NAME $OX_NODE_IP $OX_NODE_FROM $OX_NODE_MSG $OX_NODE_GROUP $OX_NODE_MODEL $OX_JOB_STATUS $OX_JOB_TIME $OX_REPO_COMMITREF $OX_REPO_NAME'
#. Change the output folder in ``validate_config.sh`` to the folder want the linting reports in.

.. DANGER::
   Any old reports will be overwritten.

Now whenever oxidized detects a config change, the ``/opt/nettools/cfgchanged.sh`` script is executed.
It also calls the ``validate_config.sh`` script in that same folder, with two parameters:

- The full name of the device config.
- The device type as defined in oxidized.

This leaves you with (assuming you did not alter paths):

- Most recent configuration files in ``/opt/nettools/data/`` (the tree structure below depends upon the oxidized config).
- Lint reports in ``$HOME/lint-reports``.
