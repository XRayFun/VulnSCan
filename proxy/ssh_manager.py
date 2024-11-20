import random
from typing import List

from _conf import EXTERNAL_SERVERS_FILE
from _log import vsc_log, logger
from _utils import load_external_servers
from proxy.ssh_server import ServerSSH


_module_name = "proxy.manager"


class ManagerSSH:
    """Manage a collection of ServerSSH instances."""

    def __init__(self, servers:List[dict]):
        """
        Initialize the bot-net manager with server configurations.

        :param servers: List of server configurations.
        """
        self.ssh_servers = {
            server["host"]: ServerSSH(
                hostname=server["host"],
                port=server["port"],
                username=server["user"],
                password=server.get("password"),
            )
            for server in servers
        }

    @logger(_module_name)
    def connect_all(self):
        """Establish SSH connections for all servers."""
        for server in self.ssh_servers.values():
            try:
                server.connect()
            except Exception as e:
                vsc_log.error_result(_module_name, f"Failed to connect to {server.hostname}: {e}")

    @logger(_module_name)
    def disconnect_all(self):
        """Close SSH connections for all servers."""
        for server in self.ssh_servers.values():
            server.close()

    @logger(_module_name)
    def get_random_server(self) -> ServerSSH:
        if not self.ssh_servers:
            vsc_log.warn_result(_module_name, "No SSH servers available.")
        return random.choice(list(self.ssh_servers.values()))

    @logger(_module_name)
    def get_all_servers(self) -> List[ServerSSH]:
        return list(self.ssh_servers.values())

    @logger(_module_name)
    def execute_on_random(self, command:str) -> tuple[str, tuple[str, str]] | None:
        """
        Execute a command on a random server.

        :param command: Command to execute.
        :return: Command stdout and stderr by hostname.
        """
        if not self.ssh_servers:
            vsc_log.warn_result(_module_name, "No SSH servers available.")
            return None

        server = random.choice(list(self.ssh_servers.values()))
        try:
            return server.hostname, server.execute_command(command)
        except Exception as e:
            vsc_log.error_result(_module_name, f"Error executing command on {server.hostname}: {e}")

    @logger(_module_name)
    def execute_on_all(self, command:str) -> dict[str, tuple[str, str] | tuple[str, None] | None] :
        """
        Execute a command on all servers.

        :param command: Command to execute.
        :return: Dict of command outputs by hostname.
        """
        results = {}
        for server in self.ssh_servers.values():
            try:
                results.update({server.hostname: server.execute_command(command)})
            except Exception as e:
                results.update({server.hostname: f"Error: {e}"})
        return results

instance_ssh_manager = ManagerSSH(load_external_servers(["ssh"], EXTERNAL_SERVERS_FILE))
try:
    instance_ssh_manager.connect_all()
except Exception as e:
    vsc_log.error_result(_module_name, e)


if __name__ == "__main__":
    try:
        # Execute the command on a random server
        host, output = instance_ssh_manager.execute_on_random("whoami")
        vsc_log.info_ip_result(_module_name, host, f"Output from random server:\n{' '.join(list(filter(None, output)))}")

        # Run the command on all servers
        all_outputs = instance_ssh_manager.execute_on_all("uptime")
        vsc_log.info_result(_module_name, "Outputs from all servers:")
        for host in all_outputs:
            vsc_log.info_ip_result(_module_name, host, f"Output:\n{' '.join(list(filter(None, all_outputs.get(host))))}")

        all_outputs = instance_ssh_manager.execute_on_all("cd /;ls -la")
        vsc_log.info_result(_module_name, "Outputs from all servers:")
        for host in all_outputs:
            vsc_log.info_ip_result(_module_name, host, f"Output:\n{' '.join(list(filter(None, all_outputs.get(host))))}")

    finally:
        # We're disconnecting from all servers
        instance_ssh_manager.disconnect_all()
