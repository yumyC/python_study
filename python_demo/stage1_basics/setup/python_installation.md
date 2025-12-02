# Python 安装指南

## 概述

本指南将帮助你在不同操作系统上安装 Python 3.9 或更高版本。

## Windows 系统安装

### 方法一：官方安装包（推荐）

1. **下载 Python 安装包**
   - 访问 Python 官网：https://www.python.org/downloads/
   - 点击 "Download Python 3.x.x" 按钮下载最新版本
   - 建议下载 Python 3.9 或更高版本

2. **运行安装程序**
   - 双击下载的 `.exe` 文件
   - **重要**：勾选 "Add Python to PATH" 选项
   - 选择 "Install Now" 进行标准安装
   - 或选择 "Customize installation" 自定义安装路径

3. **验证安装**
   ```bash
   # 打开命令提示符（CMD）或 PowerShell
   python --version
   # 应该显示：Python 3.x.x
   
   pip --version
   # 应该显示：pip 23.x.x from ...
   ```

### 方法二：Microsoft Store

1. 打开 Microsoft Store
2. 搜索 "Python 3.11" 或更高版本
3. 点击 "获取" 进行安装
4. 安装完成后验证版本

## macOS 系统安装

### 方法一：官方安装包

1. **下载 Python 安装包**
   - 访问：https://www.python.org/downloads/macos/
   - 下载适合你系统的 `.pkg` 文件

2. **运行安装程序**
   - 双击 `.pkg` 文件
   - 按照安装向导完成安装

3. **验证安装**
   ```bash
   # 打开终端（Terminal）
   python3 --version
   pip3 --version
   ```

### 方法二：Homebrew（推荐）

1. **安装 Homebrew**（如果未安装）
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **使用 Homebrew 安装 Python**
   ```bash
   brew install python@3.11
   ```

3. **验证安装**
   ```bash
   python3 --version
   pip3 --version
   ```

## Linux 系统安装

### Ubuntu/Debian

1. **更新包管理器**
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **安装 Python**
   ```bash
   # 安装 Python 3.11
   sudo apt install python3.11 python3.11-venv python3-pip
   ```

3. **验证安装**
   ```bash
   python3 --version
   pip3 --version
   ```

### CentOS/RHEL/Fedora

1. **安装 Python**
   ```bash
   # Fedora
   sudo dnf install python3.11
   
   # CentOS/RHEL
   sudo yum install python3.11
   ```

2. **验证安装**
   ```bash
   python3 --version
   pip3 --version
   ```

## 配置 pip 镜像源（可选，提升下载速度）

### 临时使用镜像源
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name
```

### 永久配置镜像源

**Windows**
```bash
# 创建配置文件
mkdir %USERPROFILE%\pip
notepad %USERPROFILE%\pip\pip.ini
```

在 `pip.ini` 中添加：
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

**macOS/Linux**
```bash
# 创建配置文件
mkdir -p ~/.pip
nano ~/.pip/pip.conf
```

在 `pip.conf` 中添加：
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

### 常用国内镜像源

- 清华大学：https://pypi.tuna.tsinghua.edu.cn/simple
- 阿里云：https://mirrors.aliyun.com/pypi/simple/
- 中国科技大学：https://pypi.mirrors.ustc.edu.cn/simple/
- 豆瓣：https://pypi.douban.com/simple/

## 升级 pip

安装完成后，建议升级 pip 到最新版本：

```bash
# Windows
python -m pip install --upgrade pip

# macOS/Linux
python3 -m pip install --upgrade pip
```

## 常见问题

### 问题 1：命令找不到 python

**Windows**
- 确保安装时勾选了 "Add Python to PATH"
- 手动添加 Python 到环境变量

**macOS/Linux**
- 使用 `python3` 而不是 `python`
- 或创建别名：`alias python=python3`

### 问题 2：pip 安装包失败

- 检查网络连接
- 使用国内镜像源
- 升级 pip 版本
- 使用管理员权限运行

### 问题 3：多个 Python 版本共存

- 使用完整路径调用特定版本
- Windows: `py -3.11` 或 `py -3.9`
- Linux/macOS: `python3.11` 或 `python3.9`

## 下一步

安装完成后，请继续学习：
- [PyCharm 虚拟环境设置](pycharm_setup.md)
- [VSCode 虚拟环境设置](vscode_setup.md)
- [虚拟环境使用指南](virtual_env_guide.md)

## 参考资源

- Python 官方文档：https://docs.python.org/zh-cn/3/
- Python 官方下载页：https://www.python.org/downloads/
- pip 官方文档：https://pip.pypa.io/
