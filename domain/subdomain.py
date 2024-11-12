import argparse
import asyncio
from datetime import datetime
from typing import List, Tuple, Any

import aiofiles

from _conf import COMMON_SUBDOMAINS, BRUTEFORCE_FILE, BRUTEFORCE_LEVEL, BRUTEFORCE_OUTPUT_FOLDER, BRUTEFORCE_OUTPUT_FORMAT, BRUTEFORCE_ASYNC_PROCESSES
from _log import vsc_log, logger
from _utils import async_load_targets, get_filtered_list, start_monitor, stop_monitor
from domain import resolve_domain
from domain.subdomain_dns_scanner import collect_subdomains


_module_name = "domain.subdomain"


@logger(_module_name)
async def limited_resolve_ips(domains:list, max_concurrent:int=BRUTEFORCE_ASYNC_PROCESSES, output_folder:str=BRUTEFORCE_OUTPUT_FOLDER, **kwargs) -> tuple[Any]:
    semaphore = asyncio.Semaphore(max_concurrent)

    output_file_path = f"{output_folder}domain.subdomain {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.txt" if output_folder else None
    output_file = await aiofiles.open(output_file_path, mode='w') if output_file_path else None

    @logger(_module_name)
    async def resolve_with_limit(domain:str) -> List[str]:
        async with semaphore:
            try:
                return await resolve_ips(domain, output_file, **kwargs)
            except Exception as e:
                vsc_log.error_status_result(_module_name, "ERROR", f"Error resolving domain '{domain}': {e}")
                return []

    vsc_log.info_status_result(_module_name, "STARTED", "The search for subdomains has begun")
    tasks = [resolve_with_limit(domain) for domain in domains]
    results = await asyncio.gather(*tasks)

    # Closing a file if it has been opened
    if output_file:
        await output_file.close()
        vsc_log.info_status_result(_module_name, "COMPLETE", f"Results saved to '{output_file_path}' file")

    return results


@logger(_module_name)
async def resolve_ips(domain:str, output_file:aiofiles, level:int=BRUTEFORCE_LEVEL, brute_force_file:str=BRUTEFORCE_FILE, output_format:str=BRUTEFORCE_OUTPUT_FORMAT) -> List[str]:
    found_ips = set()  # To store unique IP addresses

    @logger(_module_name)
    async def search_subdomains(current_domain:str, current_level:int):
        if current_level > 0:
            subdomains = collect_subdomains(current_domain) + [f"{sub}.{current_domain}" for sub in COMMON_SUBDOMAINS]
        else:
            subdomains = [current_domain]

        if brute_force_file and current_level > 0:
            additional_subdomains = await _load_subdomains_from_file(brute_force_file)
            subdomains.extend([f"{sub}.{current_domain}" for sub in additional_subdomains])


        subdomains = get_filtered_list(subdomains)
        resolved_ips = []

        try:
            resolved_ips = await asyncio.gather(*[resolve_domain(sub) for sub in subdomains])
        except Exception as exe:
            vsc_log.error_status_result(_module_name, "ERROR", f"Failed resolve_domain!\n{exe}")

        resolved_ips = get_filtered_list(resolved_ips)
        for ip in resolved_ips:
            found_ips.add(ip)

        if resolved_ips:
            # Recording results to a file as they are received
            if output_file:
                if output_format == 'domain-ip':
                    await output_file.write(f"{current_domain} - {', '.join(resolved_ips)}\n")
                elif output_format == 'ip':
                    await output_file.write(f"{', '.join(resolved_ips)}\n")

        if current_level < level:
            tasks = [search_subdomains(sub, current_level + 1) for sub in subdomains]
            await asyncio.gather(*tasks)

    # Processing of each domain
    try:
        await search_subdomains(domain, 0)
    except Exception as e:
        vsc_log.error_status_result(_module_name, "ERROR", f"Failed resolve_ips_from_subdomains for '{domain}'\n{e}")

    return get_filtered_list(found_ips)  # Return found IP addresses


@logger(_module_name)
async def _load_subdomains_from_file(file_path:str) -> List[str]:
    subdomains = []
    async with aiofiles.open(file_path, mode='r') as f:
        async for line in f:
            subdomain = line.strip()
            if subdomain and not subdomain.startswith('#'):
                subdomains.append(subdomain)
    subdomains = get_filtered_list(subdomains)
    vsc_log.info_status_result(_module_name, "LOADED", f"{len(subdomains)} subdomains from '{file_path}'")
    return subdomains


@logger(_module_name)
def main(remaining_args):
    parser = argparse.ArgumentParser(description="Subdomain resolution module")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-ds', '--domains', help="Comma-separated list of domains (no spaces)")
    group.add_argument('-iF', '--input-file', help="Path to a file with comma-separated domains")

    parser.add_argument('-dBL', '--level', type=int, default=BRUTEFORCE_LEVEL,
                        help="Level of subdomain brute-forcing (default: BRUTEFORCE_LEVEL)")
    parser.add_argument('-aP', '--async-processes', type=int, default=BRUTEFORCE_ASYNC_PROCESSES,
                        help=f"Number of parallel scanning processes (default is {BRUTEFORCE_ASYNC_PROCESSES})")
    parser.add_argument('-dBF', '--brute-force-file', default=BRUTEFORCE_FILE,
                        help="Path to brute-force subdomains file (default: BRUTEFORCE_FILE)")
    parser.add_argument('-oF', '--output-folder', default=BRUTEFORCE_OUTPUT_FOLDER,
                        help="Output folder for results")
    parser.add_argument('-oFmt', '--output-format', choices=['domain-ip', 'ip'], default='domain-ip',
                        help="Output format: 'domain-ip' or 'ip' (default: 'domain-ip')")
    args = parser.parse_args(remaining_args)

    domains = []
    if args.domains:
        domains = [domain.strip() for domain in args.domains.split(',')]
    elif args.input_file:
        _, domains = asyncio.run(async_load_targets(args.input_file))

    domains = get_filtered_list(domains)
    monitor_id = start_monitor()
    # Running asynchronous search for all domains
    asyncio.run(limited_resolve_ips(
        domains=domains,
        max_concurrent=args.async_processes,
        level=args.level,
        brute_force_file=args.brute_force_file,
        output_folder=args.output_folder,
        output_format=args.output_format
    ))
    stop_monitor(monitor_id)
