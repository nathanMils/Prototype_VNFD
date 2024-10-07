#!/bin/bash

# Function to get Docker container resource usage
get_docker_usage() {
    local vnf=$1
    local stats=$(sudo docker stats --no-stream --format "{{.CPUPerc}} {{.MemUsage}}" "$vnf")
    echo "$stats"
}

# Function to get Zeek resource usage
get_zeek_usage() {
    ps -o %cpu,%mem -C zeek | awk 'NR==1{printf "%.1f %.1f\n", $1, $2}'
}

# Function to get Filebeat resource usage
get_filebeat_usage() {
    ps -o %cpu,%mem -C filebeat | awk 'NR==1{printf "%.1f %.1f\n", $1, $2}'
}

# Function to get total resource usage
get_total_usage() {
    total_cpu=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    total_mem=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
    echo "$total_cpu $total_mem"
}

# Function to get Disk Usage
get_disk_usage() {
    df / | awk 'NR==2 {printf "%.1f\n", $3/$2 * 100.0}'
}

# Function to get Network I/O (RX and TX)
get_network_io() {
    rx_bytes=$(cat /proc/net/dev | grep -w 'ens3' | awk '{print $2}') # Adjust the interface name as necessary
    tx_bytes=$(cat /proc/net/dev | grep -w 'ens3' | awk '{print $10}') # Adjust the interface name as necessary
    echo "$rx_bytes $tx_bytes"
}

# Main execution
echo "Collecting resource usage..."
ELK_ENABLED=false # Change this based on input argument

# Initialize totals
total_docker_cpu=0
total_docker_mem=0
total_zeek_cpu=0
total_zeek_mem=0
total_filebeat_cpu=0
total_filebeat_mem=0
total_cpu=0
total_mem=0
total_disk=0
total_rx=0
total_tx=0
iterations=5 # Number of iterations to collect data

# Loop for a specified number of iterations
for (( i=0; i<$iterations; i++ )); do
    if [ "$ELK_ENABLED" = true ]; then
        read docker_cpu docker_mem < <(get_docker_usage "NF")
        total_docker_cpu=$(echo "$total_docker_cpu + $docker_cpu" | bc)
        total_docker_mem=$(echo "$total_docker_mem + $docker_mem" | bc)

        read zeek_cpu zeek_mem < <(get_zeek_usage)
        total_zeek_cpu=$(echo "$total_zeek_cpu + $zeek_cpu" | bc)
        total_zeek_mem=$(echo "$total_zeek_mem + $zeek_mem" | bc)

        read filebeat_cpu filebeat_mem < <(get_filebeat_usage)
        total_filebeat_cpu=$(echo "$total_filebeat_cpu + $filebeat_cpu" | bc)
        total_filebeat_mem=$(echo "$total_filebeat_mem + $filebeat_mem" | bc)
    fi

    read cpu mem < <(get_total_usage)
    total_cpu=$(echo "$total_cpu + $cpu" | bc)
    total_mem=$(echo "$total_mem + $mem" | bc)

    # Get disk and network usage
    disk_usage=$(get_disk_usage)
    total_disk=$(echo "$total_disk + $disk_usage" | bc)
    
    read rx tx < <(get_network_io)
    total_rx=$(echo "$total_rx + $rx" | bc)
    total_tx=$(echo "$total_tx + $tx" | bc)

    # Sleep for a short period before the next iteration
    sleep 1
done

# Calculate averages
avg_docker_cpu=$(echo "$total_docker_cpu / $iterations" | bc -l)
avg_docker_mem=$(echo "$total_docker_mem / $iterations" | bc -l)
avg_zeek_cpu=$(echo "$total_zeek_cpu / $iterations" | bc -l)
avg_zeek_mem=$(echo "$total_zeek_mem / $iterations" | bc -l)
avg_filebeat_cpu=$(echo "$total_filebeat_cpu / $iterations" | bc -l)
avg_filebeat_mem=$(echo "$total_filebeat_mem / $iterations" | bc -l)
avg_cpu=$(echo "$total_cpu / $iterations" | bc -l)
avg_mem=$(echo "$total_mem / $iterations" | bc -l)
avg_disk=$(echo "$total_disk / $iterations" | bc -l)
avg_rx=$(echo "$total_rx / $iterations" | bc -l)
avg_tx=$(echo "$total_tx / $iterations" | bc -l)

# Output JSON
echo "{
    \"docker\": {
        \"avg_cpu\": $avg_docker_cpu,
        \"avg_mem\": $avg_docker_mem
    },
    \"zeek\": {
        \"avg_cpu\": $avg_zeek_cpu,
        \"avg_mem\": $avg_zeek_mem
    },
    \"filebeat\": {
        \"avg_cpu\": $avg_filebeat_cpu,
        \"avg_mem\": $avg_filebeat_mem
    },
    \"total\": {
        \"avg_cpu\": $avg_cpu,
        \"avg_mem\": $avg_mem,
        \"avg_disk\": $avg_disk,
        \"avg_rx_bytes\": $avg_rx,
        \"avg_tx_bytes\": $avg_tx
    }
}" > resource_usage.json
