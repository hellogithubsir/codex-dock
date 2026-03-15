# CODEx SWITCH
[中文](#中文) | [English](#english)

---

## 中文

简洁、跨平台的 Codex 多账号切换命令行工具。

### ⚙️ 环境依赖
- 本工具基于 Python 编写，运行前需确保已安装 **[Python 3.6+](https://www.python.org/downloads/)**。
- 无第三方依赖库，无需额外执行 `pip install`，下载即用。

### ✨ 核心功能
- **轻量管理**：仅保存 `auth.json`，单账号占用极小。
- **智能识别**：自动从 JWT 解析邮箱并识别当前账号。
- **状态展示**：直观显示订阅类型 (Team/Plus/Pro/Free) 及剩余额度。
- **极简交互**：双语菜单，操作简单直观。
- **跨平台**：提供 Windows/macOS/Linux 一键运行脚本。

### 🚀 快速开始

#### 安装
首先，克隆本仓库到本地：
```bash
git clone https://github.com/SoKeiKei/CODEx-SWITCH.git
cd CODEx-SWITCH
```

#### Windows
双击运行 `run.bat` 或在命令行终端执行：
```bash
python codex.py
```

#### macOS / Linux
```bash
chmod +x run.sh
./run.sh
# 或执行 python3 codex.py
```
> **可选:** 运行 `python scripts/install.py` 可将工具命令自动写入 Shell 别名 (PowerShell profile 或 `.zshrc`)。

### 📖 使用说明

1. **添加账号**: 先在 Codex 登录账号，运行本工具选择 `2` 添加账号并设定别名（如 `gmail`、`work`）。
2. **切换账号**: 运行工具选择 `4`，选择对应账号或 `0`（清空认证）。
3. **生效**: 切换完成后，请**手动重启 Codex** 使更改生效。

### 📁 目录结构

```text
.codex/
└── codex-switch/           # 账号存储目录
    ├── gmail/auth.json     # 对应别名的认证文件
    └── ...

codex-switch/
├── codex.py                # 主程序 CLI 入口
├── run.bat / run.sh        # 一键运行脚本
├── bin/                    # 核心逻辑与业务代码
├── config/accounts.json    # 账号列表配置
└── scripts/install.py      # 别名安装脚本
```

### 💻 界面预览

```text
+--------------------------------------------------+
| CODEx SWITCH                                     |
| account switcher                                 |
+--------------------------------------------------+
Current Account / 当前账号:
 Alias / 别名 |  Email / 邮箱      |  Plan / 订阅 | Usage / 额度
 hotmail      |  ABC**@hotmail.com |  free        | Weekly: 90.0% left (reset 2026-03-15)
==================================================

[1] 查看账号 / List Accounts
[2] 添加账号 / Add Account
[3] 删除账号 / Remove Account
[4] 切换账号 / Switch Account
[q] 退出程序 / Exit
```

### ⚠️ 注意事项
- 额度数据读取自本地 `~/.codex/sessions` 日志，显示可能存在少许延迟。
- 邮箱默认掩码显示（前 2-3 位 + **）以保护隐私。
- 工具**不上传任何数据**，所有数据及凭证仅在本地保存。

### 📄 许可证
本项目采用 [MIT License](LICENSE) 许可证。

---

## English

A lightweight, cross-platform CLI for managing and switching multiple Codex accounts.

### ⚙️ Prerequisites
- This tool is written in Python. You must have **[Python 3.6+](https://www.python.org/downloads/)** installed before running it.
- No third-party dependencies are required (`pip install` is not needed), just download and run.

### ✨ Core Features
- **Lightweight**: Only keeps `auth.json` with minimal disk usage.
- **Auto Parse**: Automatically parses email from JWT to identify the current account.
- **Status Display**: Intuitively shows subscription plan (Team/Plus/Pro/Free) and remaining usage.
- **Interactive UI**: Bilingual menu with simple, intuitive operations.
- **Cross-platform**: Provides one-click run scripts for Windows/macOS/Linux.

### 🚀 Quick Start

#### Installation
First, clone the repository to your local machine:
```bash
git clone https://github.com/SoKeiKei/CODEx-SWITCH.git
cd CODEx-SWITCH
```

#### Windows
Double-click `run.bat` or execute the following in your terminal:
```bash
python codex.py
```

#### macOS / Linux
```bash
chmod +x run.sh
./run.sh
# or run python3 codex.py
```
> **Optional:** Run `python scripts/install.py` to automatically add the tool alias to your shell profile (PowerShell profile or `.zshrc`).

### 📖 Usage

1. **Add Account**: Log into an account in Codex first, run this tool, choose `2` to add an account and set an alias (e.g., `gmail`, `work`).
2. **Switch Account**: Run the tool, choose `4`, and select the corresponding account or `0` (Clear Auth).
3. **Apply**: After switching, please **restart Codex manually** for changes to take effect.

### 📁 Directory Layout

```text
.codex/
└── codex-switch/           # Account storage
    ├── gmail/auth.json     # Auth file for the alias
    └── ...

codex-switch/
├── codex.py                # Main CLI entry point
├── run.bat / run.sh        # One-click runners
├── bin/                    # Core logic and business code
├── config/accounts.json    # Account list configuration
└── scripts/install.py      # Alias install script
```

### 💻 UI Preview

```text
+--------------------------------------------------+
| CODEx SWITCH                                     |
| account switcher                                 |
+--------------------------------------------------+
Current Account / 当前账号:
 Alias / 别名 |  Email / 邮箱      |  Plan / 订阅 | Usage / 额度
 hotmail      |  ABC**@hotmail.com |  free        | Weekly: 90.0% left (reset 2026-03-15)
==================================================

[1] 查看账号 / List Accounts
[2] 添加账号 / Add Account
[3] 删除账号 / Remove Account
[4] 切换账号 / Switch Account
[q] 退出程序 / Exit
```

### ⚠️ Notes
- Usage data is read from local `~/.codex/sessions` logs; display might lag slightly.
- Emails are masked by default (first 2-3 characters + **) to protect privacy.
- The tool **does not upload any data**; all data and credentials belong firmly on local storage.

### 📄 License
This project is licensed under the [MIT License](LICENSE).
