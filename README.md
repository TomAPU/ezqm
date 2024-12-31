# EZQM

Making it easier for using QEMU to debug Linux kernel.

- [中文文档](README_CN.md)
- [English](README.md)

# Setting up 
## Prerequisites
EZQM is only tested on Linux. It *definitely* doesn't work on Windows, and probably doesn't work on macOS. 

EZQM is a Python-based tool developed and tested on Python 3.8. During the development, I didn't use any fancy features of Python 3.8 so it should work on a wide variety of Python 3 versions. 
It should be noted that I did use the `pexpect` library so we may need a Python 3.2+. 

EZQM is set up by `setuptools` which is not an official built-in library but often pre-installed.
If you don't have it, run:

```bash
pip3 install setuptools
```

EZQM also requires you to have `QEMU` (to be specific `qemu-system-x86_64`) and `gdb` and `scp` installed. If you don't have them, go ask ChatGPT or Stackoverflow to install them. 

EZQM runs `QEMU` by `kvm`, so you need to ensure your current user has access to the `kvm` module (i.e inside the `kvm` user group or being root)

## Installation
EZQM is a PYPI package so you can simply use `pip` to install 

```bash
pip3 install ezqm
```

You can also clone this project and run `setup.py`
```bash
git clone https://github.com/TomAPU/ezqm.git
cd ezqm 
python3 setup.py --install
```

After installation, four EZQM apps `ezcf`,`ezcp`,`ezgdb`,`ezqm` will be installed.


# Disk image generation and configuration for EZQM
To debug Linux kernels, you need a disk image and a kernel image. We can generate one disk image and use it to debug different kernels. 

Thus, EZQM is designed to be configured with one disk image into its global settings and use the image for all local projects (we'll discuss local projects later). 

## Disk image generation
We can use `Syzkaller`'s create-image.sh to create a disk image and corresponding SSH key. 
It should ne noted that EZQM's automated memory snapshot creating feature *only* supports disk images created by this script, so it is advised to use this script for EZQM.

```bash
wget https://raw.githubusercontent.com/google/syzkaller/master/tools/create-image.sh
chmod +x create-image.sh
./create-image.sh
```

After executing, you are expected to see a file ending with .img and ending with .key, for example, stretch.img and stretch.img.key 

The .img file is the disk image and the .key file is the corresponding file that can be used to ssh into the virtual machine.

## Configure the disk image and SSH key for EZQM

`ezcf` is the tool for configuration setting for EZQM project.

Use following commands to invoke `ezcf` set the disk image and SSH key for EZQM's initial setup.  

```bash
ezcf -g -u diskimage <path/to/your/image>
ezcf -g -u sshkey  <path/to/your/rsakey>
```

These two configurations are global settings (`-g`) and will affect all EZQM local projects.

Global settings are stored at `~/.config/ezqmglobal.json`. This per-user setting ensures that each user's configurations remain isolated. So if you switch to a different user, you need to reconfigure the global setting.


# Creating a local project 

"local project" is a term I created myself, it consists of a folder and an `ezqmlocal.json` under that folder, containing settings for a booting up the QEMU. 

To switch between local projects, just `cd` into the corresponding folder of the local project you want to switch to, and `ezcf`,`ezcp`,`ezgdb`,`ezqm` will automatically read the `ezqmlocal.json` under that folder.

To create a local project, you need to have global configurations set, and you need a folder that contains the source code and the compiled Linux kernel image.  
Then you can execute the following command:

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
    "kernelparam": "nokaslr console=ttyS0 root=/dev/sda rw kasan_multi_shot=1 printk.synchronous=1 net.ifnames=0 biosdevname=0",
    "additionalcmd": []
}
```

If you want to configure the local project, you can manually edit the  `ezqmlocal.json` or use `ezcf`'s `-l` 

```bash
ezcf -l -u key val
```

# Start QEMU with `ezqm` 
After setting up, simply `cd` to the local project folder and use the following command to launch the QEMU

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
With `-b` option, the `ezqm` will automatically launch the QEMU, log into the virtual machine, take snapshot and save into the `snapshotfolder`, change the local configuration file. 
So that next time you simply invoke `ezqm` and enjoy the QEMU with memory snapshot  


# Debug the kernel with the GDB wrapper `ezgdb`
ezgdb is the tool for debugging the kernel, it basically translates the command to the `gdb` one and starts the gdb so you don't have to specify `vmlinux` path or `gdb` port yourself!

1. **Launch GDB with `vmlinux`**:
   ```bash
   ezgdb
   ```
   Equivalent to:
   ```bash
   gdb <vmlinux>
   ```

2. **Connect to the virtual machine**:
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


## Transfer from Host to VM
To copy a file or folder from the host machine to the VM, use the following command:

```bash
ezcp <source> <destination>
```

- `<source>`: Path to the file or folder on the host.
- `<destination>`: Path where the file or folder should be placed on the VM.

### Example
```bash
ezcp /path/to/file.txt /path/on/vm
```

## Transfer from VM to Host
To copy a file or folder from the VM to the host machine, use the `--reverse` or `-r` option:

```bash
ezcp -r <source> <destination>
```

- `<source>`: Path to the file or folder on the VM.
- `<destination>`: Path where the file or folder should be placed on the host.

