#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <VNF>"
    exit 1
fi

VNF="$1"

declare -A FILE_IDS
FILE_IDS=(
    ["vnf1_instantiate.json"]="id1"
    ["vnf2_instantiate.json"]="id2"
    ["vnf3_instantiate.json"]="id3"
)

ID="${FILE_IDS[${VNF}_instantiate.json]}"

if [ -z "$ID" ]; then
    echo "Error: No ID found for ${VNF}_instantiate.json"
    exit 1
fi

# Set the VIM_ID variable
VIM_ID="your_vim_id_here"

JSON_FILE="${VNF}_instantiate.json"
TEMPLATE_FILE="template.json"

if [ ! -f "$JSON_FILE" ]; then
    echo "Error: $JSON_FILE does not exist"
    exit 1
fi

cp "$JSON_FILE" "$TEMPLATE_FILE"
sed -i "s/<VIM_ID>/$VIM_ID/g" "$TEMPLATE_FILE"

# Use the ID in the openstack vnflcm instantiate command
openstack vnflcm instantiate "$ID" ./template.json --os-tacker-api-version 2