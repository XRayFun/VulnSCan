from .base import *


def log_info(message):
    logger.info(message)


def log_info_result(module, ip, status, result):
    log_info(f"{module}\t{ip}\t-\t{status}\t\t{result}")
