import os
import random
import shutil
import pexpect
from .printing import print_status, print_succ, print_fail
from typing import List
import shlex
import socket
from argparse import ArgumentParser
from .settings import check_global_settings,check_local_settings

def random_num(low: int, high: int) -> int:
    """
    Generate a random number between low and high
    """
    return random.randint(low, high)


def is_folder(path: str) -> bool:
    """
    Check if the path is a folder
    """
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    """
    Check if the path is a file
    """
    return os.path.isfile(path)


def rand_port() -> int:
    """
    Generate a random port number
    """
    return random_num(30000, 65535)


def rand_string(length: int) -> str:
    """
    Generate a random string of a given length from a-zA-Z0-9
    """
    return "".join(
        random.choices(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=length
        )
    )


def rand_tmp_file() -> str:
    """
    Generate a random temporary file name
    """
    return f"/tmp/{rand_string(10)}"


def confguard(parser:ArgumentParser) -> None:
    try:
        check_global_settings()
        check_local_settings()
    except Exception as e:
        parser.print_help()
        exit(1)

def exec_command(command: List[str]) -> None:
    """
    Executes a command, replacing the current process.

    Args:
        command (List[str]): A list of strings where the first element is the command
                             and the rest are its arguments.
    """
    if not isinstance(command, list):
        raise ValueError("Command must be provided as a list of strings.")

    # Validate the command using shutil.which
    if shutil.which(command[0]) is None:
        raise FileNotFoundError(f"Command '{command[0]}' not found.")

    # Replace the current process
    os.execvp(command[0], command)


def generate_qemu_command(gconf: dict, lconf: dict) -> List[str]:
    command = []
    command.extend(
        [
            "qemu-system-x86_64",
            "-m",
            "2048",
            "-gdb",
            f"tcp::{lconf['gdbport']}",
            f"-monitor",
            f"tcp::{lconf['qemuport']},server,nowait",
            "-smp",
            "4",
            "-display",
            "none",
        ]
    )
    command.extend(["-chardev", f"stdio,id=char0,logfile={lconf['outputfile']},signal=on"])
    command.extend(
        [
            "-serial",
            "chardev:char0",
            "-no-reboot",
            "-device",
            "virtio-rng-pci",
            "-enable-kvm",
            "-cpu",
            "host,migratable=on",
            "-device",
            "e1000,netdev=net0",
            "-nographic",
            "-snapshot",
        ]
    )
    command.extend(
        [
            "-netdev",
            f"user,id=net0,restrict=on,hostfwd=tcp:127.0.0.1:{lconf['sshport']}-:22",
        ]
    )
    if "snapshot_file" in lconf:
        snapshot_file=lconf["snapshot_file"]
        command.extend(["-incoming",  f'exec: cat {snapshot_file}'])
    command.extend(["-drive", f"file={gconf['diskimage']}"])
    command.extend(["-kernel", lconf["bzImage"], "-append", lconf["kernelparam"]])
    command.extend(lconf["additionalcmd"])
    return command


def start_qemu_and_login(qemu_cmd: List[str]) -> pexpect.spawn:
    """
    Start QEMU using the generated command, wait for the prompt, and login.

    Returns:
        pexpect.spawn: The pexpect session connected to the QEMU process.
    """

    try:
        print_status("Starting QEMU and logging in...")
        # Start QEMU as a subprocess
        qemu_process = pexpect.spawn(shlex.join(qemu_cmd), timeout=300)

        # Wait for the login prompt
        qemu_process.expect("syzkaller login:")
        print_status("Received login prompt.")

        # Send the username 'root' and a newline to login
        qemu_process.sendline("root")
        print_succ("Sent login credentials.")

        # Wait for # prompt
        qemu_process.expect("#")
        print_succ("Logged in successfully.")

        # Return the process for further interaction
        return qemu_process

    except pexpect.exceptions.TIMEOUT:
        print_fail("Timed out while waiting for the login prompt.")
        qemu_process.terminate()
        raise

    except Exception as e:
        print_fail(f"Failed to start QEMU or login: {e}")
        raise


def execute_qemu_command(qemu_port: int, command: str, timeout: int = 60) -> str:
    """
    Connect to the QEMU monitor port, drain initial message, send a command, and capture the response.

    Args:
        qemu_port (int): The port to connect to QEMU's monitor.
        command (str): The command to send to QEMU.
        timeout (int): Timeout in seconds for the response.

    Returns:
        str: The response from QEMU before the "(qemu)" prompt.
    """
    try:
        print_status(f"Connecting to QEMU on port {qemu_port}...")
        with socket.create_connection(("localhost", qemu_port), timeout=10) as sock:
            print_status("Connected to QEMU monitor.")

            # Drain the initial QEMU welcome message
            response = b""
            sock.settimeout(timeout)
            while b"(qemu)" not in response:
                data = sock.recv(1024)
                if not data:
                    raise ConnectionError("Connection closed by QEMU.")
                response += data

            print_status("Initial QEMU message drained.")

            # Send the command
            sock.sendall((command + "\n").encode("utf-8"))
            print_status(f"Sent command: {command}")

            # Collect response until (qemu) prompt
            response = b""
            while b"(qemu)" not in response:
                data = sock.recv(1024)
                if not data:
                    raise ConnectionError("Connection closed by QEMU.")
                response += data

            # Extract the response before (qemu)
            response_str = response.decode("utf-8")
            result = response_str.split("(qemu)")[0].strip()
            return result
    except Exception as e:
        print(f"Error during QEMU command execution: {e}")
        raise