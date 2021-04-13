#!/bin/bash
#
# Hook for oxidized to initate validation after a changed config is stored
# 
# $OX_EVENT
# $OX_NODE_NAME
# $OX_NODE_IP
# $OX_NODE_FROM
# $OX_NODE_MSG
# $OX_NODE_GROUP
# $OX_NODE_MODEL
# $OX_JOB_STATUS
# $OX_JOB_TIME
# $OX_REPO_COMMITREF
# $OX_REPO_NAME

Storage="data"
MyPath=`dirname $0`
FilePath="$MyPath/$Storage/$OX_NODE_GROUP"
GitCmd=`which git`

# Clone the last version of the config
if [ -d "$FilePath" ]; then
  # Pull
  cd "$FilePath" && $GitCmd pull
else
  # Clone
  mkdir -p $FilePath
  $GitCmd clone "$OX_REPO_NAME" "$FilePath"
fi

# No run the validator
$MyPath/validate_config.sh  "$MyPath/$Storage/$OX_NODE_GROUP/$OX_NODE_NAME" "$OX_NODE_MODEL"
