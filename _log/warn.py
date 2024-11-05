from .base import *


def log_warn(message):
    logger.warn(message)


def log_warn_result(module, ip, result):
    log_warn(f"{module}\t{ip}:\t{result}")


def log_warn_status_result(module, ip, status, result):
    log_warn(f"{module}\t{ip}\t-\t{status}\t\t{result}")
