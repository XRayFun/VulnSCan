import argparse
import importlib
import sys

from _conf import BANNER, LOG_LEVEL, LOG_FORMAT, LOG_OUTPUT_FOLDER
from _log import scan_log


def vuln_scan():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Vulnerability Scanner with multiple scan modes.")
    parser.add_argument('module', help="Module to execute, e.g., 'nmap', 'domain'")
    parser.add_argument('command', help="Command to execute within the module, e.g., 'async_nmap', 'subdomain")
    known_args, remaining_args = parser.parse_known_args()

    # Dynamically load the selected module of the command
    try:
        command_module = importlib.import_module(f"{known_args.module}.{known_args.command}")
    except ModuleNotFoundError:
        scan_log._error(f"The command '{known_args.module}.{known_args.command}' is not recognized.")
        sys.exit(1)

    scan_log._info(f"Logger setup with:"
                   f"\n\t- Log level:  {LOG_LEVEL}"
                   f"\n\t- Log format: {LOG_FORMAT}"
                   f"\n\t- Log folder: {LOG_OUTPUT_FOLDER}")

    # Pass the remaining arguments to the command module
    scan_log._info(f"Starting scan with {known_args.module}.{known_args.command} module.")
    command_module.main(remaining_args)


if __name__ == '__main__':
    vuln_scan()
