#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <VNF>"
    exit 1
fi

VNF="$1"

declare -A FILE_IDS
FILE_IDS=(
    ["elk_instantiate.json"]="00000000-0000-0000-0000-000000000000"
    ["mysql_instantiate.json"]="00000000-0000-0000-0000-000000000001"
    ["nrf_instantiate.json"]="00000000-0000-0000-0000-000000000002"
    ["udr_instantiate.json"]="00000000-0000-0000-0000-000000000003"
    ["udm_instantiate.json"]="00000000-0000-0000-0000-000000000004"
    ["ausf_instantiate.json"]="00000000-0000-0000-0000-000000000005"
    ["amf_instantiate.json"]="00000000-0000-0000-0000-000000000006"
    ["smf_instantiate.json"]="00000000-0000-0000-0000-000000000007"
    ["upf_instantiate.json"]="00000000-0000-0000-0000-000000000008"
    ["ext_dn_instantiate.json"]="00000000-0000-0000-0000-000000000009"
    ["ueransim_instantiate.json"]="00000000-0000-0000-0000-000000000010"
    ["all_in_one.json"]="00000000-0000-0000-0000-000000000011"
)

ID="${FILE_IDS[${VNF}_instantiate.json]}"

if [ -z "$ID" ]; then
    echo "Error: No ID found for ${VNF}_instantiate.json"
    exit 1
fi

# Set the VIM_ID variable
VIM_ID="cbbc3129-3bb9-423c-be81-86708f12bab6"

JSON_FILE="${VNF}_instantiate.json"
TEMPLATE_FILE="template.json"

if [ ! -f "$JSON_FILE" ]; then
    echo "Error: $JSON_FILE does not exist"
    exit 1
fi

cp "$JSON_FILE" "$TEMPLATE_FILE"
sed -i "s/<VIM_ID>/$VIM_ID/g" "$TEMPLATE_FILE"

# Use the ID in the openstack vnflcm create command
openstack vnflcm create "$ID" --os-tacker-api-version 2
