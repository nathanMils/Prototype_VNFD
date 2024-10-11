#!/bin/bash

terminate_vnfs() {
    echo "Terminating all VNFs..."
    # List VNF IDs
    vnf_ids=$(openstack vnflcm list --os-tacker-api-version 2 -c ID -f value)

    if [ -n "$vnf_ids" ]; then
        echo "$vnf_ids" | while read -r vnf_id; do
            echo "Terminating VNF $vnf_id..."
            openstack vnflcm terminate --os-tacker-api-version 2 "$vnf_id"
        done
        echo "All VNFs termination requests sent."
        echo "Waiting for VNFs to transition to NOT_INSTANTIATED state..."
        sleep 30  # Adjust this time as necessary for your environment
    else
        echo "No VNFs found."
    fi
}

check_vnfs() {
    echo "Checking all VNFs until they are NOT_INSTANTIATED..."

    while true; do
        all_not_instantiated=true

        vnfs=$(openstack vnflcm list --os-tacker-api-version 2 -c ID -f value)

        if [ -n "$vnfs" ]; then
            echo "$vnfs" | while read -r vnf_id; do
                state=$(openstack vnflcm show --os-tacker-api-version 2 -f value -c Instantiation\ State "$vnf_id")
                echo "VNF $vnf_id is in state: $state"

                if [ "$state" != "NOT_INSTANTIATED" ]; then
                    all_not_instantiated=false
                    echo "VNF $vnf_id is not yet in NOT_INSTANTIATED state."
                fi
            done
        else
            echo "No VNFs found."
            return
        fi

        if [ "$all_not_instantiated" = true ]; then
            echo "All VNFs are now in the NOT_INSTANTIATED state."
            return
        fi

        sleep 10
    done
}


delete_vnfs() {
    echo "Deleting all VNFs..."
    vnf_ids=$(openstack vnflcm list --os-tacker-api-version 2 -c ID -f value)

    if [ -n "$vnf_ids" ]; then
        echo "$vnf_ids" | while read -r vnf_id; do
            echo "Deleting VNF $vnf_id..."
            openstack vnflcm delete --os-tacker-api-version 2 "$vnf_id"
        done
        echo "All VNFs deleted."
    else
        echo "No VNFs found."
    fi
}

# Main script execution
echo "Cleaning up VNFs..."
terminate_vnfs
check_vnfs
delete_vnfs
echo "All VNFs have been removed."
