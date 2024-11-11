import argparse
import importlib
import logging

from _conf import BANNER, FILE_LOG_LEVEL, CONSOLE_LOG_LEVEL, LOG_MESSAGE_FORMAT, LOG_OUTPUT_FOLDER
from _log import scan_log


def vuln_scan():
    scan_log._info(f"{BANNER}")
    parser = argparse.ArgumentParser(description="Vulnerability Scanner with multiple scan modes.")
    parser.add_argument('module', help="Module to execute, e.g., 'help', 'nmap', 'domain'")
    parser.add_argument('command', help="Command to execute within the module, e.g., 'async_nmap', 'subdomain")
    known_args, remaining_args = parser.parse_known_args()

    # Dynamically load the selected module of the command
    try:
        if known_args.module != "help":
            command_module = importlib.import_module(f"{known_args.module}.{known_args.command}")
        else:
            command_module = importlib.import_module(f"{known_args.module}")
    except ModuleNotFoundError:
        scan_log._error(f"The command '{known_args.module}.{known_args.command}' is not recognized.")
        return 1

    scan_log._info(f"Logger setup with:"
                   f"\n\t- Log level (console):  {logging.getLevelName(CONSOLE_LOG_LEVEL)}"
                   f"\n\t- Log level (file):  {logging.getLevelName(FILE_LOG_LEVEL)}"
                   f"\n\t- Log format: {LOG_MESSAGE_FORMAT}"
                   f"\n\t- Log folder: {LOG_OUTPUT_FOLDER}\n")

    # Pass the remaining arguments to the command module
    scan_log._info(f"Starting scan with {known_args.module}.{known_args.command} module.")
    command_module.main(remaining_args)
    return 0


if __name__ == '__main__':
    vuln_scan()
