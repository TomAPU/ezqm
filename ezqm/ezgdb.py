#!/usr/bin/python3
import argparse
import sys
from .ezlib.settings import read_local_settings
from .ezlib.utils import exec_command, valid_or_exit
from .ezlib.printing import print_status
import os


class GdbArgumentParser(argparse.ArgumentParser):
    def print_help(self):
        super().print_help()
        print("=====Below is gdb's built-in help=====")
        exec_command(["gdb", "--help"])


def main():
    # Parse arguments
    parser = GdbArgumentParser(
        description="ezgdb: Simplified GDB wrapper for Linux kernel debugging."
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        default=None,
        help="Subcommand like 'conn', or leave empty for default GDB launch.",
    )
    args, remaining_args = parser.parse_known_args()

    valid_or_exit(parser)
    lconf = read_local_settings()
    command = ["gdb", lconf["vmlinux"], "-ex", "set filename-display absolute"]
    if args.subcommand == "conn":
        command.extend(["-ex", f"target remote :{lconf['gdbport']}"])
    elif args.subcommand is not None:
        command.extend([args.subcommand])
    command.extend(remaining_args)
    print_status(f"Executing:", command)
    # Execute the command
    exec_command(command)


if __name__ == "__main__":
    main()
