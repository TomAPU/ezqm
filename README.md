# EZQM

Making QEMU Environment easier to be setup & run.


# Disk image generation and configuration for EZQM

Using Syzkaller's create-image.sh to create a disk image and corresponding SSH key. 
```bash
wget https://raw.githubusercontent.com/google/syzkaller/master/tools/create-image.sh
chmod +x create-image.sh
./create-image.sh
```

After creation, use following command to configure the disk image and SSH key used by EZQM. 

These configuration will affect all EZQM local projects (we'll talk about local projects later!)

```bash
ezcf -g -u diskimage <path/to/your/image>
ezcf -g -u sshkey  <path/to/your/rsakey>
```

# Creating a local project 
To create a local project, execute following command:
```bash
mkdir myproj && cd myproj 
ezcf --init-local <folder/to/your/compiled/linux/source/folder> 
```

After executing, you will find a `ezqmlocal.json` file under your folder with content like:
```json
{
    "src": "/xxxx/linux-upstream",
    "vmlinux": "/xxxx/linux-upstream/vmlinux",
    "bzImage": "/xxxx/linux-upstream/arch/x86/boot/bzImage",
    "gdbport": 11451,
    "qemuport": 19198,
    "sshport": 8964,
    "outputfile": "/tmp/bQZv746sBv",
    "kernelparam": "nokaslr console=ttyS0 root=/dev/sda rw kasan_multi_shot=1 printk.synchronous=1",
    "additionalcmd": []
}
```
Then, when you switch to that directory and execute EZQM related command, the corresponding `ezqmlocal.json` will be used as the local configuration file and can be configured by following command:

```bash
ezcf -l -u key val
```
# Start QEMU with `ezqm` 
After setting up, simply use the following command to launch the QEMU
```bash
ezqm
``` 

# Using memory snapshot to skip QEMU booting (optionl)!
Taking a snapshot after QEMU booting and restore the memory snapshot everytime we start QEMU to make things faster! We don't have to wait for QEMU boot anymore!
First we need a folder to store QEMU memorysnapshot. Ideally, creating a ramfs to reduce reading time by the following command:

```bash
mount ramfs -t ramfs <path/to/your/folder>
```

Then we use ezcf to configure this folder globally. 

```bash
ezcf -g -u snapshotfolder <path/to/your/folder>
```

Create snapshot and set booting parameter with the following command (Currently, only works for diskimage created by Syzkaller's create-image.sh)
```bash
ezqm -b
```

# Debug the kernel with the GDB wrapper `ezgdb`
ezgdb is the tool for this!
1. **Launch GDB with `vmlinux`**:
   ```bash
   ezgdb
   ```
   Equivalent to:
   ```bash
   gdb <vmlinux>
   ```

2. **Connect to a Remote Target**:
   ```bash
   ezgdb conn
   ```
   Equivalent to:
   ```bash
   gdb <vmlinux> -ex "target remote :<gdbport>"
   ```


3. **Custom GDB Commands**:
   ```bash
   ezgdb --ex "break KASAN"
   ```
   Equivalent to:
   ```bash
   gdb <vmlinux> --ex "break main"
   ```

# File transfering with `ezcp`

The `ezcp` tool allows you to transfer files or folders between the host machine and a virtual machine (VM). You can also transfer files in reverse, from the VM to the host.


### Transfer from Host to VM
To copy a file or folder from the host machine to the VM, use the following command:

```bash
ezcp <source> <destination>
```

- `<source>`: Path to the file or folder on the host.
- `<destination>`: Path where the file or folder should be placed on the VM.

#### Example
```bash
ezcp /path/to/file.txt /path/on/vm
```

### Transfer from VM to Host
To copy a file or folder from the VM to the host machine, use the `--reverse` or `-r` option:

```bash
ezcp --reverse <source> <destination>
```

- `<source>`: Path to the file or folder on the VM.
- `<destination>`: Path where the file or folder should be placed on the host.

