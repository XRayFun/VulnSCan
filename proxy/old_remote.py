import asyncio
import socks
import socket
import paramiko
import random
import threading
from asyncio import StreamReader, StreamWriter
from paramiko.client import SSHClient

from _conf import SSH_LOCAL_HOST, SSH_LOCAL_PORT, EXTERNAL_SERVERS_FILE, PROXY_LOCAL_HOST, PROXY_LOCAL_PORT
from _log import vsc_log, logger
from _utils import load_external_servers


class ParentServer:
    _module_name = "proxy.ssh"
    """ Connection could not be found. """

    @logger(_module_name)
    def __init__(self, host:str, port:int, config_file:str):
        self._host = host
        self._port = port
        self._external_servers = load_external_servers(["ssh", "http", "https"], config_file)
        self.loop = asyncio.new_event_loop()

    @logger(_module_name)
    def start_background(self):
        """ Starts the server loop in the background. """
        threading.Thread(target=self._run_server_loop, daemon=True).start()
        vsc_log.info_status_result(self._module_name, "START", "SSH Server is starting in the background.")

    @logger(_module_name)
    def _run_server_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start_server())
        self.loop.run_forever()

    @logger(_module_name)
    async def _start_server(self):
        """ Starts the server and handles incoming client requests. """
        try:
            self.server = await asyncio.start_server(self.handle_client, self._host, self._port)
            vsc_log.info_status_result(self._module_name, "SUCCESS", f"SSH Server started on {self._host}:{self._port}")
            async with self.server:
                await self.server.serve_forever()
        except Exception as e:
            vsc_log.error_status_result(self._module_name, "FAILED", f"Failed to start server: {e}")

    @logger(_module_name)
    def stop_server(self):
        """ Stops the server gracefully. """
        if self.server:
            vsc_log.info_status_result(self._module_name, "STOP", f"Stopping SSH Server on {self._host}:{self._port}")
            self.server.close()
            self.loop.stop()
            vsc_log.info_status_result(self._module_name, "SUCCESS", f"SSH Server on {self._host}:{self._port} stopped.")

    async def handle_client(self, client_reader: StreamReader, client_writer: StreamWriter):
        """ Client processing method. Will be overridden in inherited classes. """
        pass


class LocalServer(ParentServer):
    """ Class for local command execution. """
    _module_name = "proxy.local_ssh"

    @logger(_module_name)
    def __init__(self, host:str=SSH_LOCAL_HOST, port:int=SSH_LOCAL_PORT, config_file:str=EXTERNAL_SERVERS_FILE):
        super().__init__(host, port, config_file)
        self._external_servers = load_external_servers(["http", "https"], config_file)

    @logger(_module_name)
    async def handle_client(self, client_reader: StreamReader, client_writer: StreamWriter):
        try:
            data = await client_reader.read(4096)
            command = data.decode().strip()
            if command:
                result = await self._execute_local_command(command)
                response = result or "No output from command execution."
                vsc_log.info_status_result(self._module_name, "RESULT", f"Command feedback:\n{response.encode()}\n")
                client_writer.write(response.encode())
                await client_writer.drain()
                vsc_log.info_status_result(self._module_name, "SEND", "Response sent to client.")
            else:
                client_writer.write("Empty command received.".encode())
                await client_writer.drain()
        except Exception as e:
            vsc_log.error_status_result(self._module_name, "FAILED", f"Client handling error: {e}")
        finally:
            client_writer.close()
            await client_writer.wait_closed()

    @logger(_module_name)
    async def _execute_local_command(self, command: str) -> str | None:
        """ Execute local command while routing internet traffic through a remote server. """
        try:
            # Выбираем случайный сервер из списка внешних серверов для прокси
            remote_server = random.choice(self._external_servers)
            vsc_log.info_status_result(self._module_name, "INFO", f"Routing traffic through {remote_server['host']}:{remote_server['port']}")

            # Устанавливаем SOCKS5 прокси для работы через удалённый сервер
            socks.set_default_proxy(socks.SOCKS5, remote_server['host'], remote_server['port'], True, remote_server['user'], remote_server['password'])
            socket.socket = socks.socksocket
            asyncio.set_event_loop(self.loop)  # Устанавливаем текущий цикл событий для прокси

            # Запуск локальной команды
            result = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()

            if stderr:
                vsc_log.error_status_result(self._module_name, "ERROR", f"Command failed: {stderr.decode()}")
                return stderr.decode()
            return stdout.decode()
        except Exception as e:
            vsc_log.error_status_result(self._module_name, "ERROR", f"Local command execution failed: {e}")
            return None


