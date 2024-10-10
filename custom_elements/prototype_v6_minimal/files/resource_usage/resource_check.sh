#!/bin/bash

VNF=$1
OPT=$2
DISABLE_ELK=$3

if [ -z "$VNF" ]; then
    echo "Usage: $0 <vnf_name> [idle|load] [--disable-elk]"
    exit 1
fi

if [ -z "$OPT" ]; then
    OPT="idle"
fi

if [ "$OPT" != "idle" ] && [ "$OPT" != "load" ]; then
    echo "Invalid option: $OPT"
    exit 1
fi

COMMAND="python3 resources_check.py -c $VNF -d 300 -i 5 -n \"$VNF idle\""

if [ "$OPT" == "load" ]; then
    COMMAND="python3 resources_check.py -c $VNF -d 600 -i 5 -n \"$VNF Load\""
fi

if [ "$DISABLE_ELK" == "--disable-elk" ]; then
    COMMAND="$COMMAND --elk-disabled"
fi

eval $COMMAND
