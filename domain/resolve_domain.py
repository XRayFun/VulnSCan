import socket

from _log import vsc_log, logger

_module_name = "domain.resolve_domain"


@logger(_module_name)
async def resolve_domain(domain:str):
    clear_domain = domain.replace('*.','').replace(' ','')
    try:
        ip = socket.gethostbyname(clear_domain)
        vsc_log.info_ip_status_result(_module_name, ip, "RESOLVED", f"From {clear_domain}")
        return ip
    except socket.gaierror as e:
        vsc_log.debug_status_result(_module_name, "GAIERROR", f"Unable to resolve domain '{clear_domain}' due to address-related error: {e}")
        return None
    except socket.herror as e:
        vsc_log.debug_status_result(_module_name, "HERROR", f"Unable to resolve domain '{clear_domain}' due to host-related error: {e}")
        return None
    except ValueError as e:
        vsc_log.debug_status_result(_module_name, "VALUEERROR", f"Invalid domain format '{domain}': {e}")
        return None
    except Exception as e:
        vsc_log.warn_status_result(_module_name, "ERROR", f"Unexpected error occurred while resolving domain '{domain}': {e}")
        return None
