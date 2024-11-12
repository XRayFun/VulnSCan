from datetime import datetime
import logging

from _conf import LOG_MESSAGE_FORMAT, FILE_LOG_LEVEL, CONSOLE_LOG_LEVEL, LOG_OUTPUT_FOLDER


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

    def _info(self, message):
        self._logger.info(message)

    def _warn(self, message):
        self._logger.warning(message)

    def _error(self, message):
        self._logger.error(message)

    def _debug(self, message):
        self._logger.debug(message)

    logging.getLogger("paramiko").setLevel(logging.WARNING)
