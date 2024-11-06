from datetime import datetime
import logging

from _conf import LOG_FORMAT, LOG_LEVEL, LOG_OUTPUT_FOLDER


class BaseLogger:
    _file_log = logging.FileHandler(f"{LOG_OUTPUT_FOLDER}{datetime.now()}.log", "w")
    _console_out = logging.StreamHandler()

    logging.basicConfig(
        handlers=(_file_log, _console_out),
        level=LOG_LEVEL,
        format=LOG_FORMAT
    )

    _logger = logging.getLogger()

    def _info(self, message):
        self._logger.info(message)

    def _warn(self, message):
        self._logger.warning(message)

    def _error(self, message):
        self._logger.error(message)
