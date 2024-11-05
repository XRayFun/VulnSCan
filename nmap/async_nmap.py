import asyncio
import subprocess
import os
import argparse
import sys

from _conf import NMAP_OUTPUT_FOLDER, NMAP_PARAMS, NMAP_ASYNC_PROCESSES, BRUTEFORCE_LEVEL, BRUTEFORCE_FILE
from _log import log_error, log_info, log_info_result, log_error_result, log_warn_result
from _utils import async_load_targets, check_internet_connection, start_monitor, stop_monitor
from domain import find_subdomains


async def scan_ip(ip, nmap_params, output_folder):
    finished_file_name = os.path.join(output_folder, f"nmap.async_finished_{ip}.xml")
    if os.path.exists(finished_file_name):
        log_info_result(
            "nmap.async_nmap", ip, "SKIPPED", f"The '{finished_file_name}' file already exists."
        )
        return

    connection_monitor_id = start_monitor()

    output_file = os.path.join(output_folder, f"nmap.async_{ip}.xml")
    if os.path.exists(output_file):
        log_info(f"The '{output_file}' file already exists. It will be overwritten.")

    log_info_result("nmap.async_nmap", ip, "SCANNING", f"Starts!")

    try:
        process = await asyncio.create_subprocess_exec(
            "nmap", *nmap_params.split(), "-oX", output_file, ip,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        log_info_result("nmap.async_nmap", ip, "FINISHED", f"\n{stdout.decode()}")
        if stderr:
            log_warn_result("nmap.async_nmap", ip, f"Error when scanning:\n{stderr.decode()}")

        log_info(f"File renamed from {output_file} to {finished_file_name}")
        os.rename(output_file, finished_file_name)

    except Exception as e:
        log_error_result("nmap.async_nmap", ip, f"Error when scanning:\n{e}")

    stop_monitor(connection_monitor_id)


async def start_scan(args):
    targets = args.ip_addresses.split(',') if args.ip_addresses else await async_load_targets(args.input_file)
    domains = [t.strip() for t in targets if not t.replace('.', '').isdigit()]
    ip_list = [t.strip() for t in targets if t.replace('.', '').isdigit()]

    resolved_ips = []
    domains = list(set(domains))
    for domain in domains:
        ips = await find_subdomains(domain, args.domain_level, args.brute_force_file)
        resolved_ips.extend(ips)

    all_ips = list(set(ip_list + resolved_ips))
    log_info(f"Starts nmap async scanning to: {', '.join(all_ips)}")
    tasks = [scan_ip(ip, args.nmap_params, args.output_folder) for ip in all_ips]

    # Restriction on parallel processes
    semaphore = asyncio.Semaphore(args.async_processes)
    async def limited_task(task):
        async with semaphore:
            await task

    await asyncio.gather(*(limited_task(task) for task in tasks))


def main(remaining_args):
    parser = argparse.ArgumentParser(description="Asynchronous scanning with Nmap and Subdomain Resolution.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-iF', '--input-file',
                        help="Path to the address file (mandatory if -ips is not used)")
    group.add_argument('-ips', '--ip-addresses',
                        help="List of IP addresses, comma separated (no spaces), to be checked")

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

    # Проверка на обязательные параметры
    if args.input_file is None and args.ip_addresses is None:
        log_error("You must specify either -iF for the address file or -ips for the IP addresses!")
        parser.error("You must specify either -iF for the address file or -ips for the IP addresses!")

    if not check_internet_connection():
        log_error("Unable to execute script, no internet connection!")
        sys.exit(1)

    # Запуск сканирования
    asyncio.run(start_scan(args))
