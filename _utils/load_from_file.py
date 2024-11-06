import re
import aiofiles
from _log import scan_log


_module_name = "utils.load_from_file"


async def async_load_targets(input_file):
    ips = []
    domains = []
    scan_log.info_status_result(_module_name, "LOAD", f"Check IPs and domains in the '{input_file}' file")
    async with aiofiles.open(input_file, mode='r') as f:
        contents = await f.read()
        contents = contents.replace(" ", "").replace("\n", "").replace("\r", "")

        # Find all IP addresses
        ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', contents)

        # Find all domains (not IP)
        domains = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', contents)
        domains = [domain for domain in domains if domain not in ips]  # Exclude IP addresses

    if ips:
        scan_log.info_status_result(_module_name, "LOADED", f"IPs: {', '.join(ips)}")
    if domains:
        scan_log.info_status_result(_module_name, "LOADED", f"Domains: {', '.join(domains)}")
    if not ips and not domains:
        scan_log.error_status_result(_module_name, "FAILED", f"No IPs or domains found in '{input_file}'")

    return ips, domains


def load_targets(input_file):
    ips = []
    domains = []
    scan_log.info_status_result(_module_name, "LOAD", f"Check IPs and domains in the '{input_file}' file")
    with open(input_file, 'r') as file:
        for line in file:
            # Looking for IP addresses in the string
            ip_matches = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
            ips.extend(ip_matches)

            # Looking for domains in the string (excluding IP addresses)
            domain_matches = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', line)
            domains.extend([domain for domain in domain_matches if domain not in ip_matches])

    if ips:
        scan_log.info_status_result(_module_name, "LOADED", f"IPs: {', '.join(ips)}")
    if domains:
        scan_log.info_status_result(_module_name, "LOADED", f"Domains: {', '.join(domains)}")
    if not ips and not domains:
        scan_log.error_status_result(_module_name, "FAILED", f"No IPs or domains found in '{input_file}'")

    return ips, domains
