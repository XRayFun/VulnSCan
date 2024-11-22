import select
import socket
import threading
import paramiko
from typing import Optional

from _conf import PROXY_HOST, TEMP_DIR
from _log import logger, vsc_log
from _utils import get_random_port_from_json
from __temp__.proxy_test_auth_data import PROXY_TEST_host, PROXY_TEST_port, PROXY_TEST_user, PROXY_TEST_password


_module_name = "proxy.server"


class ServerSSH:
    def __init__(self, hostname:str, port:int, username:str, password:Optional[str] = None, pkey:Optional[str] = None, local_host: str = PROXY_HOST, local_port: int = get_random_port_from_json()):
        """
        Initialize SSH Server.
        :param hostname: SSH server address
        :param port: SSH server port
        :param username: SSH username
        :param password: SSH password (if any)
        :param pkey: Path to private key (if any)
        :param local_host: Local proxy address
        :param local_port: Local proxy port
        """
        self.remote_host = hostname
        self.remote_port = port
        self.local_host = local_host
        self.local_port = local_port
        self._username = username
        self._password = password
        self._pkey = pkey

        self._client = None
        self._channel = None
        self._tunnel_thread = None

        self.str_remote = f"{self.remote_host}:{self.remote_port}"
        self.str_local = f"{self.local_host}:{self.local_port}"

        vsc_log.info_ip_status_result(
            _module_name,
            self.str_local,
            "INIT",
            f"Remote server data: {f'*****@' if self._username else ''}{self.str_remote}"
            f"{' with password: *****' if self._password else ''}{' with pkey: *****' if self._pkey else ''}"
        )

    @logger(_module_name)
    def connect(self):
        """Establish an SSH connection."""
        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self._pkey:
                private_key = paramiko.RSAKey.from_private_key_file(self._pkey)
                self._client.connect(self.remote_host, port=self.remote_port, username=self._username, pkey=private_key)
            else:
                self._client.connect(self.remote_host, port=self.remote_port, username=self._username, password=self._password)
            vsc_log.info_ip_result(_module_name, self.local_port, "Connection successful!")
        except Exception as e:
            vsc_log.error_result(_module_name, f"Failed to connect to {self.remote_host}:{self.remote_port}: {e}")

    @logger(_module_name)
    def execute_command(self, command:str) -> tuple[str, str] | tuple[None, None]:
        """
        Execute a command on the remote server.
        :param command: Command to execute
        :return: Command output
        """
        if not self._client:
            vsc_log.warn_result(_module_name, "SSH connection is not established.")
        else:
            stdin, stdout, stderr = self._client.exec_command(command)
            return stdout.read().decode(), stderr.read().decode()
        return None, None

    @logger(_module_name)
    def sftp_upload(self, local_path:str, remote_path:str):
        """
        Upload a file via SFTP.
        :param local_path: Path to local file
        :param remote_path: Path on remote server
        """
        if not self._client:
            vsc_log.warn_ip_result(_module_name, self.str_local, "SSH connection is not established.")
        else:
            sftp = self._client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()

    @logger(_module_name)
    def sftp_download(self, remote_path:str, local_path:str):
        """
        Download a file via SFTP.
        :param remote_path: Path on remote server
        :param local_path: Path to local file
        """
        if not self._client:
            vsc_log.warn_ip_result(_module_name, self.str_local, "SSH connection is not established.")
        else:
            sftp = self._client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()

    @logger(_module_name)
    def start_proxy(self):
        """Setup a local SOCKS5 tunnel through the given SSH server."""
        try:
            vsc_log.info_ip_result(_module_name, self.str_local, f"Attempting to establish a tunnel.")
            transport = self._client.get_transport()
            transport.set_keepalive(180)
            # Setup dynamic forwarding (SOCKS5 Proxy)
            threading.Thread(target=self._start_socks5_server).start()

        except Exception as e:
            vsc_log.warn_ip_result(
                _module_name, self.str_local,
                f"Unable to establish a tunnel. Exception:\n{e}"
            )

    @logger(_module_name)
    def _start_socks5_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.local_host, self.local_port))
        server_sock.listen(5)

        vsc_log.info_ip_result(_module_name, self.str_local, "SOCKS5 proxy starts")

        while True:
            client_sock, client_addr = server_sock.accept()
            threading.Thread(target=self._handle_client, args=(client_sock,)).start()

    @logger(_module_name)
    def _handle_client(self, client_sock):
        """Handling client connection and proxying through SSH tunnel."""
        vsc_log.info_ip_result(_module_name, self.str_local, "New request received")
        try:
            # Acceptance of SOCKS5 handshake
            client_request = client_sock.recv(262)
            if client_request[0] != 0x05:  # Check SOCKS5 version
                client_sock.close()
                return

            # Send SOCKS5 support confirmation without authentication
            client_sock.sendall(b"\x05\x00")

            # Receiving a connection request
            client_request = client_sock.recv(4)
            if client_request[1] != 0x01:  # Only CONNECT is supported
                client_sock.close()
                return

            # Parse address and port of destination
            addr_type = client_request[3]
            if addr_type == 0x01:  # IPv4
                dest_addr = socket.inet_ntoa(client_sock.recv(4))
            elif addr_type == 0x03:  # Domain name
                domain_length = client_sock.recv(1)[0]
                dest_addr = client_sock.recv(domain_length).decode()
            else:
                client_sock.close()
                return

            dest_port = int.from_bytes(client_sock.recv(2), "big")

            # Set the SSH channel for direct connection
            transport = self._client.get_transport()
            self._channel = transport.open_channel(
                kind="direct-tcpip",
                dest_addr=(dest_addr, dest_port),
                src_addr=(self.local_host, self.local_port),
            )

            # Send confirmation to the client
            client_sock.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")

            # Redirecting data
            while True:
                read_sockets, _, _ = select.select([client_sock, self._channel], [], [])
                for sock in read_sockets:
                    data = sock.recv(1024)
                    if not data:
                        return
                    if sock is client_sock:
                        self._channel.send(data)
                    else:
                        client_sock.send(data)
        except Exception as e:
            vsc_log.warn_ip_result(_module_name, self.str_local, f"Error in SOCKS5 proxy handler:\n{e}")
        finally:
            client_sock.close()
            if self._channel:
                self._channel.close()

    @logger(_module_name)
    def stop_proxy(self):
        if self._tunnel_thread:
            self._tunnel_thread.join()
            vsc_log.log_ip_result(_module_name, self.str_local, f"SOCKS5 proxy stopped.")

    @logger(_module_name)
    def port_forward(self):
        """Set up local port forwarding."""
        if not self._client:
            vsc_log.warn_ip_result(_module_name, self.str_local, "SSH connection is not established.")

        transport = self._client.get_transport()
        transport.request_port_forward("", self.local_port, self.remote_host, self.remote_port)

    @logger(_module_name)
    def close(self):
        """Close the SSH connection."""
        if self._client:
            self._client.close()
        self.stop_proxy()


# Пример использования
if __name__ == "__main__":
    server = ServerSSH(
        hostname=PROXY_TEST_host,
        port=PROXY_TEST_port,
        username=PROXY_TEST_user,
        password=PROXY_TEST_password,
        local_port=11111
    )
    try:
        server.connect()

        output = server.execute_command("uptime")
        vsc_log.info_ip_result(_module_name, f"{server.str_local}", f"Output (from {server.str_remote}):\n{' '.join(list(filter(None, output)))}")

        try:
            server.start_proxy()
        except KeyboardInterrupt:
            server.stop_proxy()

        server.sftp_upload(f"{TEMP_DIR}test.txt", "/tmp/file.txt")
        server.sftp_download("/tmp/file.txt", f"{TEMP_DIR}downloaded/downloaded_file.txt")
        # ssh_manager.port_forward()
    finally:
        input()
        server.close()
