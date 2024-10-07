#!/usr/bin/python3

#
# Enhanced UE Traffic Simulator with Recursive Browsing
# Integrates recursive web traffic generation into UERANSIM for multiple UEs
#
# Dependencies:
# - psutil
# - requests
# - selenium
# - paho-mqtt
# - VLC (cvlc)
# - wget
#
# Ensure all dependencies are installed and accessible.
#

from __future__ import print_function
import subprocess
import threading
import time
import json
import os
import signal
import argparse
import requests
import re
import random
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import paho.mqtt.client as mqtt

# =======================
# Configuration Class
# =======================
class ConfigClass:
    # Recursive Browsing Configurations
    MAX_DEPTH = 5  # Dive no deeper than this for each root URL
    MIN_DEPTH = 2  # Dive at least this deep into each root URL
    MAX_WAIT = 10   # Maximum time to wait between HTTP requests
    MIN_WAIT = 3    # Minimum time to wait between HTTP requests
    DEBUG = False    # Set to True to enable debug output

    # Root URLs to start crawling
    ROOT_URLS = [
        "https://www.example.com",
        "https://www.wikipedia.org",
        "https://www.python.org"
    ]

    # Blacklist domains to exclude from crawling
    BLACKLIST = [
        'facebook.com',
        'pinterest.com',
        'twitter.com'
    ]

    # User-Agent string for HTTP requests
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'

# =======================
# Initialize Configuration
# =======================
try:
    import config  # Attempt to import from external config.py
except ImportError:
    config = ConfigClass()  # Use default configuration if config.py is not found

# =======================
# Colors for Console Output
# =======================
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    PURPLE = '\033[95m'
    NONE = '\033[0m'

# =======================
# Debug Print Function
# =======================
def debug_print(message, color=Colors.NONE):
    """Prints debug messages if DEBUG is enabled."""
    if config.DEBUG:
        print(color + message + Colors.NONE)

# =======================
# Human-Readable Byte Format
# =======================
def hr_bytes(bytes_, suffix='B', si=False):
    """Converts bytes to a human-readable format."""
    bits = 1024.0 if si else 1000.0
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(bytes_) < bits:
            return "{:.1f}{}{}".format(bytes_, unit, suffix)
        bytes_ /= bits
    return "{:.1f}{}{}".format(bytes_, 'Y', suffix)

# =======================
# Traffic Generation Functions
# =======================

# Initialize global traffic meters
data_meter = 0
good_requests = 0
bad_requests = 0

def do_request(url, ue_ip):
    """
    Makes an HTTP GET request to the specified URL bound to the UE's IP.
    Updates global traffic meters.
    """
    global data_meter, good_requests, bad_requests

    debug_print(f"  [{url}] Requesting page...", Colors.PURPLE)

    headers = {'User-Agent': config.USER_AGENT}

    try:
        # Bind the request to the UE's IP address
        response = requests.get(url, headers=headers, timeout=10, proxies={"http": f"http://{ue_ip}", "https": f"http://{ue_ip}"})
        page_size = len(response.content)
        data_meter += page_size

        debug_print(f"  [{url}] Page size: {hr_bytes(page_size)}", Colors.PURPLE)
        debug_print(f"  [{url}] Data meter: {hr_bytes(data_meter)}", Colors.PURPLE)

        status = response.status_code

        if status != 200:
            bad_requests += 1
            debug_print(f"  [{url}] Response status: {status}", Colors.RED)
            if status == 429:
                debug_print(f"  [{url}] Too many requests. Increasing wait times.", Colors.YELLOW)
                config.MIN_WAIT += 2
                config.MAX_WAIT += 2
        else:
            good_requests += 1
            debug_print(f"  [{url}] Response status: {status}", Colors.PURPLE)

        debug_print(f"  [{url}] Good requests: {good_requests}", Colors.PURPLE)
        debug_print(f"  [{url}] Bad requests: {bad_requests}", Colors.PURPLE)

        return response

    except requests.RequestException as e:
        bad_requests += 1
        debug_print(f"  [{url}] Request failed: {e}", Colors.RED)
        return None

def get_links(page_content):
    """
    Extracts all valid links from the page content, excluding blacklisted domains.
    """
    pattern = r'href=["\'](https?://[^"\']+)["\']'
    links = re.findall(pattern, page_content)
    valid_links = [link for link in links if not any(blacklisted in link for blacklisted in config.BLACKLIST)]
    return valid_links

