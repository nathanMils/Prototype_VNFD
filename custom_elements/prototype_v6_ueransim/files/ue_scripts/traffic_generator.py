import os
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Configuration for gNB
CONFIG_PATH = "/path/to/ueransim/config"
GNB_CONFIG = os.path.join(CONFIG_PATH, "gnb.yaml")
UE_CONFIG_DIR = os.path.join(CONFIG_PATH, "ue_configs")  # Directory containing UE config files

# CLI command for nr-cli
NR_CLI = "./nr-cli"  # Path to your nr-cli executable

def start_gnb():
    """Start the gNodeB."""
    print("Starting gNodeB...")
    gnb_command = ["ueransim", "-c", GNB_CONFIG]
    gnb_process = subprocess.Popen(gnb_command)
    time.sleep(5)  # Wait for gNB to start
    print("gNodeB started.")
    return gnb_process

def start_ue(ue_config):
    """Start a single User Equipment (UE)."""
    print(f"Starting UE with config: {ue_config}...")
    ue_command = ["ueransim", "-c", ue_config]
    ue_process = subprocess.Popen(ue_command)
    time.sleep(2)  # Wait for UE to start
    print(f"UE with config {ue_config} started.")
    return ue_process

def generate_traffic(ue_id, pdu_session_ip):
    """Generate web traffic using headless Firefox."""
    print(f"Starting headless Firefox for UE {ue_id}...")

    # Set Firefox options for headless mode
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Start Firefox with the specified options
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    try:
        # Open a webpage that generates traffic
        driver.get(f"http://{pdu_session_ip}")  # Navigate to the PDU session IP
        time.sleep(10)  # Wait for a while to simulate user interaction
    except Exception as e:
        print(f"Error generating traffic for UE {ue_id}: {e}")
    finally:
        driver.quit()
        print(f"Traffic generation for UE {ue_id} completed.")

def terminate_pdu_session(ue_id):
    """Terminate the PDU session for the given UE using nr-cli."""
    print(f"Terminating PDU session for UE {ue_id}...")
    terminate_command = [NR_CLI, ue_id, "--exec", "detach"]
    result = subprocess.run(terminate_command, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"PDU session for UE {ue_id} terminated successfully.")
    else:
        print(f"Failed to terminate PDU session for UE {ue_id}. Output: {result.stderr}")

def main():
    """Main function to start gNB and UEs."""
    try:
        gnb_process = start_gnb()

        # List all UE config files in the specified directory
        ue_config_files = [os.path.join(UE_CONFIG_DIR, f) for f in os.listdir(UE_CONFIG_DIR) if f.endswith('.yaml')]
        ue_processes = []

        # Start each UE with its corresponding config file
        for ue_config in ue_config_files:
            ue_process = start_ue(ue_config)
            ue_processes.append(ue_process)

            # Here you would extract the PDU session IP for each UE configuration
            pdu_session_ip = "192.168.1.2"  # Replace with the actual PDU session IP for each UE
            generate_traffic(os.path.basename(ue_config).replace('.yaml', ''), pdu_session_ip)

            # Execute commands with nr-cli
            ue_id = os.path.basename(ue_config).replace('.yaml', '')  # Extracting UE ID from filename
            subprocess.run([NR_CLI, ue_id, "--exec", "status"])  # Example command to check status

        # Keep the script running to manage gNB and UEs
        print("Press Ctrl+C to stop...")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping UEs...")
        for ue_process in ue_processes:
            ue_id = os.path.basename(ue_config).replace('.yaml', '')  # Extracting UE ID from filename
            terminate_pdu_session(ue_id)  # Terminate PDU session before shutting down UE
            ue_process.terminate()
            ue_process.wait()
            print(f"UE {ue_id} terminated.")

        print("Stopping gNodeB...")
        gnb_process.terminate()
        gnb_process.wait()
        print("gNodeB terminated.")

if __name__ == "__main__":
    main()
