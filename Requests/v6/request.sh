#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <VNF> --elk-enabled|--elk-disabled"
    exit 1
fi

VNF="$1"
ELK_OPTION="$2"

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
VIM_ID=$(openstack vim list -c ID -f value | head -n 1)

JSON_FILE="${VNF}_instantiate.json"
TEMPLATE_FILE="template.json"

if [ ! -f "$JSON_FILE" ]; then
    echo "Error: $JSON_FILE does not exist"
    exit 1
fi

cp "$JSON_FILE" "$TEMPLATE_FILE"
sed -i "s/<VIM_ID>/$VIM_ID/g" "$TEMPLATE_FILE"

if [ "$ELK_OPTION" == "--elk-enabled" ]; then
    sed -i "s/<TYPE>/v6/g" "$TEMPLATE_FILE"
elif [ "$ELK_OPTION" == "--elk-disabled" ]; then
    sed -i "s/<TYPE>/v6_elk_disabled/g" "$TEMPLATE_FILE"
else
    echo "Error: Invalid option $ELK_OPTION"
    exit 1
fi

echo "Creating VNF instance..."
VNF_ID = (openstack vnflcm create "$ID" --os-tacker-api-version 2 -c ID -f value)

echo "Waiting for 3 seconds before instantiating..."
sleep 3

echo "Instantiating VNF..."
openstack vnflcm instantiate $ID ./template.json --os-tacker-api-version 2