def recursive_browse(url, depth, ue_ip):
    """
    Recursively browses links up to a specified depth.
    """
    debug_print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", Colors.NONE)
    debug_print(f"Recursively browsing [{url}] ~~~ [depth = {depth}]", Colors.PURPLE)

    if depth <= 0:
        # Base case: load current page and return
        do_request(url, ue_ip)
        return
    else:
        # Recursive case: load page, pick random link, and recurse with decremented depth
        response = do_request(url, ue_ip)
        if not response:
            debug_print(f"  [{url}] Stopping and blacklisting: page error", Colors.YELLOW)
            config.BLACKLIST.append(url)
            return

        debug_print(f"  [{url}] Scraping page for links...", Colors.PURPLE)
        valid_links = get_links(response.text)
        debug_print(f"  [{url}] Found {len(valid_links)} valid links.", Colors.PURPLE)

        if not valid_links:
            debug_print(f"  [{url}] Stopping and blacklisting: no links found.", Colors.YELLOW)
            config.BLACKLIST.append(url)
            return

        # Wait before making the next request
        sleep_time = random.uniform(config.MIN_WAIT, config.MAX_WAIT)
        debug_print(f"  [{url}] Pausing for {sleep_time:.2f} seconds...", Colors.PURPLE)
        time.sleep(sleep_time)

        # Choose a random link to continue browsing
        next_url = random.choice(valid_links)
        recursive_browse(next_url, depth - 1, ue_ip)

def simulate_recursive_browsing(ue, root_urls):
    """
    Simulates recursive browsing for a single UE.
    """
    global data_meter, good_requests, bad_requests

    ue_ip = ue['ip']
    imsi = ue['imsi']

    debug_print(f"[{imsi}] Starting recursive browsing simulation.", Colors.PURPLE)

    for root_url in root_urls:
        # Randomly decide the depth for this browsing session
        depth = random.randint(config.MIN_DEPTH, config.MAX_DEPTH)
        debug_print(f"[{imsi}] Browsing {root_url} with depth {depth}.", Colors.PURPLE)
        recursive_browse(root_url, depth, ue_ip)

    debug_print(f"[{imsi}] Recursive browsing simulation completed.", Colors.PURPLE)

# =======================
# UE Lifecycle Management
# =======================

def launch_ue(ue):
    """
    Launches a UERANSIM UE instance using its configuration file.
    """
    ue_config_path = f"/opt/prototype_master/ueransim/configs/ue{ue['imsi']}.yaml"  # Update the path as needed
    ue_command = ["UERANSIM/build/nr-ue", "-c", ue_config_path]
    try:
        ue_proc = subprocess.Popen(ue_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        print(f"[{ue['imsi']}] UE launched with PID {ue_proc.pid}")
        return ue_proc
    except FileNotFoundError:
        print(f"[{ue['imsi']}] UERANSIM UE executable not found. Please check the path.")
        return None
    except Exception as e:
        print(f"[{ue['imsi']}] Error launching UE: {e}")
        return None

def handle_ue(ue, root_urls):
    """
    Handles the lifecycle and traffic simulation for a single UE.
    """
    ue_proc = launch_ue(ue)
    if ue_proc is None:
        return

    # Wait for UE to attach to the network
    print(f"[{ue['imsi']}] Waiting for UE to attach to the network...")
    time.sleep(20)  # Adjust based on your network's attachment time

    # Start recursive browsing simulation
    simulate_recursive_browsing(ue, root_urls)

    # Terminate UE process
    print(f"[{ue['imsi']}] Terminating UERANSIM UE...")
    try:
        os.killpg(os.getpgid(ue_proc.pid), signal.SIGTERM)
        ue_proc.wait()
        print(f"[{ue['imsi']}] UE Terminated.")
    except Exception as e:
        print(f"[{ue['imsi']}] Error terminating UE: {e}")

# =======================
# Main Function
# =======================

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Simulate recursive web traffic for multiple UERANSIM UEs.")
    parser.add_argument('--mqtt-broker-ip', type=str, required=False, help='IP address of the MQTT broker for IoT devices.')
    parser.add_argument('--traffic-types', nargs='+', default=["web_browsing"],
                        help='Types of traffic to simulate. Options: web_browsing')
    args = parser.parse_args()

    mqtt_broker_ip = args.mqtt_broker_ip
    traffic_types = args.traffic_types

    # Filter traffic types (only web_browsing is implemented here)
    if "web_browsing" not in traffic_types:
        print("No supported traffic types selected. Exiting.")
        return

    # Launch threads for each UE
    threads = []
    for ue in UES:
        thread = threading.Thread(target=handle_ue, args=(ue, config.ROOT_URLS))
        thread.start()
        threads.append(thread)
        time.sleep(5)  # Stagger UE launches if necessary

    # Wait for all UE threads to complete
    for thread in threads:
        thread.join()

    print("All UEs have completed traffic generation.")

if __name__ == "__main__":
    main()