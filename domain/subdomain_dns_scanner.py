import json
import dns.resolver
import subprocess
import requests
import re
from typing import List

from _log import scan_log


_module_name = "domain.dns_finder"

# Function for searching subdomains with crt.sh
def find_subdomains_crtsh(domain):
    url = f'https://crt.sh/?q={domain}&output=json'
    response = requests.get(url)
    subdomains = []

    # Checking the status and availability of data
    if response.status_code == 200:
        try:
            data = response.json()
            subdomains = [entry['name_value'] for entry in data if 'name_value' in entry]
        except json.JSONDecodeError:
            scan_log.warn_status_result(_module_name, "FAILED", "Failed to decode JSON. The response is probably empty or not in JSON format.")
    else:
        scan_log.error_status_result(_module_name, "ERROR", f"Error when requesting crt.sh: response status {response.status_code}")

    return subdomains


# Function for searching subdomains using DNS queries (dnspython)
def find_subdomains_dns(domain):
    subdomains = []
    try:
        result = dns.resolver.resolve(domain, 'NS')
        for ns in result:
            subdomains.append(ns.to_text())
    except:
        pass
    return subdomains


# Function for collecting subdomains using Subfinder
def find_subdomains_subfinder(domain: str) -> List[str]:
    subdomains = []
    try:
        result = subprocess.run(['subfinder', '-d', domain, '-silent'], capture_output=True, text=True)
        if result.returncode == 0:
            subdomains = result.stdout.strip().splitlines()
        else:
            scan_log.warn_status_result(_module_name, "FAILED", f"Subfinder execution error: {result.stderr}")
    except Exception as e:
        scan_log.error_status_result(_module_name, "ERROR", f"Error when starting subfinder: {e}")
    return subdomains


# Function for collecting subdomains using DNSDumpster
def find_subdomains_dnsdumpster(domain: str) -> List[str]:
    url = f"https://dnsdumpster.com/"
    subdomains = set()

    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = session.get(url, headers=headers, params={'url': domain})

        if response.status_code == 200:
            subdomains = re.findall(r"([a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,})", response.text)
    except Exception as e:
        scan_log.warn_status_result(_module_name, "FAILED", f"DNSDumpster query error: {e}")

    return list(set(subdomains))


# The main function for collecting subdomains
def collect_subdomains(domain):
    all_subdomains = set()
    scan_log.info_status_result(_module_name, "SCANNING", f"Running DNS scanning of subdomains for '{domain}'")
    # Collecting subdomains using different methods
    all_subdomains.update(find_subdomains_crtsh(domain))
    all_subdomains.update(find_subdomains_dns(domain))
    all_subdomains.update(find_subdomains_subfinder(domain))
    all_subdomains.update(find_subdomains_dnsdumpster(domain))

    # Keep only subdomains containing the main domain
    all_subdomains = {sub for sub in all_subdomains if domain in sub}

    if not all_subdomains:
        scan_log.warn_status_result(_module_name, "FAILED", f"No subdomains detected for '{domain}'")
    else:
        scan_log.info_status_result(_module_name, "RESOLVED", f"From {domain} : {', '.join(all_subdomains)}")
    # Returning unique subdomains
    return list(all_subdomains)


if __name__ == "__main__":
    domain = input("Target domain: ").strip()

    subdomains = collect_subdomains(domain)

    print(f"\nFounded {len(subdomains)} subdomains for {domain}:")
    for subdomain in subdomains:
        print(subdomain)
