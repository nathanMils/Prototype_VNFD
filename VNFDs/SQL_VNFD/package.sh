#!/bin/bash
set -e

DIR="$(dirname "$(realpath "$0")")"

meta_file_path="$DIR/TOSCA-Metadata/TOSCA.meta"
template_file_path="$DIR/TOSCA-Metadata/TOSCA.template.meta"
zip_file_path="$DIR/vnfd_package.zip"

cp "$template_file_path" "$meta_file_path"

echo "Packaging VNFD..."

if [ -f "$zip_file_path" ]; then
    echo "Removing existing VNFD package zip file..."
    rm "$zip_file_path"
fi

cd "$DIR" || exit

zip -r "$zip_file_path" TOSCA-Metadata/TOSCA.meta Definitions/ BaseHOT/ UserData/

echo "Creating VNF Package..."
VNF_PACKAGE_ID=$(openstack vnf package create -c ID -f value)

echo "Uploading VNFD package..."
openstack vnf package upload --path "$zip_file_path" "$VNF_PACKAGE_ID"

echo "VNFD package uploaded successfully."