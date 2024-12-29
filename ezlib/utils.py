import os 
import random 
import shutil
from typing import List

def random_num(low:int, high:int)->int:
    '''
    Generate a random number between low and high
    '''
    return random.randint(low, high)

def is_folder(path:str)->bool:
    '''
    Check if the path is a folder
    '''
    return os.path.isdir(path)

def is_file(path:str)->bool:
    '''
    Check if the path is a file
    '''
    return os.path.isfile(path)

def rand_port()->int:
    '''
    Generate a random port number
    '''
    return random_num(30000, 65535)

def rand_string(length:int)->str:
    '''
    Generate a random string of a given length from a-zA-Z0-9
    '''
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=length))

def rand_tmp_file()->str:
    '''
    Generate a random temporary file name
    '''
    return f'/tmp/{rand_string(10)}'


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

def generate_qemu_command(gconf: dict, lconf: dict):
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
    command.extend(["-chardev", f"stdio,id=char0,logfile={lconf['tmpfile']},signal=on"])
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
    command.extend(["-drive", f"file={gconf['diskimage']}"])
    command.extend(["-kernel", lconf["bzImage"], "-append", lconf["kernelparam"]])
    command.extend(lconf["additionalcmd"])
    return command
