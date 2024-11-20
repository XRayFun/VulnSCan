import socket
import socks
import paramiko
from typing import Optional

from _conf import PROXY_HOST, PROXY_PORT
from _log import logger, vsc_log


_module_name = "proxy.server"


class ServerSSH:
    def __init__(self, hostname:str, port:int, username:str, password:Optional[str] = None, pkey:Optional[str] = None):
        """
        Initialize SSH Manager.

        :param hostname: SSH server address
        :param port: SSH server port
        :param username: SSH username
        :param password: SSH password (if any)
        :param pkey: Path to private key (if any)
        """
        self.hostname = hostname
        self.port = port
        self._username = username
        self._password = password
        self._pkey = pkey
        self.client = None

    @logger(_module_name)
    def connect(self):
        """Establish an SSH connection."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self._pkey:
                private_key = paramiko.RSAKey.from_private_key_file(self._pkey)
                self.client.connect(self.hostname, port=self.port, username=self._username, pkey=private_key)
            else:
                self.client.connect(self.hostname, port=self.port, username=self._username, password=self._password)
        except Exception as e:
            vsc_log.error_result(_module_name, f"Failed to connect to {self.hostname}:{self.port}: {e}")

    @logger(_module_name)
    def execute_command(self, command:str) -> tuple[str, str]:
        """
        Execute a command on the remote server.

        :param command: Command to execute
        :return: Command output
        """
        if not self.client:
            vsc_log.warn_result(_module_name, "SSH connection is not established.")

        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()

    @logger(_module_name)
    def sftp_upload(self, local_path:str, remote_path:str):
        """
        Upload a file via SFTP.

        :param local_path: Path to local file
        :param remote_path: Path on remote server
        """
        if not self.client:
            raise ConnectionError("SSH connection is not established.")

        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    @logger(_module_name)
    def sftp_download(self, remote_path:str, local_path:str):
        """
        Download a file via SFTP.

        :param remote_path: Path on remote server
        :param local_path: Path to local file
        """
        if not self.client:
            raise ConnectionError("SSH connection is not established.")

        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

    @logger(_module_name)
    def setup_local_tunnel(self, local_host:str = PROXY_HOST, local_port:int = PROXY_PORT):
        """
        Setup a local SOCKS5 tunnel through the given SSH manager.

        :param server: ServerSSH to use for the tunnel.
        :param local_host: Local host for SOCKS5 proxy.
        :param local_port: Local port for SOCKS5 proxy.
        """
        transport = self.client.get_transport()
        transport.set_keepalive(120)  # Keep tunnel alive
        channel = transport.open_channel("direct-tcpip", (local_host, local_port), ("", 0))
        proxy = socks.socksocket()
        proxy.set_proxy(socks.SOCKS5, local_host, local_port)
        socket.socket = proxy

    @logger(_module_name)
    def port_forward(self, local_port:int, remote_port:int, remote_host:str):
        """
        Set up local port forwarding.

        :param local_port: Local port to forward
        :param remote_port: Remote port to forward
        :param remote_host: Remote host for forwarding
        """
        if not self.client:
            raise ConnectionError("SSH connection is not established.")

        transport = self.client.get_transport()
        transport.request_port_forward("", local_port, remote_host, remote_port)

    @logger(_module_name)
    def close(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()


# Пример использования
if __name__ == "__main__":
    server = ServerSSH(
        hostname="...",
        port=0,
        username="...",
        password="..."
    )
    try:
        server.connect()
        print(server.execute_command("uptime"))
        server.sftp_upload("/Users/xrayfun/PycharmProjects/VulnSCan/__temp__/test.txt", "/tmp/file.txt")
        server.sftp_download("/tmp/file.txt", "/Users/xrayfun/PycharmProjects/VulnSCan/__temp__/downloaded/downloaded_file.txt")
        # ssh_manager.port_forward(local_port=8080, remote_port=80, remote_host="127.0.0.1")
    finally:
        server.close()
