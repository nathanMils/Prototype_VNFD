import psutil
import json
import time
import argparse
from collections import defaultdict
import logging
import os

# Configure logging
logging.basicConfig(
    filename='apache_monitor.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Define the target process name
TARGET_PROCESS = 'apache2'

def get_process_info(process_name, prev_io=None):
    """
    Retrieves CPU, memory, disk I/O, and (placeholder for network I/O) usage for all instances of a given process.
    Optionally calculates per-interval disk I/O based on previous counts.
    """
    cpu = 0.0
    memory = 0.0
    disk_read = 0
    disk_write = 0
    network_sent = 0
    network_recv = 0  # Placeholder as per-process network I/O is not directly available

    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'io_counters']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                cpu += proc.cpu_percent(interval=None)  # Non-blocking, already calculated
                memory += proc.memory_percent()
                if proc.info['io_counters']:
                    pid = proc.info['pid']
                    current_read = proc.info['io_counters'].read_bytes
                    current_write = proc.info['io_counters'].write_bytes

                    if prev_io and pid in prev_io:
                        # Calculate per-interval disk I/O
                        disk_read += current_read - prev_io[pid]['read_bytes']
                        disk_write += current_write - prev_io[pid]['write_bytes']
                    else:
                        # First time seeing this process; cannot calculate difference
                        disk_read += 0
                        disk_write += 0

                    # Update previous I/O counters
                    if prev_io is not None:
                        prev_io[pid] = {
                            'read_bytes': current_read,
                            'write_bytes': current_write
                        }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return {
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_io": {
            "read_bytes": disk_read,
            "write_bytes": disk_write
        },
        "network_io": {
            "bytes_sent": network_sent,
            "bytes_recv": network_recv
        }
    }

def get_total_system_info():
    """
    Retrieves total CPU, memory, disk I/O, and network I/O usage for the machine.
    """
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    disk_io = psutil.disk_io_counters()
    net_io = psutil.net_io_counters()

    return {
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_io": {
            "read_bytes": disk_io.read_bytes,
            "write_bytes": disk_io.write_bytes
        },
        "network_io": {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv
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
            },
            "network_io": {
                "bytes_sent": 0,
                "bytes_recv": 0
            }
        }),
        "total_system": {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_io": {
                "read_bytes": 0,
                "write_bytes": 0
            },
            "network_io": {
                "bytes_sent": 0,
                "bytes_recv": 0
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
        # Network I/O is a placeholder
        aggregates["processes"][proc_name]["network_io"]["bytes_sent"] += info["network_io"]["bytes_sent"]
        aggregates["processes"][proc_name]["network_io"]["bytes_recv"] += info["network_io"]["bytes_recv"]
    
    aggregates["total_system"]["cpu_percent"] += data["total_system"]["cpu_percent"]
    aggregates["total_system"]["memory_percent"] += data["total_system"]["memory_percent"]
    aggregates["total_system"]["disk_io"]["read_bytes"] += data["total_system"]["disk_io"]["read_bytes"]
    aggregates["total_system"]["disk_io"]["write_bytes"] += data["total_system"]["disk_io"]["write_bytes"]
    aggregates["total_system"]["network_io"]["bytes_sent"] += data["total_system"]["network_io"]["bytes_sent"]
    aggregates["total_system"]["network_io"]["bytes_recv"] += data["total_system"]["network_io"]["bytes_recv"]

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
            },
            "network_io": {
                "bytes_sent": info["network_io"]["bytes_sent"] // sample_count,
                "bytes_recv": info["network_io"]["bytes_recv"] // sample_count
            }
        }
    
    averaged_data["total_system"] = {
        "cpu_percent": round(aggregates["total_system"]["cpu_percent"] / sample_count, 2),
        "memory_percent": round(aggregates["total_system"]["memory_percent"] / sample_count, 2),
        "disk_io": {
            "read_bytes": aggregates["total_system"]["disk_io"]["read_bytes"] // sample_count,
            "write_bytes": aggregates["total_system"]["disk_io"]["write_bytes"] // sample_count
        },
        "network_io": {
            "bytes_sent": aggregates["total_system"]["network_io"]["bytes_sent"] // sample_count,
            "bytes_recv": aggregates["total_system"]["network_io"]["bytes_recv"] // sample_count
        }
    }

    return averaged_data

def parse_arguments():
    """
    Parses command-line arguments to toggle process monitoring and specify output file.
    """
    parser = argparse.ArgumentParser(description="Monitor resource usage of apache2 process and the total system over time.")
    parser.add_argument('-d', '--duration', type=int, default=60, help='Total duration to monitor in seconds (default: 60)')
    parser.add_argument('-i', '--interval', type=int, default=5, help='Sampling interval in seconds (default: 5)')
    parser.add_argument('--output', type=str, default='apache_resource_usage.json', help='Output file path to save JSON data (default: apache_resource_usage.json)')
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

    selected_processes = [TARGET_PROCESS]  # Only monitor apache2

    sample_count = duration // interval
    if sample_count == 0:
        sample_count = 1  # Ensure at least one sample

    logging.info(f"Selected process to monitor: {selected_processes}")
    print(f"Selected process to monitor: {selected_processes}")
    logging.info(f"Starting resource monitoring for {duration} seconds with {interval}-second intervals.")
    print(f"Starting resource monitoring for {duration} seconds with {interval}-second intervals...")

    aggregates = initialize_aggregates(selected_processes)
    prev_io = {proc: {} for proc in selected_processes}  # To track previous I/O counters per process

    for sample in range(sample_count):
        logging.info(f"Collecting sample {sample + 1}/{sample_count}...")
        print(f"Collecting sample {sample + 1}/{sample_count}...")
        # Initialize CPU percent calculations
        psutil.cpu_percent(interval=None)
        for proc in psutil.process_iter(['name']):
            try:
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                logging.warning(f"Process iteration error: PID={proc.pid}")
                continue

        # Wait for the interval
        time.sleep(interval)

        try:
            # Collect current data
            process_data = {}
            for proc_name in selected_processes:
                process_data[proc_name] = get_process_info(proc_name, prev_io=prev_io[proc_name] if proc_name in prev_io else None)
            
            total_system_data = get_total_system_info()

            data = {
                "processes": process_data,
                "total_system": total_system_data
            }

            # Accumulate data
            accumulate_aggregates(aggregates, data)
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
