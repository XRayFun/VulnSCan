import os

from _conf.base import SCAN_DIR


NMAP_OUTPUT_FOLDER = f"{SCAN_DIR}nmap/"
if not os.path.exists(NMAP_OUTPUT_FOLDER):
    os.mkdir(NMAP_OUTPUT_FOLDER)

NMAP_PARAMS = "-sVC -p- -Pn -script=vuln"

NMAP_ASYNC_PROCESSES = 3
