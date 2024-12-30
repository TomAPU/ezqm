#!/usr/bin/python3
import os
import json
import argparse
from .ezlib.printing import print_succ, print_fail, print_status
from .ezlib.settings import (
    read_config,
    write_config,
    get_global_settings_path,
    get_local_settings_path,
)
from .ezlib.utils import is_folder, rand_port, rand_tmp_file


def initialize_local_settings(linux_src_folder: str):
    """
    Initialize local settings with the path to the Linux source code folder.
    We initialize:
    - src: path to the Linux source code folder
    - vmlinux: path to the vmlinux file
    - bzImage: path to the bzImage file
    - gdbport: port for GDB
    - qemuport: port for QEMU
    - sshport: port for SSH
    - outputfile: temporary file for QEMU output
    - kernelparam: kernel parameters for QEMU
    - additionalcmd: additional commands to run before QEMU
    """
    config = dict()
    if not is_folder(linux_src_folder):
        print_fail(f"Folder '{linux_src_folder}' does not exist.")
        return
    config["src"] = linux_src_folder
    config["vmlinux"] = os.path.join(linux_src_folder, "vmlinux")
    config["bzImage"] = os.path.join(linux_src_folder, "arch/x86/boot/bzImage")
    config["gdbport"] = rand_port()
    config["qemuport"] = rand_port()
    config["sshport"] = rand_port()
    config["outputfile"] = rand_tmp_file()
    config["kernelparam"] = (
        "nokaslr console=ttyS0 root=/dev/sda rw kasan_multi_shot=1 printk.synchronous=1"
    )
    config["additionalcmd"] = []
    try:
        write_config(get_local_settings_path(), config)
        print_succ(f"Initialized local settings successfully.")
    except Exception as e:
        print_fail(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage global and local settings for the ezqm project."
    )

    # Add global/local flags
    parser.add_argument(
        "-g",
        "--global",
        dest="global_scope",
        action="store_true",
        help="Operate on global settings",
    )
    parser.add_argument(
        "-l",
        "--local",
        dest="local_scope",
        action="store_true",
        help="Operate on local settings",
    )

    # Add init-local argument
    parser.add_argument(
        "--init-local",
        metavar="LINUX_SRC_FOLDER",
        help="Initialize local settings with the path to the Linux source code folder.",
    )

    # Add update key-value pair arguments
    parser.add_argument(
        "-u",
        "--update",
        nargs=2,
        action="append",
        metavar=("KEY", "VALUE"),
        help="Update key-value pairs in the configuration. Can be used multiple times.",
    )

    # Add read key argument
    parser.add_argument(
        "-r",
        "--read",
        metavar="KEY",
        nargs="?",
        const="",
        help="Read a specific key from the configuration. If no key is provided, all key-value pairs are printed.",
    )

    # Parse arguments
    args = parser.parse_args()

    # Initialize local settings
    if args.init_local:
        initialize_local_settings(args.init_local)
        return

    # Ensure valid arguments
    if args.global_scope and args.local_scope:
        print_fail("You cannot specify both --global/-g and --local/-l.")
        parser.print_help()
        return

    if not args.global_scope and not args.local_scope:
        print_fail("You must specify either --global/-g or --local/-l.")
        parser.print_help()
        return

    # Determine file path
    config_path = (
        get_global_settings_path() if args.global_scope else get_local_settings_path()
    )

    # Enforce mutual exclusivity between read and update
    if args.read and args.update:
        print_fail(
            "You cannot perform both read and update operations in the same command."
        )
        parser.print_help()
        return

    # Perform updates
    if args.update:
        try:
            settings = read_config(config_path)  # Read current settings
            for key, value in args.update:
                settings[key] = value
            write_config(config_path, settings)  # Write updated settings
            print_succ(f"Updated settings successfully.")
        except Exception as e:
            print_fail(f"An error occurred: {e}")
            parser.print_help()

    # Perform read
    elif args.read is not None:
        try:
            settings = read_config(config_path)  # Read current settings
            if args.read == "":
                print_status(f"All settings:")
                print(json.dumps(settings, indent=4))
            elif args.read in settings:
                print_status(f"{args.read}: {settings[args.read]}")
            else:
                print_fail(f"Key '{args.read}' not found in settings.")
        except Exception as e:
            print_fail(f"An error occurred: {e}")
            parser.print_help()
    else:
        print_fail("You must specify either --read or --update.")
        parser.print_help()


if __name__ == "__main__":
    main()
