import psutil
import json
import time
import argparse
from collections import defaultdict
import logging
import os

# Configure logging
logging.basicConfig(
    filename='resource_monitor.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def get_container_info(container_name, prev_io=None):
    """
    Retrieves CPU, memory, and disk I/O usage for a Docker container by name.
    Optionally calculates per-interval disk I/O based on previous counts.
    """
    cpu = 0.0
    memory = 0.0
    disk_read = 0
    disk_write = 0

    try:
        # Get the container's PID using docker ps and psutil
        container_info = os.popen(f"docker inspect -f '{{{{.State.Pid}}}}' {container_name}").read().strip()
        pid = int(container_info)

        proc = psutil.Process(pid)
        cpu = proc.cpu_percent(interval=None)  # Non-blocking, already calculated
        memory = proc.memory_percent()
        if proc.io_counters():
            current_read = proc.io_counters().read_bytes
            current_write = proc.io_counters().write_bytes
            
            if prev_io:
                # Calculate per-interval disk I/O
                disk_read += current_read - prev_io['read_bytes']
                disk_write += current_write - prev_io['write_bytes']
            else:
                # First time seeing this process; cannot calculate difference
                disk_read += 0
                disk_write += 0
            
            # Update previous I/O counters
            if prev_io is not None:
                prev_io.update({
                    'read_bytes': current_read,
                    'write_bytes': current_write
                })
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        logging.error(f"Process with PID for container '{container_name}' not found or access denied.")
        return None
    except Exception as e:
        logging.error(f"Error retrieving container info: {e}")
        return None

    return {
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_io": {
            "read_bytes": disk_read,
            "write_bytes": disk_write
        }
    }

def get_process_info(proc_name, prev_io=None):
    """
    Retrieves CPU, memory, and disk I/O usage for a given process name.
    Optionally calculates per-interval disk I/O based on previous counts.
    """
    cpu = 0.0
    memory = 0.0
    disk_read = 0
    disk_write = 0

    try:
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] == proc_name:
                cpu = proc.cpu_percent(interval=None)  # Non-blocking, already calculated
                memory = proc.memory_percent()
                if proc.io_counters():
                    current_read = proc.io_counters().read_bytes
                    current_write = proc.io_counters().write_bytes

                    if prev_io:
                        # Calculate per-interval disk I/O
                        disk_read += current_read - prev_io['read_bytes']
                        disk_write += current_write - prev_io['write_bytes']
                    else:
                        # First time seeing this process; cannot calculate difference
                        disk_read += 0
                        disk_write += 0

                    # Update previous I/O counters
                    if prev_io is not None:
                        prev_io.update({
                            'read_bytes': current_read,
                            'write_bytes': current_write
                        })
                break
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        logging.error(f"Process '{proc_name}' not found or access denied.")
        return None

    return {
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_io": {
            "read_bytes": disk_read,
            "write_bytes": disk_write
        }
    }

def get_total_system_info():
    """
    Retrieves total CPU, memory, disk I/O, and network I/O usage for the machine.
    """
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    disk_io = psutil.disk_io_counters()

    return {
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_io": {
            "read_bytes": disk_io.read_bytes,
            "write_bytes": disk_io.write_bytes
        }
    }

def initialize_aggregates(selected_processes):
    """
    Initializes data structures to accumulate resource usage data.
    """
    aggregates = {
        "processes": defaultdict(lambda: {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_io": {
                "read_bytes": 0,
                "write_bytes": 0
            }
        }),
        "total_system": {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_io": {
                "read_bytes": 0,
                "write_bytes": 0
            }
        }
    }
    # Initialize only selected processes
    for proc in selected_processes:
        aggregates["processes"][proc]  # This ensures the defaultdict initializes the entry
    return aggregates

def accumulate_aggregates(aggregates, data):
    """
    Accumulates resource usage data into aggregates.
    """
    for proc_name, info in data["processes"].items():
        aggregates["processes"][proc_name]["cpu_percent"] += info["cpu_percent"]
        aggregates["processes"][proc_name]["memory_percent"] += info["memory_percent"]
        aggregates["processes"][proc_name]["disk_io"]["read_bytes"] += info["disk_io"]["read_bytes"]
        aggregates["processes"][proc_name]["disk_io"]["write_bytes"] += info["disk_io"]["write_bytes"]
    
    aggregates["total_system"]["cpu_percent"] += data["total_system"]["cpu_percent"]
    aggregates["total_system"]["memory_percent"] += data["total_system"]["memory_percent"]
    aggregates["total_system"]["disk_io"]["read_bytes"] += data["total_system"]["disk_io"]["read_bytes"]
    aggregates["total_system"]["disk_io"]["write_bytes"] += data["total_system"]["disk_io"]["write_bytes"]

