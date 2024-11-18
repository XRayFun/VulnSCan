import http.server
import json
import random
import threading
import socketserver

import asyncio
from paramiko.client import SSHClient, AutoAddPolicy

from _conf import EXTERNAL_SERVERS_FILE, PROXY_LOCAL_HOST, PROXY_LOCAL_PORT
from _log import vsc_log


# Загрузка конфигурации серверов
with open(EXTERNAL_SERVERS_FILE, "r") as f:
    config = json.load(f)

# Распределение серверов по протоколам
protocol_map = {}
for server in config["servers"]:
    for protocol in server["protocol"]:
        protocol_map.setdefault(protocol, []).append(server)


async def execute_remote_command_via_proxy(command, url=f"http://{PROXY_LOCAL_HOST}:{PROXY_LOCAL_PORT}/ssh"):
    """
    Executes a remote command via the proxy SSH service.

    Args:
        command (str): The command to execute on the remote server.
        url (str): The URL of the proxy SSH service.

    Returns:
        stdout, stderr: The output of the command execution.
    """
    process = await asyncio.create_subprocess_exec(
        "curl", "-X", "POST", "-d", json.dumps({"command": command}), url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"Error executing remote command: {stderr.decode().strip()}")

    return stdout, stderr


# Класс обработчика HTTP-запросов
class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/http"):
            self.handle_protocol("http")
        elif self.path.startswith("/https"):
            self.handle_protocol("https")
        elif self.path == "/status":
            self.handle_status()
        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        if self.path == "/ssh":
            self.handle_ssh()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_protocol(self, protocol):
        if protocol not in protocol_map or not protocol_map[protocol]:
            self.send_error(500, f"No servers available for protocol {protocol}")
            return

        server = random.choice(protocol_map[protocol])
        response = {
            "host": server["host"],
            "port": server["port"],
            "user": server.get("user"),  # Передаем логин, если он есть
            "password": server.get("password")  # Передаем пароль, если он есть
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_status(self):
        response = {protocol: len(servers) for protocol, servers in protocol_map.items()}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_ssh(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            command = data.get("command")
            if not command:
                self.send_error(400, "Missing 'command' in request")
                return

            if not protocol_map["ssh"]:
                self.send_error(500, "No SSH servers available")
                return

            server = random.choice(protocol_map["ssh"])
            result = self.execute_ssh_command(server, command)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(result.encode())
        except Exception as e:
            self.send_error(500, str(e))

    def execute_ssh_command(self, server, command):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(
            server["host"],
            port=server["port"],
            username=server.get("user"),
            password=server.get("password"),
        )
        stdin, stdout, stderr = client.exec_command(command)
        result = stdout.read().decode() + stderr.read().decode()
        client.close()
        return result


# Класс сервера
class ProtocolServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    def __init__(self, server_address, handler_class, protocol_map):
        self.protocol_map = protocol_map
        super().__init__(server_address, handler_class)


# Запуск сервера
def run_server():
    server = ProtocolServer((PROXY_LOCAL_HOST, PROXY_LOCAL_PORT), ProxyHTTPRequestHandler, protocol_map)
    vsc_log.info_result("proxy.remote", f"Server is running on http://{PROXY_LOCAL_HOST}:{PROXY_LOCAL_PORT}")
    server.serve_forever()


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    input("Press any key to stop the server...\n")
