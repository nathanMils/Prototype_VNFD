#!/bin/bash

delete_vnf_descriptors() {
    echo "Deleting all VNF Descriptors..."

    vnfd_ids=$(openstack vnf package list -c Id -f value)

    if [ -n "$vnfd_ids" ]; then
        echo "$vnfd_ids" | while read -r vnfd_id; do
            echo "Disabling and Deleting VNFD $vnfd_id..."
            openstack vnf package update --operational-state DISABLED "$vnfd_id"
            openstack vnf package delete "$vnfd_id"
        done
        echo "All VNF Descriptors deleted."
    else
        echo "No VNF Descriptors found."
    fi
}

delete_vnf_descriptors

echo "All VNF packages and descriptors have been removed."
