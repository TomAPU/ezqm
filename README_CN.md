# EZQM

让 QEMU 调Linux内核调得更舒服

- [English](README.md)
- [中文文档](README_CN.md)

# 跑起来
## 先决条件

EZQM 仅在 Linux 上经过测试。它**绝对**无法在 Windows 上运行，并且很可能无法在 macOS 上运行。

EZQM 是一个基于 Python 的工具，开发和测试环境为 Python 3.8。在开发过程中，我并未使用 Python 3.8 的高级特性，因此它应该能兼容大多数 Python 3 版本。不过需要注意的是，我使用了 `pexpect` 库，所以可能需要 Python 3.2 及以上版本。

EZQM 使用 `setuptools` 进行安装配置，`setuptools` 不是官方内置库，但通常会预装。如果你的系统没有安装它，可以运行以下命令安装：

```bash
pip3 install setuptools
```

EZQM 还需要系统中安装 `QEMU`（具体为 `qemu-system-x86_64`）、`gdb` 和 `scp`。如果这些工具未安装，可以询问 ChatGPT 或查阅 Stackoverflow 来完成安装。

EZQM 通过 `kvm` 运行 `QEMU`，因此你需要确保当前用户对 `kvm` 模块有访问权限（也就是说，你的用户属于 `kvm` 用户组，或者以 root 身份运行）。

## 安装

EZQM 是一个 PYPI 包，因此你可以直接使用 `pip` 进行安装：

```bash
pip3 install ezqm
```

你也可以克隆此项目并运行 `setup.py` 进行安装：

```bash
git clone https://github.com/TomAPU/ezqm.git
cd ezqm 
python3 setup.py --install
```

安装完成后，四个 EZQM 应用程序 `ezcf`、`ezcp`、`ezgdb` 和 `ezqm` 将被安装到系统中。

# EZQM 的磁盘镜像生成和配置

要调试 Linux 内核，需要一个磁盘镜像和一个内核镜像。我们可以生成一个磁盘镜像，并用它来调试不同的内核。

因此，EZQM 被设计为通过全局设置配置一个磁盘镜像，并将该镜像用于所有本地项目（我们稍后会讨论本地项目）。

## 磁盘镜像生成
我们可以使用 `Syzkaller` 提供的 `create-image.sh` 脚本生成一个磁盘镜像和对应的 SSH 密钥。

需要注意的是，EZQM 的自动化内存快照创建功能**仅**支持通过此脚本生成的磁盘镜像，因此建议使用此脚本以确保 EZQM 的完整功能。

```bash
wget https://raw.githubusercontent.com/google/syzkaller/master/tools/create-image.sh
chmod +x create-image.sh
./create-image.sh
```

执行脚本后，应该会看到两个文件，一个以 `.img` 结尾，另一个以 `.key` 结尾。例如：`stretch.img` 和 `stretch.img.key`。

`.img` 文件是磁盘镜像，而 `.key` 文件是对应的密钥文件，可用于通过 SSH 登录到虚拟机。


## 为 EZQM 配置磁盘镜像和 SSH 密钥

`ezcf` 是用于设置 EZQM 项目配置的工具。

使用以下命令调用 `ezcf`，为 EZQM 的初始设置配置磁盘镜像和 SSH 密钥：

```bash
ezcf -g -u diskimage <path/to/your/image>
ezcf -g -u sshkey  <path/to/your/rsakey>
```

### 翻译文档：

这两个配置是全局设置（`-g`），会影响所有 EZQM 的本地项目。

全局设置存储在 `~/.config/ezqmglobal.json` 文件中。这是设置跟着用户走，确保每个用户的配置互不干扰。因此，如果切换到其他用户账户，需要重新配置全局设置。


# 创建本地项目

“本地项目”是我自己定义的术语，它由一个文件夹和该文件夹下的一个 `ezqmlocal.json` 文件组成，用于存储启动 QEMU 的配置。

要在本地项目之间切换，只需 `cd` 到你要切换的本地项目对应的文件夹，`ezcf`、`ezcp`、`ezgdb` 和 `ezqm` 将会自动读取该文件夹下的 `ezqmlocal.json`。

要创建本地项目，你需要先完成全局配置，并准备一个包含源码和已编译的 Linux 内核镜像的文件夹。  
然后可以执行以下命令：

```bash
mkdir myproj && cd myproj 
ezcf --init-local <folder/to/your/compiled/linux/source/folder> 
```

执行后，你会在你的文件夹下发现一个`ezqmlocal.json`文件，其内容类似这样：
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

如果要配置本地项目，可以手动编辑`ezqmlocal.json`或使用`ezcf`的`-l`

```bash
ezcf -l -u key val
```

# 使用 `ezqm` 启动 QEMU

设置完成后，只需“cd”到本地项目文件夹并使用以下命令启动 QEMU

```bash
ezqm
``` 

# 使用内存快照跳过 QEMU 启动（可选）

通过在 QEMU 启动后拍摄快照，并在每次启动 QEMU 时恢复内存快照，可以加快启动速度！这样我们就不需要再等待 QEMU 启动了。

首先，我们需要一个文件夹来存储 QEMU 的内存快照。为了减少读取时间，理想的做法是创建一个 `ramfs`，可以通过以下命令完成：

```bash
mount ramfs -t ramfs <path/to/your/folder>
```

然后我们使用ezcf来全局配置这个文件夹：

```bash
ezcf -g -u snapshotfolder <path/to/your/folder>
```

使用以下命令创建快照并设置启动参数（目前仅适用于 Syzkaller 的 create-image.sh 创建的磁盘映像）

```bash
ezqm -b
```
使用 `-b` 选项，`ezqm` 将自动启动 QEMU，登录虚拟机，拍摄快照并存储到 `snapshotfolder`，更改本地配置文件。
这样下次您只需调用 `ezqm` 并享受带有内存快照的 QEMU


# 使用 GDB 包装器 `ezgdb` 调试内核
ezgdb 是用于调试内核的工具，它基本上将命令转换为 `gdb` 命令并启动 gdb，因此您不必自己指定 `vmlinux` 路径或 `gdb` 端口！

1. **使用 `vmlinux` 启动 GDB**：
   ```bash
   ezgdb
   ```
   等价于:
   ```bash
   gdb <vmlinux>
   ```

2. **连接到虚拟机**：
   ```bash
   ezgdb conn
   ```
   等价于:
   ```bash
   gdb <vmlinux> -ex "target remote :<gdbport>"
   ```


3. **自定义GDB命令**：
   ```bash
   ezgdb --ex "break KASAN"
   ```
   等价于:
   ```bash
   gdb <vmlinux> --ex "break main"
   ```

# 使用 `ezcp` 进行文件传输

`ezcp` 工具允许您在主机和虚拟机 (VM) 之间传输文件或文件夹。您还可以反向传输文件，从 VM 传输到主机。

## 从主机传输到虚拟机
要将文件或文件夹从主机复制到虚拟机，请使用以下命令

```bash
ezcp <source> <destination>
```

- `<source>`：主机上文件或文件夹的路径。  
- `<destination>`：文件或文件夹在虚拟机中存放的位置。

### 示例
```bash
ezcp /path/to/file.txt /path/on/vm
```

## 从虚拟机传输到主机
要将文件或文件夹从虚拟机传输到主机，请使用 `--reverse` 或 `-r` 选项：

```bash
ezcp -r <source> <destination>
```

- `<source>`：虚拟机中文件或文件夹的路径。  
- `<destination>`：文件或文件夹在主机中存放的位置。