#!/bin/bash

set -e  # Exit on error

# Function to calculate SHA-256 hash of a file
calculate_sha256() {
    local file_path=$1
    sha256sum "$file_path" | awk '{ print $1 }'
}

# Function to replace placeholders in TOSCA.meta
replace_hashes_in_meta() {
    local meta_file_path=$1
    shift
    local hashes=("$@")

    local content
    content=$(<"$meta_file_path")

    for hash_entry in "${hashes[@]}"; do
        local script_name
        local hash_value
        script_name=$(echo "$hash_entry" | cut -d':' -f1)
        hash_value=$(echo "$hash_entry" | cut -d':' -f2)
        local placeholder="<${script_name^^}_HASH>"
        content=$(echo "$content" | sed "s|$placeholder|$hash_value|g")
    done

    echo "$content" > "$meta_file_path"
}

# Main script
scripts_dir='Scripts'
definitions_dir='Definitions'
meta_file_path='TOSCA-Metadata/TOSCA.meta'
tosca_version='v2.1.6'
script_files=(
    'configure_main.sh'
    'configure_prototype.sh'
    'configure_network_function.sh'
    'configure_suricata.sh'
)

hashes=()
for script_file in "${script_files[@]}"; do
    file_path="$scripts_dir/$script_file"
    hash_value=$(calculate_sha256 "$file_path")
    hashes+=("$script_file:$hash_value")
done

replace_hashes_in_meta "$meta_file_path" "${hashes[@]}"

# Download etsi nfv sol001 definitions for VNFD
wget -P "$definitions_dir" https://forge.etsi.org/rep/nfv/SOL001/raw/${tosca_version}/etsi_nfv_sol001_common_types.yaml
wget -P "$definitions_dir" https://forge.etsi.org/rep/nfv/SOL001/raw/${tosca_version}/etsi_nfv_sol001_vnfd_types.yaml

# Zip final VNFD package
zip -r vnfd_package.zip TOSCA-Metadata/ Definitions/ BaseHOT/ Files/ Scripts/ UserData/
