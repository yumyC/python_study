# Python 虚拟环境使用指南

## 什么是虚拟环境？

虚拟环境（Virtual Environment）是 Python 项目的独立运行环境，它允许你为每个项目创建隔离的 Python 环境，包含独立的包和依赖。

### 为什么需要虚拟环境？

1. **依赖隔离**: 不同项目可以使用不同版本的包，避免冲突
2. **环境清洁**: 不污染系统全局 Python 环境
3. **便于迁移**: 通过 requirements.txt 轻松复制环境
4. **权限管理**: 不需要管理员权限安装包
5. **版本控制**: 明确项目依赖，便于团队协作

### 示例场景

假设你有两个项目：
- 项目 A 需要 Django 3.2
- 项目 B 需要 Django 4.2

如果不使用虚拟环境，两个版本会冲突。使用虚拟环境后，每个项目有独立的 Django 版本。

## 虚拟环境工具对比

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| **venv** | Python 内置，轻量级 | 推荐用于大多数项目 |
| **virtualenv** | 功能更强，支持旧版 Python | 需要兼容 Python 2.x |
| **conda** | 管理 Python 和非 Python 包 | 数据科学、机器学习项目 |
| **pipenv** | 结合 pip 和 virtualenv | 需要 Pipfile 管理 |
| **poetry** | 现代依赖管理工具 | 需要高级依赖解析 |

本指南主要介绍 **venv**（推荐）。

## 使用 venv 创建虚拟环境

### 创建虚拟环境

**Windows**:
```bash
# 在项目目录下
python -m venv venv
```

**macOS/Linux**:
```bash
python3 -m venv venv
```

### 命令解释

- `python -m venv`: 运行 venv 模块
- `venv`: 虚拟环境文件夹名称（可自定义，如 `.venv`、`env`）

### 虚拟环境目录结构

创建后会生成以下结构：

**Windows**:
```
venv/
├── Include/
├── Lib/
│   └── site-packages/    # 安装的包存放位置
├── Scripts/
│   ├── activate.bat      # CMD 激活脚本
│   ├── Activate.ps1      # PowerShell 激活脚本
│   ├── deactivate.bat    # 停用脚本
│   ├── pip.exe           # pip 工具
│   └── python.exe        # Python 解释器
└── pyvenv.cfg            # 配置文件
```

**macOS/Linux**:
```
venv/
├── bin/
│   ├── activate          # 激活脚本
│   ├── pip               # pip 工具
│   └── python            # Python 解释器
├── include/
├── lib/
│   └── python3.x/
│       └── site-packages/
└── pyvenv.cfg
```

## 激活虚拟环境

### Windows

**CMD**:
```bash
venv\Scripts\activate.bat
```

**PowerShell**:
```bash
venv\Scripts\Activate.ps1
```

**Git Bash**:
```bash
source venv/Scripts/activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

### 激活成功标志

终端提示符前会显示虚拟环境名称：
```bash
(venv) C:\Users\YourName\project>
```

或

```bash
(venv) user@hostname:~/project$
```

## 停用虚拟环境

在任何操作系统上，激活虚拟环境后都可以使用：
```bash
deactivate
```

停用后，提示符恢复正常，不再显示 `(venv)`。

## 在虚拟环境中管理包

### 安装包

激活虚拟环境后：
```bash
pip install requests
pip install flask==2.3.0        # 安装特定版本
pip install 'django>=4.0,<5.0'  # 安装版本范围
```

### 查看已安装的包

```bash
pip list                # 列表格式
pip freeze              # requirements 格式
```

### 升级包

```bash
pip install --upgrade requests
pip install -U requests          # 简写
```

### 卸载包

```bash
pip uninstall requests
pip uninstall -y requests        # 不询问确认
```

### 批量安装

```bash
pip install -r requirements.txt
```

### 批量卸载

```bash
pip uninstall -r requirements.txt -y
```

## 依赖管理最佳实践

### 生成 requirements.txt

```bash
pip freeze > requirements.txt
```

### requirements.txt 格式

```txt
# 固定版本（推荐用于生产环境）
requests==2.31.0
flask==2.3.3

# 最小版本
requests>=2.30.0

# 版本范围
django>=4.0,<5.0

# 从 Git 仓库安装
git+https://github.com/user/repo.git@v1.0.0

# 本地包
-e ./local_package

