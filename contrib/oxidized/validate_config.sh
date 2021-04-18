#!/bin/bash
# 
# Initate a config check
# 
# arguments: filename  oxidixed_modelname
#

ReportDir="$HOME/lint-reports"

mkdir -p "$ReportDir"
cfgfile=`basename $1`
netlint -o "$ReportDir/$cfgfile.rpt" -i $1
