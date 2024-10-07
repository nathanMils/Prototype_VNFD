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
            cmd = cmd + '--http2-prior-knowledge '
        cmd = cmd + f'http://{nrf_ip}:{nrf_port}/nnrf-nfm/v1/nf-instances?nf-type='
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

def check_ip_in_response(response, ip, vnf_name):
    logging.debug(f"Response for {vnf_name}: {response}")
    try:
        data = json.loads(response)
        logging.debug(f"Parsed JSON data for {vnf_name}: {json.dumps(data, indent=2)}")
        items = data.get('_links', {}).get('item', [])
        for item in items:
            if ip in item.get('href', ''):
                print(f"\033[0;32m{vnf_name}: {ip}\033[0m")
                return True
        print(f"\033[0;31m{vnf_name}: Error\033[0m")
        return False
    except json.JSONDecodeError:
        logging.error(f"{vnf_name}: Invalid JSON response")
        print(f"\033[0;31m{vnf_name}: Invalid JSON response\033[0m")
        return False

def check_config_and_output_responses(nrf_ip):
    curl_cmd = generate_nrf_curl_cmd(nrf_ip)

    logging.debug('\033[0;34mChecking if the NFs are configured\033[0m....')
    logging.debug('\033[0;34mChecking if AMF, SMF and UPF registered with nrf core network\033[0m....')

    cmd = f'{curl_cmd}"AMF"'
    amf_response = run_cmd(cmd, False)
    if amf_response is not None:
        check_ip_in_response(amf_response, nrf_ip, "AMF")

    cmd = f'{curl_cmd}"SMF"'
    smf_response = run_cmd(cmd, False)
    if smf_response is not None:
        check_ip_in_response(smf_response, nrf_ip, "SMF")

    cmd = f'{curl_cmd}"UPF"'
    upf_response = run_cmd(cmd, False)
    if upf_response is not None:
        check_ip_in_response(upf_response, nrf_ip, "UPF")

    logging.debug('\033[0;34mChecking if AUSF, UDM and UDR registered with nrf core network\033[0m....')

    cmd = f'{curl_cmd}"AUSF"'
    ausf_response = run_cmd(cmd, False)
    if ausf_response is not None:
        check_ip_in_response(ausf_response, nrf_ip, "AUSF")

    cmd = f'{curl_cmd}"UDM"'
    udm_response = run_cmd(cmd, False)
    if udm_response is not None:
        check_ip_in_response(udm_response, nrf_ip, "UDM")

    cmd = f'{curl_cmd}"UDR"'
    udr_response = run_cmd(cmd, False)
    if udr_response is not None:
        check_ip_in_response(udr_response, nrf_ip, "UDR")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Health check script for NRF")
    parser.add_argument("--nrf_ip", required=True, help="NRF IP address")
    args = parser.parse_args()

    check_config_and_output_responses(args.nrf_ip)
