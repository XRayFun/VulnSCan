import json
import dns.resolver
import subprocess
import requests
import re
from typing import List

from _log import scan_log, logger
from _utils import get_filtered_list


_module_name = "domain.dns_finder"


# Function for searching subdomains with crt.sh
@logger(_module_name)
def _find_subdomains_crtsh(v_domain: str) -> List[str]:
    url = f'https://crt.sh/?q={v_domain}&output=json'
    response = requests.get(url)
    v_subdomains = []

    # Checking the status and availability of data
    if response.status_code == 200:
        try:
            data = response.json()
            v_subdomains = [entry['name_value'] for entry in data if 'name_value' in entry]
        except json.JSONDecodeError:
            scan_log.warn_status_result(_module_name, "FAILED", "Failed to decode JSON. The response is probably empty or not in JSON format.")
    else:
        scan_log.error_status_result(_module_name, "ERROR", f"Error when requesting crt.sh: response status {response.status_code}")

    return list(v_subdomains)


# Function for searching subdomains using DNS queries (dnspython)
@logger(_module_name)
def _find_subdomains_dns(v_domain: str) -> List[str]:
    v_subdomains = []
    try:
        result = dns.resolver.resolve(v_domain, 'NS')
        for ns in result:
            v_subdomains.append(ns.to_text())
    except Exception as e:
        scan_log.error_status_result(_module_name, "ERROR", f"Error when requesting DNS Resolver: {e}")
    return list(v_subdomains)


# Function for collecting subdomains using Subfinder
@logger(_module_name)
def _find_subdomains_subfinder(v_domain: str) -> List[str]:
    v_subdomains = []
    try:
        result = subprocess.run(['subfinder', '-d', v_domain, '-silent'], capture_output=True, text=True)
        if result.returncode == 0:
            v_subdomains = result.stdout.strip().splitlines()
        else:
            scan_log.warn_status_result(_module_name, "FAILED", f"Subfinder execution error: {result.stderr}")
    except Exception as e:
        scan_log.error_status_result(_module_name, "ERROR", f"Error when starting subfinder: {e}")
    return list(v_subdomains)


# Function for collecting subdomains using DNSDumpster
@logger(_module_name)
def _find_subdomains_dnsdumpster(v_domain: str) -> List[str]:
    url = f"https://dnsdumpster.com/"
    v_subdomains = set()

    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = session.get(url, headers=headers, params={'url': v_domain})

        if response.status_code == 200:
            v_subdomains = re.findall(r"([a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,})", response.text)
    except Exception as e:
        scan_log.warn_status_result(_module_name, "FAILED", f"DNSDumpster query error: {e}")

    return list(v_subdomains)


# The main function for collecting subdomains
@logger(_module_name)
def collect_subdomains(target_domain: str) -> List[str]:
    all_subdomains = set()
    scan_log.info_status_result(_module_name, "SCANNING", f"Running DNS scanning of subdomains for '{target_domain}'")
    # Collecting subdomains using different methods
    all_subdomains.update(_find_subdomains_crtsh(target_domain))
    all_subdomains.update(_find_subdomains_dns(target_domain))
    all_subdomains.update(_find_subdomains_subfinder(target_domain))
    all_subdomains.update(_find_subdomains_dnsdumpster(target_domain))

    # Keep only subdomains containing the main domain
    all_subdomains = {sub for sub in all_subdomains if target_domain in sub}
    all_subdomains = get_filtered_list(all_subdomains)

    if not all_subdomains:
        scan_log.warn_status_result(_module_name, "FAILED", f"No subdomains detected for '{target_domain}'")
    else:
        scan_log.info_status_result(_module_name, "RESOLVED", f"From {target_domain} : {', '.join(all_subdomains)}")
    # Returning unique subdomains
    return all_subdomains


if __name__ == "__main__":
    domain = input("Target domain: ").strip()

    subdomains = collect_subdomains(domain)

    print(f"\nFounded {len(subdomains)} subdomains for {domain}:")
    for subdomain in subdomains:
        print(subdomain)
