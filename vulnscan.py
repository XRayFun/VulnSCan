import argparse
import importlib
import sys

from _conf import BANNER
from _log import log_info, log_error


def vuln_scan():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Vulnerability Scanner with multiple scan modes.")
    parser.add_argument('module', help="Module to execute, e.g., 'nmap'")
    parser.add_argument('command', help="Command to execute within the module, e.g., 'async_nmap'")
    known_args, remaining_args = parser.parse_known_args()

    # Динамически загружаем выбранный модуль команды
    try:
        command_module = importlib.import_module(f"{known_args.module}.{known_args.command}")
    except ModuleNotFoundError:
        log_error(f"The command '{known_args.module}.{known_args.command}' is not recognized.")
        sys.exit(1)

    # Передаем оставшиеся аргументы в командный модуль
    log_info(f"Starting scan with {known_args.module}.{known_args.command}.")
    command_module.main(remaining_args)


if __name__ == '__main__':
    vuln_scan()
