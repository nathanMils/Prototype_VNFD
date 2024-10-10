import socks
import socket
import subprocess

# Configure SOCKS proxy settings
SOCKS_PROXY_HOST = '172.24.4.64'  # Address of the SOCKS proxy server
SOCKS_PROXY_PORT = 1080         # Port of the SOCKS proxy server

# Set up the SOCKS proxy for outgoing connections
socks.set_default_proxy(socks.SOCKS5, SOCKS_PROXY_HOST, SOCKS_PROXY_PORT)
socket.socket = socks.socksocket

# Curl command to test the connection through SOCKS proxy
url = 'https://www.google.com'  # URL to request via curl
curl_command = ['curl', '-x', f'socks5://{SOCKS_PROXY_HOST}:{SOCKS_PROXY_PORT}', url]

try:
    # Run the curl command via the SOCKS proxy
    result = subprocess.run(curl_command, capture_output=True, text=True)
    
    # Print the output of the curl command
    print(result.stdout)
except Exception as e:
    print(f"Error: {e}")
