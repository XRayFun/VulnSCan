from datetime import datetime
import logging
from enum import Enum

from _conf import LOG_MESSAGE_FORMAT, FILE_LOG_LEVEL, CONSOLE_LOG_LEVEL, LOG_OUTPUT_FOLDER, MODULE_WIDTH, IP_WIDTH, STATUS_WIDTH, DEFAULT_AUTOLOG_LEVEL


class LogLevel(Enum):
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    DEFAULT_AUTOLOG_LEVEL = DEFAULT_AUTOLOG_LEVEL


def _format_message(module, result, ip=None, status=None):
    """
    Formats the log message based on provided data.
    """
    if ip and status:
        return f"{module:<{MODULE_WIDTH}}{ip:<{IP_WIDTH}}{status:<{STATUS_WIDTH}}{result}"
    elif ip:
        return f"{module:<{MODULE_WIDTH}}{ip:<{IP_WIDTH + STATUS_WIDTH}}{result}"
    elif status:
        return f"{module:<{MODULE_WIDTH + IP_WIDTH}}{status:<{STATUS_WIDTH}}{result}"
    else:
        return f"{module:<{MODULE_WIDTH + IP_WIDTH + STATUS_WIDTH}}{result}"


class BaseLogger:
    # File handler for debug-level logging
    _file_log = logging.FileHandler(f"{LOG_OUTPUT_FOLDER}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.log", "w")
    _file_log.setLevel(FILE_LOG_LEVEL)

    # Console handler for info-level logging
    _console_out = logging.StreamHandler()
    _console_out.setLevel(CONSOLE_LOG_LEVEL)

    # Setting up the formatter for both handlers
    formatter = logging.Formatter(LOG_MESSAGE_FORMAT)
    _file_log.setFormatter(formatter)
    _console_out.setFormatter(formatter)

    # Creating and configuring the logger
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(_file_log)
    _logger.addHandler(_console_out)

    # Additional loggers
    logging.getLogger("paramiko").setLevel(logging.WARNING)


    def log_result(self, level:LogLevel, module:str, result:str, ip=None, status=None):
        """
        Logs a message at the specified log level with a structured format.
        """
        log_message = _format_message(module, result, ip, status)
        self._logger.log(level.value if level else LogLevel.NOTSET, log_message)

    def log(self, level:LogLevel, message):
        self._logger.log(level.value if level else LogLevel.NOTSET, message)


    def _debug(self, message):
        self._logger.debug(message)

    def _info(self, message):
        self._logger.info(message)

    def _warn(self, message):
        self._logger.warning(message)

    def _error(self, message):
        self._logger.error(message)


    def log_settings(self):
        self.log(LogLevel.DEBUG, "Logger setup with:"
                                 f"\n\t- Log level (console):  {logging.getLevelName(CONSOLE_LOG_LEVEL)}"
                                 f"\n\t- Log level (file):  {logging.getLevelName(FILE_LOG_LEVEL)}"
                                 f"\n\t- Log format: {LOG_MESSAGE_FORMAT}"
                                 f"\n\t- Log folder: {LOG_OUTPUT_FOLDER}\n")