def calculate_averages(aggregates, sample_count):
    """
    Calculates average resource usage from aggregates.
    """
    averaged_data = {
        "processes": {},
        "total_system": {}
    }

    for proc_name, info in aggregates["processes"].items():
        averaged_data["processes"][proc_name] = {
            "cpu_percent": round(info["cpu_percent"] / sample_count, 2),
            "memory_percent": round(info["memory_percent"] / sample_count, 2),
            "disk_io": {
                "read_bytes": info["disk_io"]["read_bytes"] // sample_count,
                "write_bytes": info["disk_io"]["write_bytes"] // sample_count
            }
        }
    
    averaged_data["total_system"] = {
        "cpu_percent": round(aggregates["total_system"]["cpu_percent"] / sample_count, 2),
        "memory_percent": round(aggregates["total_system"]["memory_percent"] / sample_count, 2),
        "disk_io": {
            "read_bytes": aggregates["total_system"]["disk_io"]["read_bytes"] // sample_count,
            "write_bytes": aggregates["total_system"]["disk_io"]["write_bytes"] // sample_count
        }
    }

    return averaged_data

def parse_arguments():
    """
    Parses command-line arguments to toggle process monitoring and specify output file.
    """
    parser = argparse.ArgumentParser(description="Monitor resource usage of a Docker container by name and the total system over time.")
    parser.add_argument('-c', '--container', type=str, required=True, help='Name of the Docker container to monitor (required)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Total duration to monitor in seconds (default: 60)')
    parser.add_argument('-i', '--interval', type=int, default=5, help='Sampling interval in seconds (default: 5)')
    parser.add_argument('--elk-disabled', action='store_true', help='Disable monitoring of ELK stack processes (zeek and filebeat)')
    parser.add_argument('--zeek-disabled', action='store_true', help='Disable monitoring of zeek process')
    parser.add_argument('--filebeat-disabled', action='store_true', help='Disable monitoring of filebeat process')
    parser.add_argument('-o', '--output', type=str, default='resource_usage.json', help='Output file path to save JSON data (default: resource_usage.json)')
    return parser.parse_args()

def main():
    args = parse_arguments()

    duration = args.duration
    interval = args.interval

    if interval <= 0:
        logging.error("Interval must be a positive integer.")
        print("Interval must be a positive integer.")
        return
    if duration <= 0:
        logging.error("Duration must be a positive integer.")
        print("Duration must be a positive integer.")
        return

    # Determine which processes to monitor based on flags
    selected_processes = [args.container]  # Use the provided container name

    # Add zeek and filebeat based on user input
    if not args.elk_disabled:
        if not args.zeek_disabled:
            selected_processes.append("zeek")
        if not args.filebeat_disabled:
            selected_processes.append("filebeat")

    aggregates = initialize_aggregates(selected_processes)

    logging.info(f"Monitoring started for {selected_processes} over {duration} seconds with {interval}-second intervals.")

    # Initialize previous I/O counters
    previous_io = {}
    sample_count = duration // interval

    for _ in range(sample_count):
        try:
            # Collect data
            current_data = {
                "processes": {},
                "total_system": get_total_system_info()
            }

            # Collect Docker container info
            container_info = get_container_info(args.container, previous_io.get(args.container))
            if container_info is not None:
                current_data["processes"][args.container] = container_info
            
            # Collect other process info if not disabled
            if not args.elk_disabled:
                if "zeek" in selected_processes:
                    zeek_info = get_process_info("zeek", previous_io.get("zeek"))
                    if zeek_info is not None:
                        current_data["processes"]["zeek"] = zeek_info
                
                if "filebeat" in selected_processes:
                    filebeat_info = get_process_info("filebeat", previous_io.get("filebeat"))
                    if filebeat_info is not None:
                        current_data["processes"]["filebeat"] = filebeat_info
            
            # Accumulate aggregates
            accumulate_aggregates(aggregates, current_data)

            # Wait for the next interval
            time.sleep(interval)

        except Exception as e:
            logging.error(f"Error during data collection: {e}")
            print(f"An error occurred during data collection: {e}")

    try:
        # Calculate averages
        averaged_data = calculate_averages(aggregates, sample_count)

        # Output the data as JSON
        json_output = json.dumps(averaged_data, indent=4)

        # Write to external JSON file
        output_file = args.output
        with open(output_file, 'w') as f:
            f.write(json_output)
        logging.info(f"Averaged Resource Usage has been saved to {output_file}")
        print(f"\nAveraged Resource Usage has been saved to {output_file}")

        # Also print to console
        print("\nAveraged Resource Usage:")
        print(json_output)
    except Exception as e:
        logging.error(f"Error during averaging or output: {e}")
        print(f"An error occurred during averaging or output: {e}")

if __name__ == "__main__":
    main()