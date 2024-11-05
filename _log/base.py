from datetime import datetime
import logging

from _conf import BASE_DIR

file_log = logging.FileHandler(f"{BASE_DIR}/temp/log/scan {datetime.now()}.log", "w")
console_out = logging.StreamHandler()

logging.basicConfig(
    handlers=(file_log, console_out),
    level=logging.INFO,
    format="[%(asctime)s | %(levelname)s] %(message)s"
)

logger = logging.getLogger()
