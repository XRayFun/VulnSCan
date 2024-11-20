from _log.base import BaseLogger, LogLevel


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
    """

    def debug_result(self, module, result):
        self.log_result(LogLevel.DEBUG, module, result)

    def debug_ip_result(self, module, ip, result):
        self.log_result(LogLevel.DEBUG, module, result, ip)

    def debug_status_result(self, module, status, result):
        self.log_result(LogLevel.DEBUG, module, result, status=status)

    def debug_ip_status_result(self, module, ip, status, result):
        self.log_result(LogLevel.DEBUG, module, result, ip, status)


    def info_result(self, module, result):
        self.log_result(LogLevel.INFO, module, result)

    def info_ip_result(self, module, ip, result):
        self.log_result(LogLevel.INFO, module, result, ip)

    def info_status_result(self, module, status, result):
        self.log_result(LogLevel.INFO, module, result, status=status)

    def info_ip_status_result(self, module, ip, status, result):
        self.log_result(LogLevel.INFO, module, result, ip, status)


    def warn_result(self, module, result):
        self.log_result(LogLevel.WARN, module, result)

    def warn_ip_result(self, module, ip, result):
        self.log_result(LogLevel.WARN, module, result, ip)

    def warn_status_result(self, module, status, result):
        self.log_result(LogLevel.WARN, module, result, status=status)

    def warn_ip_status_result(self, module, ip, status, result):
        self.log_result(LogLevel.WARN, module, result, ip, status)


    def error_result(self, module, result):
        self.log_result(LogLevel.ERROR, module, result)

    def error_ip_result(self, module, ip, result):
        self.log_result(LogLevel.ERROR, module, result, ip)

    def error_status_result(self, module, status, result):
        self.log_result(LogLevel.ERROR, module, result, status=status)

    def error_ip_status_result(self, module, ip, status, result):
        self.log_result(LogLevel.ERROR, module, result, ip, status)


vsc_log = Logger()
