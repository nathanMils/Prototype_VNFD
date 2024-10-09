import psutil
import json
import time
import docker
import argparse
from collections import defaultdict
import logging
import os

logging.basicConfig(
    filename='resource_monitor.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def get_container_info(container_name):
    """
    Retrieves CPU and memory usage for a Docker container by name.
    """
    client = docker.from_env()
    cpu_percent = 0.0
    memory_percent = 0.0

    try:
        container = client.containers.get(container_name)
        
        stats = container.stats(stream=False)

        cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
        system_cpu_usage = stats['cpu_stats']['system_cpu_usage']

        # Check for 'percpu_usage' existence
        if 'percpu_usage' in stats['cpu_stats']['cpu_usage']:
            number_of_cores = len(stats['cpu_stats']['cpu_usage']['percpu_usage'])
        else:
            number_of_cores = 1  # Default to 1 if not available

        if system_cpu_usage > 0:
            cpu_percent = (cpu_usage / system_cpu_usage) * number_of_cores * 100

        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats']['limit']
        memory_percent = (memory_usage / memory_limit) * 100 if memory_limit > 0 else 0

    except docker.errors.NotFound:
        logging.error(f"Container '{container_name}' not found.")
        return None
    except docker.errors.APIError as e:
        logging.error(f"Error accessing Docker API: {e}")
        return None
    except KeyError as e:
        logging.error(f"KeyError: {e} - Check the structure of the stats returned.")
        return None

    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
    }

def get_process_info(proc_name):
    """
    Retrieves CPU and memory usage for a given process name.
    """
    cpu = 0.0
    memory = 0.0

    try:
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] == proc_name:
                cpu = proc.cpu_percent(interval=None)
                memory = proc.memory_percent()
                break
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        logging.error(f"Process '{proc_name}' not found or access denied.")
        return None

    return {
        "cpu_percent": cpu,
        "memory_percent": memory,
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
            "memory_percent": 0.0
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
    for proc in selected_processes:
        aggregates["processes"][proc]  # Initialize entry for each process
    return aggregates

def accumulate_aggregates(aggregates, data):
    """
    Accumulates resource usage data into aggregates.
    """
    for proc_name, info in data["processes"].items():
        aggregates["processes"][proc_name]["cpu_percent"] += info["cpu_percent"]
        aggregates["processes"][proc_name]["memory_percent"] += info["memory_percent"]
    
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
            "memory_percent": round(info["memory_percent"] / sample_count, 2)
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

ZAPIER_WEBHOOK_URL = 'https://hooks.zapier.com/hooks/catch/20350848/2mcrrua/'

def send_to_zapier(json_data):
    try:
        cmd = f"curl -X POST {ZAPIER_WEBHOOK_URL} -H 'Content-Type: application/json' -d '{json_data}'"
        os.system(cmd)  # Execute the curl command
        logging.info(f"Data sent to Zapier: {json_data}")
    except Exception as e:
        logging.error(f"Error sending data to Zapier: {e}")

def parse_arguments():
    """
    Parses command-line arguments to toggle process monitoring and specify output file.
    """
    parser = argparse.ArgumentParser(description="Monitor resource usage of a Docker container by name and the total system over time.")
    parser.add_argument('-c', '--container', type=str, required=True, help='Name of the Docker container to monitor (required)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Total duration to monitor in seconds (default: 60)')
    parser.add_argument('-i', '--interval', type=int, default=5, help='Sampling interval in seconds (default: 5)')
    parser.add_argument('-n', '--name', type=str, help='Custom name to include in the JSON output (not sent to Zapier)')
    parser.add_argument('--elk-disabled', action='store_true', help='Disable monitoring of ELK stack processes (zeek and filebeat)')
    parser.add_argument('-o', '--output', type=str, default='averaged_data.json', help='Output file for the averaged data (default: averaged_data.json)')

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
    
    selected_processes = [args.container]

    if not args.elk_disabled:
        selected_processes.append("zeek")
        selected_processes.append("filebeat")

    aggregates = initialize_aggregates(selected_processes)

    logging.info(f"Monitoring started for {selected_processes} over {duration} seconds with {interval}-second intervals.")
    sample_count = duration // interval

    for _ in range(sample_count):
        try:
            current_data = {
                "processes": {},
                "total_system": get_total_system_info()
            }

            container_info = get_container_info(args.container)
            if container_info is not None:
                current_data["processes"][args.container] = container_info
            
            if not args.elk_disabled:
                if "zeek" in selected_processes:
                    zeek_info = get_process_info("zeek")
                    if zeek_info is not None:
                        current_data["processes"]["zeek"] = zeek_info
                
                if "filebeat" in selected_processes:
                    filebeat_info = get_process_info("filebeat")
                    if filebeat_info is not None:
                        current_data["processes"]["filebeat"] = filebeat_info
            
            accumulate_aggregates(aggregates, current_data)

            time.sleep(interval)

        except Exception as e:
            logging.error(f"Error during data collection: {e}")
            print(f"An error occurred during data collection: {e}")

    try:
        averaged_data = calculate_averages(aggregates, sample_count)

        if args.name:
            averaged_data["custom_name"] = args.name
        
        json_output = json.dumps(averaged_data, indent=4)

        output_file = args.output
        with open(output_file, 'w') as f:
            f.write(json_output)
        logging.info(f"Averaged Resource Usage has been saved to {output_file}")
        print(f"\nAveraged Resource Usage has been saved to {output_file}")

        send_to_zapier(json_output)

        print("\nAveraged Resource Usage:")
        print(json_output)
    except Exception as e:
        logging.error(f"Error during averaging or output: {e}")
        print(f"An error occurred during averaging or output: {e}")

if __name__ == "__main__":
    main()
