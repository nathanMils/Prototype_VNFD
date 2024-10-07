#!/bin/bash

# Output file
output_file="resource_usage.json"

# Parse command line arguments
elk_enabled=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --elk-enabled) elk_enabled=true ;;
        *) echo "Unknown parameter: $1" ;;
    esac
    shift
done

# Function to get Docker container resource usage
get_docker_usage() {
    # Get the CPU and memory usage of the NF Docker container
    docker_stats=$(sudo docker stats --no-stream --format "{{.Name}}: CPU={{.CPUPerc}} | MEM={{.MemUsage}}")
    echo "$docker_stats"
}

# Function to get Zeek resource usage
get_zeek_usage() {
    # Get the CPU, memory usage, and disk I/O of the Zeek process
    local zeek_info=$(ps -o pid,%cpu,%mem,command -C zeek | awk 'NR==1{printf "{\"Zeek\": {\"CPU\": \"%.1f%%\", \"MEM\": \"%.1f%%\", \"I/O\": \"%s KB/s\"}}", $2, $3, get_io_usage($1)}')
    echo "$zeek_info"
}

# Function to get Filebeat resource usage
get_filebeat_usage() {
    # Get the CPU, memory usage, and disk I/O of the Filebeat process
    local filebeat_info=$(ps -o pid,%cpu,%mem,command -C filebeat | awk 'NR==1{printf "{\"Filebeat\": {\"CPU\": \"%.1f%%\", \"MEM\": \"%.1f%%\", \"I/O\": \"%s KB/s\"}}", $2, $3, get_io_usage($1)}')
    echo "$filebeat_info"
}

# Function to get disk I/O for a specific PID
get_io_usage() {
    pid=$1
    if [[ -n "$pid" ]]; then
        # Use pidstat to get I/O statistics for the specified PID
        io_stats=$(pidstat -d -p "$pid" 1 1 | awk 'NR==4 {print $5 + $6}') # rx_bytes + wx_bytes
        echo "$io_stats"  # Return total I/O bytes
    else
        echo "0"
    fi
}

# Function to get total resource usage
get_total_usage() {
    # Get total CPU usage and total memory usage
    total_cpu=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    total_mem=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
    total_io=$(iostat -d | awk 'NR==4 {print $3}')  # Total disk I/O
    active_processes=$(ps aux | wc -l)  # Count active processes
    
    echo "{\"Total\": {\"CPU\": \"${total_cpu}%, \"MEM\": \"${total_mem}%, \"I/O\": \"$total_io KB/s\", \"Active Processes\": \"$active_processes\"}}"
}

# Function to get network statistics
get_network_stats() {
    # Use ifstat to get network statistics (install ifstat if not present)
    network_stats=$(ifstat -S 1 1 | awk 'NR==3 {print $1, $2}')
    echo "{\"Network\": {\"Received\": \"${network_stats[0]} KB/s\", \"Transmitted\": \"${network_stats[1]} KB/s\"}}"
}

# Main execution
echo "Collecting resource usage..."

# Create the JSON output file
echo "{" > "$output_file"
echo "\"resource_usage\": {" >> "$output_file"

# Get Docker usage and append to the JSON output file
docker_usage=$(get_docker_usage)
echo "$docker_usage," >> "$output_file"

# Check if ELK is enabled
if [[ "$elk_enabled" == true ]]; then
    # Get Zeek and Filebeat usage if ELK is enabled
    zeek_usage=$(get_zeek_usage)
    filebeat_usage=$(get_filebeat_usage)

    # Remove any trailing commas and format correctly
    echo "$zeek_usage," >> "$output_file"
    echo "$filebeat_usage," >> "$output_file"
fi

# Get total usage and network stats, then append to the JSON output file
total_usage=$(get_total_usage)
network_stats=$(get_network_stats)

echo "$total_usage," >> "$output_file"
echo "$network_stats" >> "$output_file"

# Finalize the JSON structure
echo "}" >> "$output_file"
echo "}" >> "$output_file"

echo "Resource usage data saved to $output_file"
