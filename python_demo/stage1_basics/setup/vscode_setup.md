# VSCode 虚拟环境设置教程

## 概述

本教程将指导你在 Visual Studio Code (VSCode) 中创建和管理 Python 虚拟环境。

## 前置要求

- 已安装 Python 3.9+（参考 [Python 安装指南](python_installation.md)）
- 已安装 VSCode

## VSCode 下载与安装

1. 访问官网：https://code.visualstudio.com/
2. 下载适合你操作系统的版本
3. 运行安装程序并完成安装

## 安装 Python 扩展

1. **打开 VSCode**

2. **安装 Python 扩展**
   - 点击左侧活动栏的扩展图标（或按 `Ctrl+Shift+X`）
   - 搜索 "Python"
   - 安装 Microsoft 官方的 Python 扩展
   - 扩展 ID: `ms-python.python`

3. **推荐的额外扩展**
   - **Pylance**: Python 语言服务器（通常随 Python 扩展自动安装）
   - **Python Indent**: 自动缩进辅助
   - **autoDocstring**: 自动生成文档字符串

## 创建虚拟环境

### 方法一：使用命令面板（推荐）

1. **打开命令面板**
   - Windows/Linux: `Ctrl+Shift+P`
   - macOS: `Cmd+Shift+P`

2. **创建虚拟环境**
   - 输入 "Python: Create Environment"
   - 选择环境类型：
     - **Venv**（推荐）
     - Conda

3. **选择 Python 解释器**
   - 选择已安装的 Python 版本
   - VSCode 会在项目根目录创建 `.venv` 文件夹

4. **选择依赖文件**（可选）
   - 如果项目中有 `requirements.txt`，VSCode 会询问是否安装依赖
   - 选择 "Yes" 自动安装

### 方法二：使用集成终端

1. **打开集成终端**
   - View → Terminal
   - 快捷键: `Ctrl+` ` (反引号)

2. **创建虚拟环境**

   **Windows**:
   ```bash
   python -m venv venv
   ```

   **macOS/Linux**:
   ```bash
   python3 -m venv venv
   ```

3. **VSCode 会自动检测**
   - 右下角会弹出提示询问是否使用新环境
   - 点击 "Yes" 选择该环境

## 激活虚拟环境

### 自动激活（推荐）

VSCode 会在打开新终端时自动激活虚拟环境。

### 手动激活

如果需要手动激活：

**Windows (CMD)**:
```bash
venv\Scripts\activate.bat
```

**Windows (PowerShell)**:
```bash
venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
source venv/bin/activate
```

### 激活成功标志

终端提示符前会显示环境名称：
```bash
(venv) C:\Users\YourName\project>
```

## 选择 Python 解释器

### 方法一：通过状态栏

1. 点击 VSCode 右下角的 Python 版本显示
2. 从列表中选择虚拟环境的解释器
3. 通常显示为：`Python 3.x.x ('venv': venv)`

### 方法二：通过命令面板

1. 打开命令面板 (`Ctrl+Shift+P`)
2. 输入 "Python: Select Interpreter"
3. 选择虚拟环境的解释器

### 方法三：通过设置文件

在项目根目录创建 `.vscode/settings.json`：
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python"
}
```

Windows 路径：
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}\\venv\\Scripts\\python.exe"
}
```

## 管理包依赖

### 安装包

在激活虚拟环境的终端中：
```bash
pip install requests
pip install flask fastapi
```

### 从 requirements.txt 安装

```bash
pip install -r requirements.txt
```

### 查看已安装的包

```bash
pip list
pip freeze
```

### 生成 requirements.txt

```bash
pip freeze > requirements.txt
```

### 卸载包

```bash
pip uninstall requests
```

## 配置 VSCode 设置

### 推荐的工作区设置

创建 `.vscode/settings.json`：
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### 设置说明

- `python.defaultInterpreterPath`: 默认解释器路径
- `python.terminal.activateEnvironment`: 自动激活虚拟环境
- `python.linting.enabled`: 启用代码检查
- `python.formatting.provider`: 代码格式化工具
- `editor.formatOnSave`: 保存时自动格式化
- `python.testing.pytestEnabled`: 启用 pytest 测试框架

## 运行 Python 代码

### 方法一：右键运行

1. 打开 Python 文件
2. 右键点击编辑器
3. 选择 "Run Python File in Terminal"

### 方法二：使用快捷键

- 运行当前文件: `Ctrl+Alt+N` (需要安装 Code Runner 扩展)
- 或使用 F5 进行调试运行

### 方法三：使用终端

```bash
python script.py
```

## 调试 Python 代码

### 配置调试

1. **创建调试配置**
   - 点击左侧活动栏的调试图标
   - 点击 "create a launch.json file"
   - 选择 "Python File"

2. **launch.json 示例**
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Current File",
               "type": "python",
               "request": "launch",
               "program": "${file}",
               "console": "integratedTerminal",
               "justMyCode": true
           }
       ]
   }
   ```

