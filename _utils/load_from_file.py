import json
import os
import re
from typing import List, Tuple, Any

import aiofiles
from _log import vsc_log, logger
from _utils.cleaner import get_filtered_list, get_filtered_str

_module_name = "utils.load_from_file"


@logger(_module_name)
async def async_load_targets(input_file:str) -> tuple[List[str], List[str]]:
    ips = []
    domains = []
    vsc_log.info_status_result(_module_name, "LOAD", f"Check IPs and domains in the '{input_file}' file")
    async with aiofiles.open(input_file, mode='r') as f:
        contents = await f.read()
        contents = get_filtered_str(contents)

        # Find all IP addresses
        ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', contents)

        # Find all domains (not IP)
        domains = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', contents)
        domains = [domain for domain in domains if domain not in ips]  # Exclude IP addresses

    ips = get_filtered_list(ips)
    domains = get_filtered_list(domains)

    if ips:
        vsc_log.info_status_result(_module_name, "LOADED", f"IPs: {', '.join(ips)}")
    if domains:
        vsc_log.info_status_result(_module_name, "LOADED", f"Domains: {', '.join(domains)}")
    if not ips and not domains:
        vsc_log.error_status_result(_module_name, "FAILED", f"No IPs or domains found in '{input_file}'")

    return ips, domains


@logger(_module_name)
def load_targets(input_file:str) -> tuple[List[str], List[str]]:
    ips = []
    domains = []
    vsc_log.info_status_result(_module_name, "LOAD", f"Check IPs and domains in the '{input_file}' file")
    with open(input_file, 'r') as file:
        for line in file:
            # Looking for IP addresses in the string
            ip_matches = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
            ips.extend(ip_matches)

            # Looking for domains in the string (excluding IP addresses)
            domain_matches = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', line)
            domains.extend([domain for domain in domain_matches if domain not in ip_matches])

    ips = get_filtered_list(ips)
    domains = get_filtered_list(domains)

    if ips:
        vsc_log.info_status_result(_module_name, "LOADED", f"IPs: {', '.join(ips)}")
    if domains:
        vsc_log.info_status_result(_module_name, "LOADED", f"Domains: {', '.join(domains)}")
    if not ips and not domains:
        vsc_log.error_status_result(_module_name, "FAILED", f"No IPs or domains found in '{input_file}'")

    return ips, domains


def load_external_servers(protocols:List[str], config_file:str) -> List[dict]:
    """
    Loads the external servers from the given JSON configuration file.
    :param protocols: List of protocol names for the remote connection (example: ['ssh', 'ftp']).
    :param config_file: Path to the JSON configuration file.
    :return: List of external server dictionaries with 'host', 'port', 'user', and 'password'.
    """
    if not os.path.exists(config_file):
        vsc_log.error_status_result(_module_name, "ERROR", f"Configuration file '{config_file}' not found.")
        return []

    with open(config_file, 'r') as file:
        data = json.load(file)
        servers = [server for server in data.get("servers", [])
                   if any(protocol in server.get("protocol", []) for protocol in protocols)]
        vsc_log.info_status_result(_module_name, "SUCCESS", f"Loaded {len(servers)} external servers from '{config_file}'")
        return servers

