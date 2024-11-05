import re
import aiofiles

from _log import log_info, log_error


async def async_load_targets(input_file):
    ips = []
    async with aiofiles.open(input_file, mode='r') as f:
        contents = await f.read()
        contents = contents.replace(" ", "").replace("\n", "").replace("\r", "")
        ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', contents)
    if ips:
        log_info(f"Loaded IPs from '{input_file}': {', '.join(ips)}")
    else:
        log_error(f"File not found: '{input_file}'")
    return ips


def load_targets(input_file):
    ips = []
    # Открываем файл асинхронно
    with open(input_file, 'r') as file:
        for line in file:
            # Ищем IP-адрес в строке
            match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
            if match:
                ips.append(match.group(0))
    if ips:
        log_info(f"Loaded IPs from '{input_file}': {', '.join(ips)}")
    else:
        log_error(f"IPs not found in '{input_file}' file!")

    return ips