### 使用调试器

1. 在代码行号左侧点击设置断点（红点）
2. 按 F5 开始调试
3. 使用调试工具栏控制执行：
   - 继续 (F5)
   - 单步跳过 (F10)
   - 单步进入 (F11)
   - 单步跳出 (Shift+F11)
   - 停止 (Shift+F5)

## PowerShell 执行策略问题

### 问题描述

Windows PowerShell 可能阻止运行激活脚本，显示错误：
```
无法加载文件 venv\Scripts\Activate.ps1，因为在此系统上禁止运行脚本
```

### 解决方案

1. **以管理员身份运行 PowerShell**

2. **查看当前策略**
   ```powershell
   Get-ExecutionPolicy
   ```

3. **修改执行策略**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **确认更改**
   - 输入 `Y` 确认

5. **重新激活虚拟环境**
   ```powershell
   venv\Scripts\Activate.ps1
   ```

### 临时解决方案

使用 CMD 而不是 PowerShell：
```bash
venv\Scripts\activate.bat
```

## 常见问题

### 问题 1：VSCode 无法识别虚拟环境

**解决方案**：
- 重新加载窗口: `Ctrl+Shift+P` → "Developer: Reload Window"
- 手动选择解释器
- 检查 `.venv` 文件夹是否存在

### 问题 2：导入模块显示错误

**解决方案**：
- 确认已选择正确的解释器
- 确认包已安装在虚拟环境中
- 重启 Pylance 语言服务器

### 问题 3：终端没有自动激活虚拟环境

**解决方案**：
- 检查设置: `python.terminal.activateEnvironment` 为 `true`
- 关闭并重新打开终端
- 手动激活虚拟环境

### 问题 4：多个 Python 版本冲突

**解决方案**：
- 明确指定解释器路径
- 使用 `py -3.11` (Windows) 或 `python3.11` (Linux/macOS)
- 在 settings.json 中设置默认解释器

## 最佳实践

1. **项目结构**
   ```
   my_project/
   ├── .venv/              # 虚拟环境（不提交到 Git）
   ├── .vscode/            # VSCode 配置
   │   ├── settings.json
   │   └── launch.json
   ├── src/                # 源代码
   ├── tests/              # 测试代码
   ├── requirements.txt    # 依赖列表
   ├── .gitignore          # Git 忽略文件
   └── README.md           # 项目说明
   ```

2. **Git 配置**
   
   在 `.gitignore` 中添加：
   ```
   # 虚拟环境
   venv/
   .venv/
   env/
   
   # Python 缓存
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   
   # VSCode
   .vscode/
   
   # 其他
   .DS_Store
   *.log
   ```

3. **依赖管理**
   - 使用 `requirements.txt` 管理依赖
   - 固定版本号避免兼容性问题
   - 定期更新依赖

4. **代码质量**
   - 安装 linting 工具: `pip install pylint flake8`
   - 安装格式化工具: `pip install black`
   - 配置自动格式化

## 快捷键参考

| 功能 | Windows/Linux | macOS |
|------|---------------|-------|
| 命令面板 | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| 打开终端 | `Ctrl+` ` | `Ctrl+` ` |
| 运行文件 | `Ctrl+Alt+N` | `Ctrl+Option+N` |
| 调试 | `F5` | `F5` |
| 切换解释器 | 点击状态栏 | 点击状态栏 |

## 推荐扩展

- **Python** (ms-python.python): 必装
- **Pylance** (ms-python.vscode-pylance): 语言服务器
- **Python Indent** (KevinRose.vsc-python-indent): 智能缩进
- **autoDocstring** (njpwerner.autodocstring): 文档字符串生成
- **Python Test Explorer** (LittleFoxTeam.vscode-python-test-adapter): 测试浏览器
- **GitLens** (eamodio.gitlens): Git 增强
- **Code Runner** (formulahendry.code-runner): 快速运行代码

## 下一步

- 学习 [PyCharm 虚拟环境设置](pycharm_setup.md)
- 阅读 [虚拟环境使用指南](virtual_env_guide.md)
- 开始 [Python 基础教程](../tutorials/)

## 参考资源

- VSCode Python 文档：https://code.visualstudio.com/docs/python/python-tutorial
- Python 扩展文档：https://marketplace.visualstudio.com/items?itemName=ms-python.python
- VSCode 快捷键：https://code.visualstudio.com/shortcuts/keyboard-shortcuts-windows.pdf
