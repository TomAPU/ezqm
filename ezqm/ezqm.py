#!/usr/bin/python3
import os
import argparse
import pexpect
from .ezlib.settings import (
    read_global_settings,
    write_local_settings,
    read_local_settings,
    validate_settings,
)
from .ezlib.printing import print_status, print_fail
from .ezlib.utils import (
    exec_command,
    generate_qemu_command,
    start_qemu_and_login,
    execute_qemu_command,
    rand_string,
    confguard
)




def main():
    parser = argparse.ArgumentParser(description="ezqm - Simplified QEMU launching.")

    parser.add_argument(
        "-b",
        "--build-memory-snapshot",
        action="store_true",
        help="Build a memory snapshot to facilitate QEMU. This only works for diskimage created by Syzkaller's create-image.sh",
    )

    args = parser.parse_args()
    confguard(parser)
    
    gconf = read_global_settings()
    lconf = read_local_settings()

    if args.build_memory_snapshot:
        # Read snapshotfolder from global settings
        # check if snapshotfolder exists
        try:
            validate_settings(
                gconf,
                {"snapshotfolder": {"required": True, "path_type": "directory"}},
                "global settings",
            )
        except Exception as e:
            print_fail(f"Error in global settings: {e}")
            print_status(
                "Please use ezcf -g -u snapshotfolder <path/to/your/folder> to set the snapshot folder first."
            )
            return
        if "snapshot_file" in lconf:
            print_status("A memory snapshot already exists, deleting it and regenerating.")
            os.remove(lconf["snapshot_file"])
            del lconf["snapshot_file"]
        qemu_cmd = generate_qemu_command(gconf, lconf)
        # Generate snapshot file path
        snapshot_file = os.path.join(gconf["snapshotfolder"], rand_string(10))
        print_status(f"Building memory snapshot to {snapshot_file}...")
        p: pexpect.pty_spawn.spawn = start_qemu_and_login(qemu_cmd)
        ret = execute_qemu_command(
            lconf["qemuport"], f'migrate "exec: cat > {snapshot_file}"'
        )
        print_status("Return of qemu port:", ret)
        # Check if the snapshot file exists
        if os.path.exists(snapshot_file):
            print_status(f"Memory snapshot built successfully at {snapshot_file}.")
            # Update the local settings
            lconf["snapshot_file"] = snapshot_file
            # Write the updated local settings
            write_local_settings(lconf)
            print_status("Updated local settings with the memory snapshot.")
        else:
            print_fail(f"Memory snapshot failed to build at {snapshot_file}.")
        p.close(force=True)
    else:
        qemu_cmd = generate_qemu_command(gconf, lconf)
        print_status("Executing:",qemu_cmd)
        exec_command(qemu_cmd)


if __name__ == "__main__":
    main()
