#!/bin/bash

VNF=$1
OPT=$2

if [ -z "$VNF" ]; then
    echo "Usage: $0 <vnf_name> [idle|load]"
    exit 1
fi

if [ -z "$OPT" ]; then
    OPT="idle"
fi

if [ "$OPT" != "idle" ] && [ "$OPT" != "load" ]; then
    echo "Invalid option: $OPT"
    exit 1
fi

if [ "$OPT" == "idle" ]; then
    python3 resource_check.py -c $VNF -d 300 -i 5 -n "$VNF idle" --zapier-webhook "https://hooks.zapier.com/hooks/catch/20350848/2mcrrua/"
elif [ "$OPT" == "load" ]; then
    python3 resource_check.py -c $VNF -d 600 -i 5 -n "$VNF Load" --zapier-webhook "https://hooks.zapier.com/hooks/catch/20350848/2mcrrua/"
fi