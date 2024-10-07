#!/bin/bash

# Output file
output_file="resource_usage.json"

# Function to get Docker container resource usage
get_docker_usage() {
    # Get the CPU and memory usage of the NF Docker container
    docker_stats=$(sudo docker stats --no-stream --format "{{$VNF}}: CPU={{.CPUPerc}} | MEM={{.MemUsage}}")
    echo "$docker_stats"
}

# Function to get Zeek resource usage
get_zeek_usage() {
    # Get the CPU, memory usage, and disk I/O of the Zeek process
    local zeek_info=$(ps -o pid,%cpu,%mem,command -C zeek | awk 'NR==1{printf "{\"Zeek\": {\"CPU\": \"%.1f%%\", \"MEM\": \"%.1f%%\", \"I/O\": \"%.1f KB/s\"}}", $2, $3, get_io_usage($1)}')
    echo "$zeek_info"
}

# Function to get Filebeat resource usage
get_filebeat_usage() {
    # Get the CPU, memory usage, and disk I/O of the Filebeat process
    local filebeat_info=$(ps -o pid,%cpu,%mem,command -C filebeat | awk 'NR==1{printf "{\"Filebeat\": {\"CPU\": \"%.1f%%\", \"MEM\": \"%.1f%%\", \"I/O\": \"%.1f KB/s\"}}", $2, $3, get_io_usage($1)}')
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
    
    echo "{\"Total\": {\"CPU\": \"${total_cpu}%, \"MEM\": \"${total_mem}%\"}}"
}

# Main execution
echo "Collecting resource usage..."

# Create the JSON output file
echo "{" > "$output_file"
echo "\"resource_usage\": {" >> "$output_file"

# Get each usage and append to the JSON output file
docker_usage=$(get_docker_usage)
zeek_usage=$(get_zeek_usage)
filebeat_usage=$(get_filebeat_usage)
total_usage=$(get_total_usage)

# Remove any trailing commas and format correctly
echo "$docker_usage," >> "$output_file"
echo "$zeek_usage," >> "$output_file"
echo "$filebeat_usage," >> "$output_file"
echo "$total_usage" >> "$output_file"

# Finalize the JSON structure
echo "}" >> "$output_file"
echo "}" >> "$output_file"

echo "Resource usage data saved to $output_file"
