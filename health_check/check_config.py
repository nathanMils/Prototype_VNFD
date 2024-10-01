import yaml
import re
import subprocess
import time
import logging
import argparse
import sys

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

nrf_ip = ""
amf_ip = ""
smf_ip = ""
gpp_ip = "192.168.70.201"
ausf_ip = ""
udm_ip = ""
udr_ip = ""

def generate_nrf_curl_cmd():
    # if not found, there is an exception here, but it is fine because then we have to update our scenarios
    conf_file = 'conf/basic_vpp_nrf_config.yaml'
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
    except:
        pass
    return result

def check_config(file_name):
    curl_cmd = generate_nrf_curl_cmd()
    deployStatus = True

    logging.debug('\033[0;34m Checking if the NFs are configured\033[0m....')
    logging.debug('\033[0;34m Checking if AMF, SMF and UPF registered with nrf core network\033[0m....')

    cmd = f'{curl_cmd}"AMF" | grep -o "{amf_ip}"'
    amf_registration_nrf = run_cmd(cmd, False)
    if amf_registration_nrf is not None:
        print(amf_registration_nrf)

    cmd = f'{curl_cmd}"SMF" | grep -o "{smf_ip}"'
    smf_registration_nrf = run_cmd(cmd, False)
    if smf_registration_nrf is not None:
        print(smf_registration_nrf)

    cmd = f'{curl_cmd}"UPF" | grep -o "{gpp_ip}"'
    upf_registration_nrf = run_cmd(cmd, False)
    if upf_registration_nrf is not None:
        print(upf_registration_nrf)

    logging.debug('\033[0;34m Checking if AUSF, UDM and UDR registered with nrf core network\033[0m....')

    cmd = f'{curl_cmd}"AUSF" | grep -o "{ausf_ip}"'
    ausf_registration_nrf = run_cmd(cmd, False)
    if ausf_registration_nrf is not None:
        print(ausf_registration_nrf)

    cmd = f'{curl_cmd}"UDM" | grep -o "{udm_ip}"'
    udm_registration_nrf = run_cmd(cmd, False)
    if udm_registration_nrf is not None:
        print(udm_registration_nrf)
    cmd = f'{curl_cmd}"UDR" | grep -o "{udr_ip}"'
    udr_registration_nrf = run_cmd(cmd, False)
    if udr_registration_nrf is not None:
        print(udr_registration_nrf)
    
    if amf_registration_nrf is None or smf_registration_nrf is None or upf_registration_nrf is None or \
        ausf_registration_nrf is None or udm_registration_nrf is None or udr_registration_nrf is None:
            logging.error('\033[0;31m Registration problem with NRF, check the reason manually\033[0m....')
            deployStatus = False
    else:
        logging.debug('\033[0;32m AUSF, UDM, UDR, AMF, SMF and UPF are registered to NRF\033[0m....')

    # logging.debug('\033[0;34m Checking if SMF is able to connect with UPF\033[0m....')

    # cmd1 = 'docker logs oai-smf 2>&1 | grep "Received N4 ASSOCIATION SETUP RESPONSE from an UPF"'
    # cmd2 = 'docker logs oai-smf 2>&1 | grep "Node ID Type FQDN: vpp-upf"'
    # upf_logs1 = run_cmd(cmd1)
    # upf_logs2 = run_cmd(cmd2)
    # if upf_logs1 is None or upf_logs2 is None:
    #     logging.error('\033[0;31m UPF did not answer to N4 Association request from SMF\033[0m....')
    #     deployStatus = False
    # else:
    #     logging.debug('\033[0;32m UPF did answer to N4 Association request from SMF\033[0m....')
    # cmd1 = 'docker logs oai-smf 2>&1 | grep "PFCP HEARTBEAT PROCEDURE"'
    # upf_logs1 = run_cmd(cmd1)
    # if upf_logs1 is None:
    #     logging.error('\033[0;31m SMF is NOT receiving heartbeats from UPF\033[0m....')
    #     deployStatus = False
    # else:
    #     logging.debug('\033[0;32m SMF is receiving heartbeats from UPF\033[0m....')
