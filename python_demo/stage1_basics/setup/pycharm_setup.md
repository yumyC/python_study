# PyCharm 虚拟环境设置教程

## 概述

本教程将指导你在 PyCharm 中创建和管理 Python 虚拟环境。虚拟环境可以为每个项目创建独立的依赖环境，避免包版本冲突。

## 前置要求

- 已安装 Python 3.9+（参考 [Python 安装指南](python_installation.md)）
- 已安装 PyCharm（Community 或 Professional 版本）

## PyCharm 下载与安装

### 下载 PyCharm

1. 访问 JetBrains 官网：https://www.jetbrains.com/pycharm/download/
2. 选择版本：
   - **Community Edition**（免费，适合学习）
   - **Professional Edition**（付费，功能更全）
3. 下载并安装

### 学生免费授权

如果你是学生，可以免费使用 Professional 版本：
1. 访问：https://www.jetbrains.com/community/education/
2. 使用学校邮箱注册
3. 获取免费授权

## 创建新项目并配置虚拟环境

### 方法一：创建项目时配置（推荐）

1. **启动 PyCharm**
   - 打开 PyCharm
   - 点击 "New Project"

2. **配置项目设置**
   - **Location**: 选择项目保存路径
   - **Python Interpreter**: 选择 "New environment using"
   - 选择虚拟环境类型：
     - **Virtualenv**（推荐）
     - Pipenv
     - Poetry
     - Conda

3. **配置 Virtualenv**
   - **Location**: 虚拟环境路径（默认在项目下的 `venv` 文件夹）
   - **Base interpreter**: 选择已安装的 Python 版本
   - 勾选 "Create a main.py welcome script"（可选）
   - 勾选 "Inherit global site-packages"（通常不勾选）

4. **创建项目**
   - 点击 "Create" 按钮
   - PyCharm 会自动创建虚拟环境并激活

### 方法二：为现有项目添加虚拟环境

1. **打开项目**
   - File → Open → 选择项目文件夹

2. **打开设置**
   - Windows/Linux: File → Settings
   - macOS: PyCharm → Preferences
   - 快捷键: `Ctrl+Alt+S` (Windows/Linux) 或 `Cmd+,` (macOS)

3. **配置解释器**
   - 导航到: Project: [项目名] → Python Interpreter
   - 点击右上角的齿轮图标 ⚙️
   - 选择 "Add..."

4. **添加新环境**
   - 选择 "Virtualenv Environment"
   - 选择 "New environment"
   - **Location**: 设置虚拟环境路径（建议使用 `venv` 或 `.venv`）
   - **Base interpreter**: 选择 Python 版本
   - 点击 "OK"

5. **应用设置**
   - 点击 "OK" 关闭设置窗口
   - PyCharm 会创建并激活虚拟环境

## 使用现有虚拟环境

如果你已经通过命令行创建了虚拟环境：

1. **打开解释器设置**
   - Settings → Project → Python Interpreter

2. **添加现有环境**
   - 点击齿轮图标 ⚙️ → Add...
   - 选择 "Virtualenv Environment"
   - 选择 "Existing environment"
   - 点击 "..." 浏览按钮

3. **选择解释器**
   - 导航到虚拟环境目录
   - 选择解释器文件：
     - Windows: `venv\Scripts\python.exe`
     - macOS/Linux: `venv/bin/python`
   - 点击 "OK"

## 管理包依赖

### 使用 PyCharm 界面安装包

1. **打开包管理器**
   - Settings → Project → Python Interpreter
   - 查看已安装的包列表

2. **安装新包**
   - 点击 "+" 按钮
   - 搜索包名（如 `requests`）
   - 选择包并点击 "Install Package"

3. **卸载包**
   - 选择要卸载的包
   - 点击 "-" 按钮

4. **升级包**
   - 选择要升级的包
   - 点击 "↑" 按钮

### 使用 PyCharm 终端

1. **打开终端**
   - View → Tool Windows → Terminal
   - 快捷键: `Alt+F12`
   - 终端会自动激活虚拟环境

2. **安装包**
   ```bash
   pip install requests
   pip install -r requirements.txt
   ```

3. **查看已安装的包**
   ```bash
   pip list
   pip freeze
   ```

## 生成和使用 requirements.txt

### 生成依赖文件

1. **使用终端**
   ```bash
   pip freeze > requirements.txt
   ```

2. **使用 PyCharm**
   - Tools → Sync Python Requirements...
   - PyCharm 会自动检测项目中使用的包

### 安装依赖

```bash
pip install -r requirements.txt
```

## 虚拟环境激活状态识别

### 终端提示符

激活虚拟环境后，终端提示符会显示环境名称：
```bash
(venv) C:\Users\YourName\project>
```

### PyCharm 状态栏

- 右下角显示当前使用的 Python 解释器
- 点击可快速切换解释器

### 代码编辑器

- 如果配置正确，代码中的导入语句不会显示红色波浪线
- 自动补全会显示虚拟环境中安装的包

## 切换虚拟环境

1. **点击状态栏**
   - 点击右下角的 Python 解释器显示
   - 选择 "Add Interpreter..."

2. **或通过设置**
   - Settings → Project → Python Interpreter
   - 从下拉列表中选择不同的解释器

## 常见问题

### 问题 1：PyCharm 无法识别已安装的包

**解决方案**：
- 确认使用了正确的解释器
- 重建索引：File → Invalidate Caches / Restart
- 重新安装包

### 问题 2：终端没有自动激活虚拟环境

**解决方案**：
- Settings → Tools → Terminal
- 勾选 "Activate virtualenv"
- 重启终端

### 问题 3：创建虚拟环境失败

**解决方案**：
- 检查 Python 是否正确安装
- 检查磁盘空间
- 使用管理员权限运行 PyCharm
- 手动创建虚拟环境后再添加到 PyCharm

### 问题 4：多个项目共享虚拟环境

**不推荐**，但如果需要：
- 在项目外创建虚拟环境
- 在每个项目中添加该现有环境
- 注意：可能导致依赖冲突

## 最佳实践

1. **每个项目使用独立的虚拟环境**
   - 避免依赖冲突
   - 便于项目迁移

2. **虚拟环境命名**
   - 使用 `venv` 或 `.venv` 作为文件夹名
   - 便于识别和 `.gitignore` 配置

3. **版本控制**
   - 不要将虚拟环境提交到 Git
   - 在 `.gitignore` 中添加：
     ```
     venv/
     .venv/
     *.pyc
     __pycache__/
     ```

4. **依赖管理**
   - 定期更新 `requirements.txt`
   - 使用版本固定：`requests==2.31.0`
   - 或使用范围：`requests>=2.30.0,<3.0.0`

5. **定期清理**
   - 删除不再使用的虚拟环境
   - 释放磁盘空间

## 快捷键参考

| 功能 | Windows/Linux | macOS |
|------|---------------|-------|
| 打开设置 | `Ctrl+Alt+S` | `Cmd+,` |
| 打开终端 | `Alt+F12` | `Option+F12` |
| 运行文件 | `Shift+F10` | `Ctrl+R` |
| 调试文件 | `Shift+F9` | `Ctrl+D` |

## 下一步

- 学习 [VSCode 虚拟环境设置](vscode_setup.md)
- 阅读 [虚拟环境使用指南](virtual_env_guide.md)
- 开始 [Python 基础教程](../tutorials/)

## 参考资源

- PyCharm 官方文档：https://www.jetbrains.com/help/pycharm/
- 虚拟环境配置：https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html
