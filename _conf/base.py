import os


BANNER = """

██╗  ██╗██████╗  █████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗    
╚██╗██╔╝██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║    
 ╚███╔╝ ██████╔╝███████║ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║    
 ██╔██╗ ██╔══██╗██╔══██║  ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║    
██╔╝ ██╗██║  ██║██║  ██║   ██║   ██║     ╚██████╔╝██║ ╚████║    
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝

Vulnerability scanner for web servers and applications.
Authored by XRayFun - 2024

"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMP_DIR = f"{BASE_DIR}/temp/"
if not os.path.exists(TEMP_DIR):
    os.mkdir(TEMP_DIR)

SCAN_DIR = f"{TEMP_DIR}scan/"
if not os.path.exists(SCAN_DIR):
    os.mkdir(SCAN_DIR)
