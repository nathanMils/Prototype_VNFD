import socks
import socket
import subprocess
import argparse

def run_nmap(target_ip, ports, proxy_host, proxy_port):
    socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
    socket.socket = socks.socksocket

    nmap_command = ["nmap", "-p", ports, target_ip]
    
    try:
        print(f"Running Nmap scan on {target_ip} for ports {ports} using SOCKS proxy {proxy_host}:{proxy_port}...")
        result = subprocess.run(nmap_command, capture_output=True, text=True)
        
        print(result.stdout)
        print(result.stderr)
    except Exception as e:
        print(f"Error running Nmap: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Nmap through a SOCKS proxy.")
    parser.add_argument("target_ip", help="Target IP address to scan.")
    parser.add_argument("ports", help="Comma-separated list of ports or port ranges (e.g., 1-1024).")
    parser.add_argument("proxy_host", help="SOCKS proxy host address.")
    parser.add_argument("proxy_port", type=int, help="SOCKS proxy port.")

    args = parser.parse_args()
    
    run_nmap(args.target_ip, args.ports, args.proxy_host, args.proxy_port)
