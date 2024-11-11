import inspect
from functools import wraps
from logging import Logger

from _log.base import BaseLogger
from _conf import MODULE_WIDTH, IP_WIDTH, STATUS_WIDTH


class Logger(BaseLogger):
    """
    Logger class for structured logging of informational, warning, and error messages with specific formatting.

    Each method in this class logs messages with customizable column widths based on configuration values
    (MODULE_WIDTH, IP_WIDTH, and STATUS_WIDTH). This class enables structured and clear log entries for different
    levels of logging (info, warning, error), with methods designed to log results associated with a module,
    an IP address, or a status.

    Methods:
        - info_result(module, result): Logs an informational message for a general result.
        - info_ip_result(module, ip, result): Logs an informational message for a result tied to a specific IP.
        - info_status_result(module, status, result): Logs an informational message for a status.
        - info_ip_status_result(module, ip, status, result): Logs an informational message for a result with both IP and status.

        - warn_result(module, result): Logs a warning for a general result.
        - warn_ip_result(module, ip, result): Logs a warning for a result tied to a specific IP.
        - warn_status_result(module, status, result): Logs a warning for a status.
        - warn_ip_status_result(module, ip, status, result): Logs a warning for a result with both IP and status.

        - error_result(module, result): Logs an error for a general result.
        - error_ip_result(module, ip, result): Logs an error for a result tied to a specific IP.
        - error_status_result(module, status, result): Logs an error for a status.
        - error_ip_status_result(module, ip, status, result): Logs an error for a result with both IP and status.

        - debug_result(module, result): Logs a debug for a general result.
        - debug_ip_result(module, ip, result): Logs a debug for a result tied to a specific IP.
        - debug_status_result(module, status, result): Logs a debug for a status.
        - debug_ip_status_result(module, ip, status, result): Logs a debug for a result with both IP and status.

    Attributes:
        MODULE_WIDTH (int): Width for the module name in log output.
        IP_WIDTH (int): Width for the IP address in log output.
        STATUS_WIDTH (int): Width for the status field in log output.
    """

    def info_result(self, module, result):
        self._info(f"{module:<{MODULE_WIDTH+IP_WIDTH+STATUS_WIDTH}}{result}")

    def info_ip_result(self, module, ip, result):
        self._info(f"{module:<{MODULE_WIDTH}}{ip:<{IP_WIDTH+STATUS_WIDTH}}{result}")

    def info_status_result(self, module, status, result):
        self._info(f"{module:<{MODULE_WIDTH+IP_WIDTH}}{status:<{STATUS_WIDTH}}{result}")

    def info_ip_status_result(self, module, ip, status, result):
        self._info(f"{module:<{MODULE_WIDTH}}{ip:<{IP_WIDTH}}{status:<{STATUS_WIDTH}}{result}")


    def warn_result(self, module, result):
        self._warn(f"{module:<{MODULE_WIDTH+IP_WIDTH+STATUS_WIDTH}}{result}")

    def warn_ip_result(self, module, ip, result):
        self._warn(f"{module:<{MODULE_WIDTH}}{ip:<{IP_WIDTH+STATUS_WIDTH}}{result}")

    def warn_status_result(self, module, status, result):
        self._warn(f"{module:<{MODULE_WIDTH+IP_WIDTH}}{status:<{STATUS_WIDTH}}{result}")

    def warn_ip_status_result(self, module, ip, status, result):
        self._warn(f"{module:<{MODULE_WIDTH}}\t{ip:<{IP_WIDTH}}\t\t{status:<{STATUS_WIDTH}}\t\t{result}")


    def error_result(self, module, result):
        self._error(f"{module:<{MODULE_WIDTH+IP_WIDTH+STATUS_WIDTH}}\n\t{result}")

    def error_ip_result(self, module, ip, result):
        self._error(f"{module:<{MODULE_WIDTH}}{ip:<{IP_WIDTH+STATUS_WIDTH}}\n\t{result}")

    def error_status_result(self, module, status, result):
        self._error(f"{module:<{MODULE_WIDTH+IP_WIDTH}}{status:<{STATUS_WIDTH}}\n\t{result}")

    def error_ip_status_result(self, module, ip, status, result):
        self._error(f"{module:<{MODULE_WIDTH}}{ip:<{IP_WIDTH}}{status:<{STATUS_WIDTH}}\n\t{result}")


    def debug_result(self, module, result):
        self._debug(f"{module:<{MODULE_WIDTH+IP_WIDTH+STATUS_WIDTH}}\t{result}")

    def debug_ip_result(self, module, ip, result):
        self._debug(f"{module:<{MODULE_WIDTH}}{ip:<{IP_WIDTH+STATUS_WIDTH}}{result}")

    def debug_status_result(self, module, status, result):
        self._debug(f"{module:<{MODULE_WIDTH+IP_WIDTH}}{status:<{STATUS_WIDTH}}{result}")

    def debug_ip_status_result(self, module, ip, status, result):
        self._debug(f"{module:<{MODULE_WIDTH}}\t{ip:<{IP_WIDTH}}\t\t{status:<{STATUS_WIDTH}}\t\t{result}")


scan_log = Logger()
