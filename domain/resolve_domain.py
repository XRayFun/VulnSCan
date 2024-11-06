import socket

from _log import scan_log


_module_name = "domain.resolve_domain"


async def resolve_domain(domain):
    try:
        clear_domain = domain.replace('*.','')
        ip = socket.gethostbyname(clear_domain)
        scan_log.info_ip_status_result(_module_name, ip, "RESOLVED", f"From {clear_domain}")
        return ip
    except socket.gaierror:
        return None
