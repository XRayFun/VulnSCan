from _conf.base import BASE_DIR


NMAP_OUTPUT_FOLDER = f"{BASE_DIR}/temp/scan/"
NMAP_PARAMS = "-sVC -p- -Pn -script=vuln"
NMAP_ASYNC_PROCESSES = 3
