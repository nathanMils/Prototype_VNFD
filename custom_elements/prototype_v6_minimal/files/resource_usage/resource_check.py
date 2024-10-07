import psutil
import json
import time
import argparse
from collections import defaultdict

# Define the target process names
TARGET_PROCESSES = ['docker', 'zeek', 'filebeat']

def get_process_info(process_name):
    """
    Retrieves CPU, memory, disk I/O, and (placeholder for network I/O) usage for all instances of a given process.
    """
    cpu = 0.0
    memory = 0.0
    disk_read = 0
    disk_write = 0
    network_sent = 0
    network_recv = 0  # Placeholder as per-process network I/O is not directly available

    # Iterate over all running processes
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent', 'io_counters']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                cpu += proc.cpu_percent(interval=None)  # Non-blocking, already calculated
                memory += proc.memory_percent()
                if proc.info['io_counters']:
                    disk_read += proc.info['io_counters'].read_bytes
                    disk_write += proc.info['io_counters'].write_bytes
                # Network I/O per process is not available via psutil
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

def initialize_aggregates():
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

def main():
    # Parse command-line arguments for duration and interval
    parser = argparse.ArgumentParser(description="Monitor resource usage of specific processes and the total system over time.")
    parser.add_argument('-d', '--duration', type=int, default=60, help='Total duration to monitor in seconds (default: 60)')
    parser.add_argument('-i', '--interval', type=int, default=5, help='Sampling interval in seconds (default: 5)')
    args = parser.parse_args()

    duration = args.duration
    interval = args.interval

    if interval <= 0:
        print("Interval must be a positive integer.")
        return
    if duration <= 0:
        print("Duration must be a positive integer.")
        return

    sample_count = duration // interval
    if sample_count == 0:
        sample_count = 1  # Ensure at least one sample

    print(f"Starting resource monitoring for {duration} seconds with {interval}-second intervals...")
    aggregates = initialize_aggregates()

    for _ in range(sample_count):
        # Initialize CPU percent calculations
        psutil.cpu_percent(interval=None)
        for proc in psutil.process_iter(['name']):
            try:
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Wait for the interval
        time.sleep(interval)

        # Collect current data
        process_data = {}
        for proc_name in TARGET_PROCESSES:
            process_data[proc_name] = get_process_info(proc_name)
        
        total_system_data = get_total_system_info()

        data = {
            "processes": process_data,
            "total_system": total_system_data
        }

        # Accumulate data
        accumulate_aggregates(aggregates, data)

    # Calculate averages
    averaged_data = calculate_averages(aggregates, sample_count)

    # Output the data as JSON
    json_output = json.dumps(averaged_data, indent=4)
    print("\nAveraged Resource Usage:")
    print(json_output)

if __name__ == "__main__":
    main()
