import subprocess
import time
import argparse

def monitor_process(process_name, duration, output_file):
    cmd = [
        'glances', '--process-filter', process_name, f'--export-json-file {output_file}'
    ]
    with subprocess.Popen(cmd) as proc:
        time.sleep(duration)
        proc.terminate()

def monitor_container(container_name, duration, output_file):
    cmd = [
        'glances', '--process-filter', container_name, '--export-json-file', output_file
    ]
    with subprocess.Popen(cmd) as proc:
        time.sleep(duration)
        proc.terminate()

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Monitor processes and Docker containers using Glances.')
    parser.add_argument('-c', '--container', type=str, required=True,
                        help='Name of the Docker container to monitor')
    parser.add_argument('-t', '--time', type=int, default=300,
                        help='Duration in seconds to monitor (default: 300)')

    args = parser.parse_args()

    duration = args.time

    subprocess_1 = subprocess.Popen(
        lambda: monitor_process('filebeat', duration, 'filebeat_monitor.json')
    )

    subprocess_2 = subprocess.Popen(
        lambda: monitor_process('zeek', duration, 'zeek_monitor.json')
    )

    subprocess_3 = subprocess.Popen(
        lambda: monitor_container(args.container, duration, 'docker_monitor.json')
    )

    subprocess_1.wait()
    subprocess_2.wait()
    subprocess_3.wait()

    print("Monitoring completed. Check the JSON output files.")