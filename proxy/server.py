import asyncio
import threading
import time
from asyncio import StreamReader, StreamWriter

import paramiko
import random
import json
import os

from _conf import PROXY_LOCAL_HOST, PROXY_LOCAL_PORT, PROXY_EXTERNAL_SERVERS_FILE
from _log import logger, scan_log, LogLevel

_module_name = "proxy.server"
_executor_name = "proxy.executor"


class ProxyServer:
    @logger(_module_name)
    def __init__(self, host:str=PROXY_LOCAL_HOST, port:int=PROXY_LOCAL_PORT, config_file:str=PROXY_EXTERNAL_SERVERS_FILE):
        """
        Initializes the SOCKS5 proxy server.
        :param host: The host where the proxy server will listen for incoming connections.
        :param port: The port for the proxy server to listen on.
        :param config_file: Path to the JSON configuration file that contains external server information.
        """
        self._host = host
        self._port = port
        self._external_servers = self._load_external_servers(config_file)
        self.loop = asyncio.new_event_loop()  # Create a new event loop
        self.server = None
        self.server_task = None
        self.server_thread = None  # Thread for running the server

    @logger(_module_name)
    def start_background(self):
        """
        Starts the server in a background thread.
        """
        # Create and start a new thread to run the server
        self.server_thread = threading.Thread(target=self._run_server_loop)
        self.server_thread.start()
        scan_log.info_status_result(_module_name, "RUN", "SOCKS5 Proxy Server is starting in the background.")

    @logger(_module_name)
    def _run_server_loop(self):
        """
        Runs the server event loop in a new thread.
        """
        asyncio.set_event_loop(self.loop)  # Set the event loop for this thread
        self.server_task = self.loop.create_task(self._start_server())
        self.loop.run_forever()  # Start the event loop

    @logger(_module_name)
    async def _start_server(self):
        """
        Starts the proxy server asynchronously.
        """
        self.server = await asyncio.start_server(self._handle_client, self._host, self._port)
        scan_log.info_status_result(_module_name, "SUCCESS", f"SOCKS5 Proxy Server started on {self._host}:{self._port}")
        async with self.server:
            await self.server.serve_forever()

    @logger(_module_name)
    def stop_server(self):
        """
        Stops the proxy server and closes the event loop.
        """
        if self.server_task:
            self.server_task.cancel()
            scan_log.info_status_result(_module_name, "STOPPED", "Proxy server stopped.")
        if self.server:
            self.loop.call_soon_threadsafe(self.loop.stop)  # Stop the event loop
            self.server_thread.join()  # Wait for the thread to finish

    @logger(_module_name)
    def _load_external_servers(self, config_file:str):
        """
        Loads the external servers from the given JSON configuration file.
        :param config_file: Path to the JSON configuration file.
        :return: List of external server dictionaries with 'host', 'port', 'user', and 'password'.
        """
        if not os.path.exists(config_file):
            scan_log.error_status_result(_module_name, "ERROR", f"Configuration file '{config_file}' not found.")
            return []

        with open(config_file, 'r') as file:
            data = json.load(file)
            servers = data.get("servers", [])
            scan_log.info_status_result(_module_name, "SUCCESS", f"Loaded {len(servers)} external servers from '{config_file}'")
            return servers

    @logger(_module_name)
    async def _handle_client(self, client_reader:StreamReader, client_writer:StreamWriter):
        """
        Handles a client connection to the proxy server asynchronously.
        :param client_reader: The asyncio StreamReader object representing the client connection.
        :param client_writer: The asyncio StreamWriter object representing the client connection.
        """
        try:
            # Получаем команду от клиента
            data = await client_reader.read(4096)
            command = data.decode().strip()

            # Проверяем, что команда не пустая
            if not command:
                scan_log.error_status_result(_executor_name, "ERROR", "Empty command received.")
                client_writer.close()
                await client_writer.wait_closed()
                return

            # Выбираем случайный сервер из списка для выполнения команды
            if not self._external_servers:
                scan_log.error_status_result(_executor_name, "ERROR", "No external servers found. Ensure the config file is correct.")
                client_writer.close()
                await client_writer.wait_closed()
                return

            external_server = random.choice(self._external_servers)
            result = await self._execute_remote_command(external_server, command)

            # Отправляем результат обратно клиенту
            client_writer.write(result.encode())
            await client_writer.drain()
        except Exception as e:
            scan_log.error_status_result(_executor_name, "FAILED", f"Handling client command: {e}")
        finally:
            client_writer.close()
            await client_writer.wait_closed()

    @staticmethod
    def executor_log(log_type:LogLevel, server_info:dict, status:str, message:str):
        ip = f"{server_info['host']}:{server_info['port']}" if server_info else ""
        scan_log.log_result(log_type, _executor_name, message, ip, status)

    @logger(_module_name)
    async def proxy_execute(self, command:str):
        """
        Executes a command on a remote server chosen from the configured external servers.
        :param command: Command to execute on the remote server.
        :return: Result of the command execution.
        """
        self.executor_log(LogLevel.INFO, {}, "START", "Local command execution")
        # Check if external servers are available
        if not self._external_servers:
            self.executor_log(LogLevel.ERROR, {}, "ERROR", "No external servers found.")
            return None

        # Execute the command and return the result by random server
        return await self._execute_remote_command(random.choice(self._external_servers), command)

    @logger(_module_name)
    async def _execute_remote_command(self, server_info:dict, command:str):
        """
        Executes a command on a remote server over SSH and returns the output.
        :param server_info: Dictionary containing 'host', 'port', 'user', and 'password' of the server.
        :param command: The command to execute.
        :return: Output from the remote command execution.
        """
        scan_log.info_status_result(_executor_name, "EXECUTE", f"Command: '{command}'")
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Подключаемся к серверу
            self.executor_log(LogLevel.INFO, server_info, "CONNECTION", "Try to connect for command execution.")
            ssh_client.connect(
                hostname=server_info['host'],
                port=server_info['port'],
                username=server_info['user'],
                password=server_info['password']
            )
            self.executor_log(LogLevel.INFO, server_info, "SUCCESS", "Connection established.")

            # Выполняем команду и получаем результат
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            ssh_client.close()
            self.executor_log(LogLevel.INFO, server_info, "COMPLETE", "The command call has been successful. Connection closed.")

            # Возвращаем либо результат выполнения, либо ошибку
            if output:
                self.executor_log(LogLevel.INFO, server_info, "RESULT", f"Command feedback:\n{output}")
            elif error:
                self.executor_log(LogLevel.ERROR, server_info, "FAILED", f"Command feedback:\n{error}")
            else:
                self.executor_log(LogLevel.INFO, server_info, "RESULT", f"Command feedback is blank.")
            return output if output else error
        except Exception as e:
            self.executor_log(LogLevel.ERROR, server_info, "ERROR", f"Remote command execution failed: {e}")
            return None


async def main():
    proxy = ProxyServer()
    proxy.start_background()
    time.sleep(3)
    await proxy.proxy_execute("cd /")


# To start the proxy server
if __name__ == "__main__":
    asyncio.run(main())
