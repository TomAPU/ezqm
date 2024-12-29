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
    "tmpfile": "/tmp/bQZv746sBv",
    "kernelparam": "nokaslr console=ttyS0 root=/dev/sda rw kasan_multi_shot=1 printk.synchronous=1",
    "additionalcmd": []
}
```
Then, when you switch to that directory and execute EZQM related command, the corresponding `ezqmlocal.json` will be used as the local configuration file and can be configured by following command:

```bash
ezcf -l -u key val
```
