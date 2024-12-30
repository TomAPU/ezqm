#!/usr/bin/python3
import argparse
import sys
from .ezlib.settings import read_local_settings
from .ezlib.utils import exec_command, confguard
from .ezlib.printing import print_status

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
    parser.add_argument(
        "gdb_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments passed directly to GDB.",
    )

    args = parser.parse_args()
    confguard(parser)

    # Read local settings
    lconf = read_local_settings()

    # Build the GDB command
    if args.subcommand == "conn":
        command = [
            "gdb",
            lconf["vmlinux"],
            "-ex",
            f"target remote :{lconf['gdbport']}",
        ] + args.gdb_args
    elif args.subcommand is None:
        command = ["gdb", lconf["vmlinux"]] + args.gdb_args
    else:
        print(f"Unknown subcommand: {args.subcommand}")
        parser.print_help()
        sys.exit(1)
    print_status(f"Executing:", command)
    # Execute the command
    exec_command(command)


if __name__ == "__main__":
    main()
