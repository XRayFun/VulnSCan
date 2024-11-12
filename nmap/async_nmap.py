import asyncio
import subprocess
import os
import argparse
import sys

from _conf import NMAP_OUTPUT_FOLDER, NMAP_PARAMS, NMAP_ASYNC_PROCESSES, BRUTEFORCE_LEVEL, BRUTEFORCE_FILE
from _log import vsc_log, logger
from _utils import async_load_targets, check_internet_connection, start_monitor, stop_monitor, get_filtered_list
from domain import limited_resolve_ips


_module_name = "nmap.async_nmap"


@logger(_module_name)
async def _scan_ip(ip:str, nmap_params:str, output_folder:str):
    finished_file_name = os.path.join(output_folder, f"nmap.async_finished_{ip}.xml")
    if os.path.exists(finished_file_name):
        vsc_log.info_ip_status_result(_module_name, ip, "SKIPPED", f"The '{finished_file_name}' file already exists.")
        return

    connection_monitor_id = start_monitor()

    output_file = os.path.join(output_folder, f"nmap.async_{ip}.xml")
    if os.path.exists(output_file):
        vsc_log.info_result(_module_name, f"The '{output_file}' file already exists. It will be overwritten.")

    vsc_log.info_ip_status_result(_module_name, ip, "SCANNING", f"Starts!")

    try:
        process = await asyncio.create_subprocess_exec(
            "nmap", *nmap_params.split(), "-oX", output_file, ip,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        vsc_log.info_ip_status_result(_module_name, ip, "FINISHED", f"\n{stdout.decode()}")
        if stderr:
            vsc_log.warn_ip_result(_module_name, ip, f"Error when scanning:\n{stderr.decode()}")

        vsc_log.info_result(_module_name, f"File renamed from {output_file} to {finished_file_name}")
        os.rename(output_file, finished_file_name)

    except Exception as e:
        vsc_log.error_ip_result(_module_name, ip, f"Error when scanning:\n{e}")

    stop_monitor(connection_monitor_id)


@logger(_module_name)
async def _start_scan(args):
    domains = []
    ips = []

    if args.ip_addresses:
        targets = args.ip_addresses.split(',')
        domains = [t.strip() for t in targets if not t.replace('.', '').isdigit()]
        ips = [t.strip() for t in targets if t.replace('.', '').isdigit()]
    else:
        ips, domains = await async_load_targets(args.input_file)

    resolved_ips = []
    domains = get_filtered_list(domains)
    if domains:
        domain_ips = await limited_resolve_ips(
            domains=domains,
            max_concurrent=args.async_processes,
            level=args.brute_force_level,
            brute_force_file=args.brute_force_file
        )
        resolved_ips.extend(domain_ips)

    all_ips = get_filtered_list(ips + resolved_ips)
    vsc_log.info_result(_module_name, f"Starts scanning to: {', '.join(all_ips)}")
    tasks = [_scan_ip(ip, args.nmap_params, args.output_folder) for ip in all_ips]

    # Restriction on parallel processes
    semaphore = asyncio.Semaphore(args.async_processes)

    @logger(_module_name)
    async def limited_task(task):
        async with semaphore:
            await task

    await asyncio.gather(*(limited_task(task) for task in tasks))


@logger(_module_name)
def main(remaining_args):
    parser = argparse.ArgumentParser(description="Asynchronous scanning with Nmap and Subdomain Resolution.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-iF', '--input-file',
                        help="Path to the IP addresses or domains included file")
    group.add_argument('-ips', '--ip-addresses',
                        help="List of IP addresses or domains, comma separated (no spaces), to be checked")

    parser.add_argument('-oF', '--output-folder', default=NMAP_OUTPUT_FOLDER,
                        help=f"Folder path for results (default is the '{NMAP_OUTPUT_FOLDER}' folder)")
    parser.add_argument('-nmap-params', default=NMAP_PARAMS,
                        help=f"Parameters for nmap (default '{NMAP_PARAMS}')")
    parser.add_argument('-aP', '--async-processes', type=int, default=NMAP_ASYNC_PROCESSES,
                        help=f"Number of parallel scanning processes (default is {NMAP_ASYNC_PROCESSES})")
    parser.add_argument('-dBL','--brute-force-level',type=int, default=BRUTEFORCE_LEVEL,
                        help=f"Level brute-forcing subdomains (default is {BRUTEFORCE_LEVEL})")
    parser.add_argument('-dBF', '--brute-force-file', default=BRUTEFORCE_FILE,
                        help=f"Path to file with subdomains for brute-forcing (default is {BRUTEFORCE_FILE})")

    args = parser.parse_args(remaining_args)

    if not check_internet_connection():
        vsc_log.error_result(_module_name, "Unable to execute script, no internet connection!")
        sys.exit(1)

    # Start scanning
    asyncio.run(_start_scan(args))
