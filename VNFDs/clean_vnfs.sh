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
        # Assume all VNFs are NOT_INSTANTIATED at the start of each iteration
        all_not_instantiated=true

        # Get the list of VNF IDs
        vnfs=$(openstack vnflcm list --os-tacker-api-version 2 -c ID -f value)

        # Check if there are any VNFs
        if [ -n "$vnfs" ]; then
            # Loop through each VNF ID
            echo "$vnfs" | while read -r vnf_id; do
                # Get the instantiation state of the VNF
                state=$(openstack vnflcm show --os-tacker-api-version 2 -f value -c Instantiation\ State "$vnf_id")
                echo "VNF $vnf_id is in state: $state"

                # If any VNF is not in NOT_INSTANTIATED state, set the flag to false
                if [ "$state" != "NOT_INSTANTIATED" ]; then
                    all_not_instantiated=false
                    echo "VNF $vnf_id is not yet in NOT_INSTANTIATED state."
                fi
            done
        else
            echo "No VNFs found."
            return
        fi

        # If all VNFs are NOT_INSTANTIATED, exit the loop
        if [ "$all_not_instantiated" = true ]; then
            echo "All VNFs are now in the NOT_INSTANTIATED state."
            return
        fi

        # Wait before checking again
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
