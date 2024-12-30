#!/usr/bin/python3
import os
import argparse
import pexpect
from .ezlib.settings import read_global_settings, read_local_settings
from .ezlib.utils import exec_command, confguard


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Transfer files or folders between host and VM."
    )
    parser.add_argument(
        "source", help="Path to the file or folder on the source system."
    )
    parser.add_argument(
        "destination", help="Path to the destination on the target system."
    )
    parser.add_argument(
        "-r", "--reverse", action="store_true", help="Transfer from VM to host."
    )
    args = parser.parse_args()
    confguard(parser)
    # Read global configuration
    gconf = read_global_settings()
    lconf = read_local_settings()
    
    ssh_key=gconf["sshkey"]
    port=lconf["sshport"]

    scp_command = [
            "scp",
            "-P",
            str(port),
            "-F",
            "/dev/null",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "BatchMode=yes",
            "-o",
            "IdentitiesOnly=yes",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ConnectTimeout=10",
            "-i",
            ssh_key,
            "-r",
            "-v"
        ]
    if args.reverse:
        # Transfer from VM to host
        remote_source = f"root@localhost:{args.source}"
        local_destination = args.destination
        scp_command += [remote_source, local_destination]
    else:
        # Transfer from host to VM
        local_source = args.source
        remote_destination = f"root@localhost:{args.destination}"
        scp_command += [local_source, remote_destination]

    # Execute the SCP command
    exec_command(scp_command)

if __name__ == "__main__":
    main()
