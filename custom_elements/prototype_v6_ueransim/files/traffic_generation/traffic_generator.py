import subprocess
import os
import signal
import sys
import time

UERANSIM_PATH = "/UERANSIM/build"
GNBNAME = "gnb"
UE_NAMES = ["ue_1", "ue_2", "ue_3"]
CONFIG_DIR = "/opt/prototype_master/ueransim"

def launch_gnb():
    gnb_config = os.path.join(CONFIG_DIR, "gnb_config.yaml")
    if not os.path.isfile(gnb_config):
        print(f"gNB configuration file not found: {gnb_config}")
        sys.exit(1)
    
    gnb_executable = os.path.join(UERANSIM_PATH, "nr-gnb")
    if not os.path.isfile(gnb_executable):
        print(f"gNB executable not found: {gnb_executable}")
        sys.exit(1)
    
    print("Launching gNB...")
    gnb_proc = subprocess.Popen([gnb_executable, "-c", gnb_config], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return gnb_proc

def launch_ue(ue_name):
    ue_config = os.path.join(CONFIG_DIR, f"{ue_name}_config.yaml")
    if not os.path.isfile(ue_config):
        print(f"UE configuration file not found: {ue_config}")
        sys.exit(1)
    
    ue_executable = os.path.join(UERANSIM_PATH, "nr-ue")
    if not os.path.isfile(ue_executable):
        print(f"UE executable not found: {ue_executable}")
        sys.exit(1)
    
    print(f"Launching {ue_name}...")
    ue_proc = subprocess.Popen([ue_executable, "-c", ue_config], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return ue_proc

def main():
    processes = []

    try:
        gnb_proc = launch_gnb()
        processes.append(gnb_proc)
        time.sleep(4)

        for ue_name in UE_NAMES:
            ue_proc = launch_ue(ue_name)
            processes.append(ue_proc)
            time.sleep(1)

        print("All processes launched. Press Ctrl+C to terminate.")
        while True:
            for proc in processes:
                if proc.poll() is not None:
                    print(f"Process {proc.pid} terminated.")
                    sys.exit(1)
                line = proc.stdout.readline()
                if line:
                    print(line.decode().strip())
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nTerminating all processes...")
        for proc in processes:
            proc.send_signal(signal.SIGINT)
        for proc in processes:
            proc.wait()
        print("All processes terminated.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        for proc in processes:
            proc.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
