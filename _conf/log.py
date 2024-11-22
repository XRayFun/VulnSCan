import logging
import os

from _conf.base import TEMP_DIR


LOG_OUTPUT_FOLDER = f"{TEMP_DIR}log/"
if not os.path.exists(LOG_OUTPUT_FOLDER):
    os.mkdir(LOG_OUTPUT_FOLDER)

LOG_MESSAGE_FORMAT = "[%(asctime)-15s | %(levelname)-8s] %(message)s"

FILE_LOG_LEVEL = logging.DEBUG

CONSOLE_LOG_LEVEL = logging.INFO

DEFAULT_AUTOLOG_LEVEL = logging.DEBUG

MODULE_WIDTH = 26

IP_WIDTH = 22

STATUS_WIDTH = 18

SENSITIVE_KEYS = ['user', 'username', 'password', 'pkey']
