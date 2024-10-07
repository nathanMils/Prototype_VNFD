#!/bin/bash

# Output file
output_file="resource_usage.json"

elk_enabled=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --elk-enabled) elk_enabled=true ;;
        *) echo "Unknown parameter: $1" ;;
    esac
    shift
done

get_docker_usage() {
    docker_stats=$(sudo docker stats --no-stream --format "{{.Name}}: CPU={{.CPUPerc}} | MEM={{.MemUsage}}")
    echo "$docker_stats"
}

get_zeek_usage() {
    local zeek_info=$(ps -o pid,%cpu,%mem,command -C zeek | awk 'NR==1{printf "{\"Zeek\": {\"CPU\": \"%.1f%%\", \"MEM\": \"%.1f%%\", \"I/O\": \"%s KB/s\"}}", $2, $3, get_io_usage($1)}')
    echo "$zeek_info"
}

get_filebeat_usage() {
    local filebeat_info=$(ps -o pid,%cpu,%mem,command -C filebeat | awk 'NR==1{printf "{\"Filebeat\": {\"CPU\": \"%.1f%%\", \"MEM\": \"%.1f%%\", \"I/O\": \"%s KB/s\"}}", $2, $3, get_io_usage($1)}')
    echo "$filebeat_info"
}

get_io_usage() {
    pid=$1
    if [[ -n "$pid" ]]; then
        io_stats=$(pidstat -d -p "$pid" 1 1 | awk 'NR==4 {print $5 + $6}')
        echo "$io_stats" 
    else
        echo "0"
    fi
}

get_total_usage() {
    total_cpu=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    total_mem=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
    total_io=$(iostat -d | awk 'NR==4 {print $3}')
    active_processes=$(ps aux | wc -l)
    
    echo "{\"Total\": {\"CPU\": \"${total_cpu}%, \"MEM\": \"${total_mem}%, \"I/O\": \"$total_io KB/s\", \"Active Processes\": \"$active_processes\"}}"
}

get_network_stats() {
    network_stats=$(ifstat -S 1 1 | awk 'NR==3 {print $1, $2}')
    echo "{\"Network\": {\"Received\": \"${network_stats[0]} KB/s\", \"Transmitted\": \"${network_stats[1]} KB/s\"}}"
}

echo "Collecting resource usage..."

echo "{" > "$output_file"
echo "\"resource_usage\": {" >> "$output_file"

docker_usage=$(get_docker_usage)
echo "$docker_usage," >> "$output_file"

if [[ "$elk_enabled" == true ]]; then
    zeek_usage=$(get_zeek_usage)
    filebeat_usage=$(get_filebeat_usage)

    echo "$zeek_usage," >> "$output_file"
    echo "$filebeat_usage," >> "$output_file"
fi

total_usage=$(get_total_usage)
network_stats=$(get_network_stats)

echo "$total_usage," >> "$output_file"
echo "$network_stats" >> "$output_file"

echo "}" >> "$output_file"
echo "}" >> "$output_file"

echo "Resource usage data saved to $output_file"