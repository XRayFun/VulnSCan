import json
import os
import aiofiles
import random
import re
from typing import List

from _conf import PROXY_JSON_FILE
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


def load_external_servers(protocols:List[str], config_file:str = PROXY_JSON_FILE) -> List[dict]:
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


@logger(_module_name)
def get_random_port_from_json(file_path:str = PROXY_JSON_FILE) -> int:
    """
    Reads a JSON file to get a range of ports and returns a random port in that range.

    :param file_path: Path to the JSON file.
    :return: A random port within the specified range.
    :raises: ValueError if the range is invalid or the JSON format is incorrect.
    """
    try:
        # Load the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Extract port range
        ports = data.get("local_ports", {})
        port_from = ports.get("from")
        port_to = ports.get("to")

        # Validate the range
        if not isinstance(port_from, int) or not isinstance(port_to, int):
            vsc_log.error_result(_module_name, "Invalid port range: 'from' and 'to' must be integers.")
            return random.randint(11000, 12000)
        if port_from > port_to:
            vsc_log.error_result(_module_name, "Invalid port range: 'from' cannot be greater than 'to'.")
            return random.randint(11000, 12000)

        # Generate a random port
        return random.randint(port_from, port_to)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        vsc_log.error_result(_module_name, f"Error reading JSON file: {e}")
        return random.randint(11000, 12000)