# 注释
# 这是一个注释
```

### 分离开发和生产依赖

**requirements/base.txt** (基础依赖):
```txt
django==4.2.0
psycopg2-binary==2.9.6
```

**requirements/dev.txt** (开发依赖):
```txt
-r base.txt
pytest==7.4.0
black==23.7.0
flake8==6.1.0
```

**requirements/prod.txt** (生产依赖):
```txt
-r base.txt
gunicorn==21.2.0
```

安装方式：
```bash
pip install -r requirements/dev.txt
```

## 虚拟环境常用操作

### 复制虚拟环境

不推荐直接复制文件夹，而是：

1. 导出依赖：
   ```bash
   pip freeze > requirements.txt
   ```

2. 在新位置创建虚拟环境：
   ```bash
   python -m venv new_venv
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 删除虚拟环境

直接删除虚拟环境文件夹：

**Windows**:
```bash
rmdir /s venv
```

**macOS/Linux**:
```bash
rm -rf venv
```

### 重建虚拟环境

```bash
# 1. 停用当前环境
deactivate

# 2. 删除旧环境
rm -rf venv

# 3. 创建新环境
python -m venv venv

# 4. 激活新环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 5. 安装依赖
pip install -r requirements.txt
```

### 升级虚拟环境中的 pip

```bash
python -m pip install --upgrade pip
```

## 高级用法

### 指定 Python 版本

```bash
# 使用特定 Python 版本创建虚拟环境
python3.11 -m venv venv
py -3.9 -m venv venv  # Windows
```

### 不包含系统包

默认情况下，虚拟环境不继承系统包。如需包含：
```bash
python -m venv venv --system-site-packages
```

### 不包含 pip

```bash
python -m venv venv --without-pip
```

### 使用 virtualenv（更多功能）

安装 virtualenv：
```bash
pip install virtualenv
```

创建虚拟环境：
```bash
virtualenv venv
virtualenv -p python3.11 venv  # 指定 Python 版本
```

## 常见问题

### 问题 1：激活脚本执行失败

**Windows PowerShell 错误**:
```
无法加载文件，因为在此系统上禁止运行脚本
```

**解决方案**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题 2：找不到 python 命令

**解决方案**:
- Windows: 使用 `py` 命令
- macOS/Linux: 使用 `python3` 命令
- 或将 Python 添加到 PATH

### 问题 3：虚拟环境占用空间大

**原因**: 每个虚拟环境都包含 Python 解释器副本

**解决方案**:
- 定期清理不用的虚拟环境
- 考虑使用 `virtualenv` 的 `--no-download` 选项
- 使用 `poetry` 或 `pipenv` 共享缓存

### 问题 4：requirements.txt 安装失败

**可能原因**:
- 包版本不兼容
- 网络问题
- 缺少系统依赖

**解决方案**:
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 忽略错误继续安装
pip install -r requirements.txt --ignore-installed

# 逐个安装排查问题
pip install package_name
```

### 问题 5：虚拟环境中 pip 版本过旧

**解决方案**:
```bash
python -m pip install --upgrade pip
```

## 项目实践示例

### 示例 1：创建新项目

```bash
# 1. 创建项目目录
mkdir my_project
cd my_project

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装项目依赖
pip install flask requests

# 6. 生成 requirements.txt
pip freeze > requirements.txt

# 7. 创建 .gitignore
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
```

### 示例 2：克隆项目并设置环境

```bash
# 1. 克隆项目
git clone https://github.com/user/project.git
cd project

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行项目
python app.py
```

## 最佳实践总结

1. **每个项目使用独立虚拟环境**
2. **虚拟环境不提交到版本控制**（添加到 .gitignore）
3. **使用 requirements.txt 管理依赖**
4. **固定依赖版本号**（生产环境）
5. **定期更新依赖**（开发环境）
6. **虚拟环境命名统一**（推荐 `venv` 或 `.venv`）
7. **文档化环境设置步骤**（README.md）
8. **使用国内镜像加速下载**

## 下一步

- 学习 [PyCharm 虚拟环境设置](pycharm_setup.md)
- 学习 [VSCode 虚拟环境设置](vscode_setup.md)
- 开始 [Python 基础教程](../tutorials/)

## 参考资源

- Python venv 官方文档：https://docs.python.org/zh-cn/3/library/venv.html
- pip 官方文档：https://pip.pypa.io/
- virtualenv 文档：https://virtualenv.pypa.io/
