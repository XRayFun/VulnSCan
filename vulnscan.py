import argparse
import importlib

from _conf import BANNER
from _log import vsc_log, LogLevel, logger


@logger("main")
def vuln_scan():
    vsc_log.log(LogLevel.INFO, f"{BANNER}")
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
    except ModuleNotFoundError as e:
        vsc_log.log(LogLevel.ERROR, f"Module '{known_args.module}.{known_args.command}' not found: {e}")
        return 1
    except Exception as e:
        vsc_log.log(LogLevel.ERROR, f"Unexpected error during import: {e}")
        return 1

    vsc_log.log_settings()

    # Pass the remaining arguments to the command module
    vsc_log.log(LogLevel.INFO, f"Starting scan with {known_args.module}.{known_args.command} module.")
    command_module.main(remaining_args)
    return 0


if __name__ == '__main__':
    vuln_scan()
