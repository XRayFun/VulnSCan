from .base import *


def log_error(message):
    logger.error(message)


def log_error_result(module, ip, result):
    log_error(f"{module}\t{ip}:\n\t{result}")
