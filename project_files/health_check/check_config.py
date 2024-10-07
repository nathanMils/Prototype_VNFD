import yaml
import subprocess
import logging
import argparse
import sys
import json

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

def generate_nrf_curl_cmd(nrf_ip):
    conf_file = './conf/basic_vpp_nrf_config.yaml'
    with open(conf_file) as f:
        y = yaml.safe_load(f)
        http_version = y.get('http_version', 1)
        nrf_port = 80

        if y.get('nfs') and y['nfs'].get('nrf'):
            nrf_cfg = y['nfs']['nrf']
            if nrf_cfg.get('sbi') and nrf_cfg['sbi'].get('port'):
                nrf_port = nrf_cfg['sbi']['port']

        cmd = 'curl -s -X GET '
        if http_version == 2:
            cmd += '--http2-prior-knowledge '
        cmd += f'http://{nrf_ip}:{nrf_port}/nnrf-nfm/v1/nf-instances?nf-type='
        return cmd
    
def run_cmd(cmd, silent=True):
    if not silent:
        logging.debug(cmd)
    result = None
    try:
        res = subprocess.run(cmd,
                              shell=True, check=True,
                              stdout=subprocess.PIPE,
                              universal_newlines=True)
        result = res.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with error: {e}")
    return result

def check_ip_in_response(response, vnf_name):
    logging.debug(f"Response for {vnf_name}: {response}")
    try:
        data = json.loads(response)
        logging.debug(f"Parsed JSON data for {vnf_name}: {json.dumps(data, indent=2)}")
        items = data.get('_links', {}).get('item', [])
        if items:
            # Check if there is any 'href' with an IP-like value
            for item in items:
                if 'href' in item and item['href']:  # If href exists and is non-empty
                    logging.info(f"{vnf_name}: Registered successfully with IP: {item['href']}")
                    return True
        logging.error(f"{vnf_name}: Error, no registration")
        return False
    except json.JSONDecodeError:
        logging.error(f"{vnf_name}: Invalid JSON response")
        return False

def check_config_and_output_responses(nrf_ip):
    curl_cmd = generate_nrf_curl_cmd(nrf_ip)

    logging.debug('Checking if the NFs are configured....')
    logging.debug('Checking if AMF, SMF and UPF registered with nrf core network....')

    # Check each VNF
    for vnf in ["AMF", "SMF", "UPF", "AUSF", "UDM", "UDR"]:
        cmd = f'{curl_cmd}"{vnf}"'  # Correctly formatted command
        response = run_cmd(cmd, False)
        if response is not None:
            check_ip_in_response(response, vnf)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Health check script for NRF")
    parser.add_argument("--nrf_ip", required=True, help="NRF IP address")
    args = parser.parse_args()

    check_config_and_output_responses(args.nrf_ip)
