from _log.base import BaseLogger
from _conf import MODULE_WIDTH, IP_WIDTH, STATUS_WIDTH


class Logger(BaseLogger):
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