class RemoteServer(ParentServer):
    """ Class for remote command execution via SSH. """
    _module_name = "proxy.remote_ssh"

    @logger(_module_name)
    def __init__(self, host:str=PROXY_LOCAL_HOST, port:int=PROXY_LOCAL_PORT, config_file:str=EXTERNAL_SERVERS_FILE):
        super().__init__(host, port, config_file)
        self._external_servers = load_external_servers(["ssh"], config_file)

    @logger(_module_name)
    async def handle_client(self, client_reader:StreamReader, client_writer:StreamWriter):
        try:
            data = await client_reader.read(4096)
            command = data.decode().strip()
            if command:
                result = await self._execute_remote_command(command)
                response = result or "No output from command execution."
                client_writer.write(response.encode())
                await client_writer.drain()
                vsc_log.info_status_result(self._module_name, "SEND", "Response sent to client.")
            else:
                client_writer.write("Empty command received.".encode())
                await client_writer.drain()
        except Exception as e:
            vsc_log.error_status_result(self._module_name, "FAILED", f"Client handling error: {e}")
        finally:
            client_writer.close()
            await client_writer.wait_closed()

    @logger(_module_name)
    async def _execute_remote_command(self, command:str) -> str | None:
        """ Executing a command on a remote server via SSH. """
        server_info = random.choice(self._external_servers)
        server_name = f"{server_info['host']}:{server_info['port']}"
        ssh_client = await self._make_ssh_client(server_info)
        if ssh_client:
            try:
                _, stdout, stderr = ssh_client.exec_command(command)
                output, error = stdout.read().decode(), stderr.read().decode()
                ssh_client.close()
                if error:
                    vsc_log.error_ip_status_result(self._module_name, server_name, "FAILED", f"Command feedback:\n{error}")
                else:
                    feedback = f":\n{output}" if output else " is blank."
                    vsc_log.info_ip_status_result(self._module_name, server_name, "RESULT", f"Command feedback{feedback}")
                return output if output else error
            except Exception as e:
                vsc_log.error_ip_status_result(self._module_name, server_name, "ERROR", f"Command execution failed: {e}")
        return None

    async def _make_ssh_client(self, server_info) -> SSHClient | None:
        """ Creating an SSH client for a remote server. """
        server_name = f"{server_info['host']}:{server_info['port']}"
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(
                hostname=server_info['host'], port=server_info['port'],
                username=server_info['user'], password=server_info['password']
            )
            vsc_log.info_ip_status_result(self._module_name, server_name, "SUCCESS", "Connection established.")
            return ssh_client
        except Exception as e:
            vsc_log.error_ip_status_result(self._module_name, server_name, "FAILED", f"Failed to connect: {e}")
            return None


async def main():
    """ Start both servers in parallel. """
    local_server = LocalServer()  # Local command execution server
    remote_server = RemoteServer()  # Remote command execution server

    # Start both servers in parallel
    await asyncio.gather(
        asyncio.to_thread(local_server.start_background),
        asyncio.to_thread(remote_server.start_background)
    )

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        local_server.stop_server()
        remote_server.stop_server()
        vsc_log.error_status_result("proxy.ssh", "STOP", "SSH серверы были остановлены.")


if __name__ == "__main__":
    asyncio.run(main())
