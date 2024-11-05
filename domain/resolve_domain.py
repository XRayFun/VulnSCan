import socket

from _log import log_info_result


module_name = "domain.resolve_domain"


async def resolve_domain(domain):
    try:
        clear_domain = domain.replace('*.','')
        ip = socket.gethostbyname(clear_domain)
        log_info_result(module_name, ip, "RESOLVED", f"From {clear_domain}")
        return ip
    except socket.gaierror:
        return None
