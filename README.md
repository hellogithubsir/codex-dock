# codex-dock

[中文](#中文) | [English](#english)

* * *

## 中文

简洁、跨平台的 Codex / ChatGPT 多账号切换工具，支持网页面板、额度检查、精准刷新、账号排序，以及回到默认干净环境。

当前项目参考 [SoKeiKei/CODEx-SWITCH](https://github.com/SoKeiKei/CODEx-SWITCH) 的构思，并在此基础上新增了这些功能：

1. 网页管理面板
2. 更完整的账号总览与操作说明
3. 当前账号未保存提醒
4. 邮箱隐藏切换
5. 额度检查与精准刷新
6. 账户 token 自动刷新
7. 按当前使用状态、会员、额度、重置时间的排序规则
8. 启动时检查账户并自动刷新到期额度
9. 带开关的按账号排队 token 保活刷新（默认关闭，24 小时后再加较大随机偏移）
10. 更直观的启动/安装脚本命名

### ⚙️ 环境依赖

- 本工具基于 Python 编写，运行前需确保已安装 [Python 3.10+](https://www.python.org/downloads/)。
- 无第三方依赖库，无需额外执行 `pip install`，下载即用。
- 如果设置了环境变量 `CODEX_HOME`，本项目会优先使用该目录；否则默认使用 `~/.codex`。

### ✨ 核心功能

- 轻量管理：保存当前账号并归档认证文件，便于多账号切换。
- 智能识别：自动从 JWT 解析邮箱、套餐和账号信息。
- 网页总览：提供 Web 面板查看账号、额度、会员状态和重置时间。
- 精准刷新：支持调用官方 usage 接口获取更准确的额度数据。
- 自动刷新：支持账户 token 自动刷新，并在启动时检查到期额度后自动重试刷新。
- Token 保活队列：支持手动开关；开启后后台按账号串行刷新登录凭据，为每个账号生成更保守的随机计划时间，降低多个账号同时刷新导致 refresh token 冲突的概率。
- 智能排序：按当前使用状态、会员、额度、重置时间对账号排序。
- 跨平台：提供 Windows / macOS / Linux 启动脚本和安装脚本。

### 🚀 快速开始

#### 方式 1：直接本地运行

- Windows (PowerShell / 双击)：

```powershell
start-codex-dock.bat
```

- macOS / Linux (Terminal)：

```bash
./start-codex-dock.sh
```

- Python：

```bash
python codex.py
```

> 默认会打开 Web 面板；如果要进入命令行菜单，可以追加 `--cli`。

#### 方式 2：安装全局命令

安装后会把当前项目复制到本地目录，并写入全局快捷命令 `codex-dock`。

- Windows:

```powershell
install-codex-dock-command.ps1
```

- macOS / Linux:

```bash
./install-codex-dock-command.sh
```

> 默认安装到 `~/.codex/codex-dock-app`；如果设置了 `CODEX_HOME`，则安装到 `$CODEX_HOME/codex-dock-app`。

#### 方式 3：命令行模式

```bash
python codex.py --cli
```

或：

```bash
python -m scripts --cli
```

### 📖 使用说明

#### 💡 如何登录并保存新账号？（重要指引）

1. 请不要在 Codex 软件内点击“退出登录 (Logout)”。
2. 先运行本工具，通过网页按钮“添加当前账号”或 CLI 菜单 `2`“保存当前登录”，把当前已登录账号保存下来，并起一个别名，例如 `work`。
3. 如果要登录一个全新账号，可以切换到“默认 / 干净状态”。
4. 重新打开 Codex 软件并登录新账号。
5. 再次运行本工具，把新账号保存进来，例如命名为 `gmail`。
6. 之后就可以在这些已收录账号之间自由切换。

#### 🧭 日常操作说明

1. 平时直接启动 Web 面板，查看当前账号和全部已保存账号状态。
2. 如果只是切换账号，不需要手动做 token 刷新；后台会按队列自动维护已保存账号的登录凭据。
   只有你手动开启顶部的“保活已开启 / 保活已关闭”开关后，这个后台保活队列才会运行。
3. 如果想看最新额度，优先点“刷新额度”；只有在需要和官网数据严格对齐时，再点“精准刷新”。
4. 如果某个账号提示“自动刷新登录凭据失败”或提示 refresh token 已失效，切换到该账号重新登录一次，再用“添加当前账号”重新保存覆盖即可。
5. 不要同时开多个实例频繁切换或精准刷新同一个账号，否则仍可能触发 refresh token 被轮换或已被使用。

#### 🌐 网页面板可以做什么？

- 查看当前账号、套餐、额度和重置时间
- 查看全部已保存账号的卡片总览
- 刷新额度或精准刷新
- 添加当前账号
- 删除已保存账号
- 切换到任意已保存账号
- 切换回默认干净环境
- 手动开启或关闭后台 token 保活
- 隐藏或显示邮箱
- 在当前账号未保存时给出提醒
- 后台自动维护每个已保存账号的 token 保活节奏

#### ⌨️ CLI 菜单可以做什么？

1. 刷新本地额度快照（快速，可能不准）
2. 保存当前登录
3. 删除已保存账号
4. 切换账号 / 默认环境
5. 重置为干净会话
p. 精准刷新当前账号
w. 打开完整功能网页面板（推荐）
q. 退出

### 📁 目录结构

```text
.codex/
└── codex-dock/                    # 已保存账号的认证归档目录
    ├── work/auth.json
    └── ...

codex-dock/
├── codex.py
├── start-codex-dock.bat
├── start-codex-dock.sh
├── install-codex-dock-command.ps1
├── install-codex-dock-command.sh
├── config/
│   └── accounts.json
└── scripts/
    ├── main.py
    ├── service.py
    ├── web.py
    └── mcp_stdio_proxy.py
```

- `start-codex-dock.bat` / `start-codex-dock.sh`：直接启动工具，默认打开 Web 面板。
- `install-codex-dock-command.ps1` / `install-codex-dock-command.sh`：安装全局 `codex-dock` 命令。
- `config/accounts.json`：本项目自己的账号映射和额度记录。
- `scripts/service.py`：账号保存、切换、刷新、排序核心逻辑。
- `scripts/web.py`：网页面板。
- `scripts/mcp_stdio_proxy.py`：MCP stdio 兼容代理。

### 🔄 Token 保活说明

- 每个已保存账号都会在本地归档 `auth.json` 中记录 `last_refresh` 和 `next_token_refresh_at`。
- 保活默认关闭，只有手动开启后后台队列才会运行。
- 后台线程会按账号排队检查，到达计划时间后串行刷新 token，而不是并发请求。
- 默认下一次刷新时间为上次成功刷新后的 `24 小时 + 2~12 小时随机偏移`。
- 对于首次纳入保活的旧账号，系统会先安排 `20~90 分钟` 的随机首轮延迟，而不是启动后立刻全部补刷。
- 每轮最多只处理 1 个到期账号；如果失败，会退避约 12 小时后再尝试。
- 刷新成功后会立即写回新的 `access_token`、`id_token`、`refresh_token` 和下一次计划时间。
- 如果服务端返回 `401 Unauthorized` 或提示 refresh token 已被使用，工具会记录中文错误提示；这类账号需要重新登录一次后再保存。
- 保活刷新只负责更新登录凭据；额度数据仍建议通过“刷新额度”或“精准刷新”查看。

### ⚠️ 注意事项

- 当前登录信息默认来自 `~/.codex/auth.json`；如果设置了 `CODEX_HOME`，则使用 `$CODEX_HOME/auth.json`。
- 已保存账号默认备份到 `~/.codex/codex-dock/<别名>/auth.json`；如果设置了 `CODEX_HOME`，则使用 `$CODEX_HOME/codex-dock/<别名>/auth.json`。
- 本地额度快照默认来自 `~/.codex/sessions`；如果设置了 `CODEX_HOME`，则使用 `$CODEX_HOME/sessions`。
- CLI 的本地快照可能不如网页精准刷新准确，建议日常使用 Web 面板。
- Token 保活机制会尽量维持已保存账号可刷新，但如果 refresh token 已被其他实例使用、被服务端轮换或撤销，仍然需要重新登录。
- 邮箱默认可按掩码显示，以保护隐私。
- 工具不会上传本地认证文件，数据默认只保留在本机。

### 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

* * *

## English

A lightweight, cross-platform multi-account switcher for Codex / ChatGPT, with a Web dashboard, quota checks, precise refresh, account sorting, and clean-session reset.

This project is inspired by [SoKeiKei/CODEx-SWITCH](https://github.com/SoKeiKei/CODEx-SWITCH), and extends that idea with these additions:

1. A Web dashboard
2. Richer account overview and usage guidance
3. Reminders when the current account has not been saved yet
4. Email masking controls
5. Quota checking and precise refresh
6. Automatic account token refresh
7. Account sorting by current state, membership, quota, and reset time
8. Startup checks that auto-refresh accounts whose quota window has expired
9. Toggleable queued token keepalive refresh with a conservative post-24-hour random offset
10. Clearer launcher and installer script naming

### ⚙️ Prerequisites

- This tool is written in Python. You need [Python 3.10+](https://www.python.org/downloads/) installed.
- No third-party dependencies are required. No `pip install` step is needed.
- If `CODEX_HOME` is set, the project uses that directory first; otherwise it defaults to `~/.codex`.

### ✨ Core Features

- Lightweight management: save current accounts and archive auth files for switching.
- Smart parsing: extract email, plan, and account identity from JWT tokens.
- Web dashboard: inspect accounts, quota, member status, and reset times visually.
- Precise refresh: call the official usage endpoint for more accurate quota data.
- Auto refresh: refresh account tokens automatically and retry quota refresh on startup when needed.
- Token keepalive queue: can be enabled manually; when enabled, it refreshes saved account credentials serially in the background and assigns each account a more conservative randomized schedule to reduce refresh-token collisions.
- Smart sorting: sort accounts by current state, membership, quota, and reset time.
- Cross-platform: provide launcher and installer scripts for Windows / macOS / Linux.

### 🚀 Quick Start

#### Method 1: Run locally

- Windows:

```powershell
start-codex-dock.bat
```

- macOS / Linux:

```bash
./start-codex-dock.sh
```

- Python:

```bash
python codex.py
```

> The default behavior is to open the Web dashboard. Add `--cli` to open the terminal menu instead.

#### Method 2: Install a global command

After installation, the project is copied into a local app directory and a global `codex-dock` shortcut is added to your shell profile.

- Windows:

```powershell
install-codex-dock-command.ps1
```

- macOS / Linux:

```bash
./install-codex-dock-command.sh
```

> The default install path is `~/.codex/codex-dock-app`; if `CODEX_HOME` is set, the install path becomes `$CODEX_HOME/codex-dock-app`.

#### Method 3: CLI mode

```bash
python codex.py --cli
```

or:

```bash
python -m scripts --cli
```

### 🔄 Token Keepalive

- Each saved account stores `last_refresh` and `next_token_refresh_at` in its archived `auth.json`.
- Keepalive is off by default. The background queue runs only after you enable it manually.
- A background worker checks accounts in queue order and refreshes tokens serially when their scheduled time arrives.
- The default next refresh is `24 hours + 2-12 hours of random jitter` after the last successful refresh.
- For older accounts that are entering keepalive for the first time, the tool schedules an initial randomized delay of `20-90 minutes` instead of refreshing everything immediately at startup.
- Each cycle processes at most one due account. If a refresh fails, the tool backs off for about 12 hours before trying that account again.
- After a successful refresh, the tool immediately persists the new `access_token`, `id_token`, `refresh_token`, and the next scheduled refresh time.
- If the service returns `401 Unauthorized` or reports that the refresh token has already been used, the tool records a friendly error message; that account must be signed in again and re-saved.
- Keepalive refresh only maintains credentials. Use quota refresh or precise refresh when you need the latest usage data.

### 📖 Usage

#### 💡 How do I save a new account? (Important Guide)

1. Do not click “Logout” inside the Codex app.
2. Run this tool and save the current account through the Web button “添加当前账号” or CLI option `2`.
3. If you want to sign in with a new account, switch back to the default clean state first.
4. Reopen Codex and sign in with the new account.
5. Save that account as well, for example with an alias like `gmail`.
6. After that, you can switch freely among saved accounts.

#### 🧭 Daily Workflow

1. Start with the Web dashboard for normal daily use and to inspect all saved accounts.
2. If you only need to switch accounts, you do not need to refresh tokens manually; the background queue maintains saved account credentials automatically.
   That queue runs only after you manually enable the top `Keepalive On / Keepalive Off` toggle.
3. If you want the latest usage data, use quota refresh first. Use precise refresh only when you need the dashboard to match the official usage endpoint more closely.
4. If an account shows an automatic credential-refresh failure or indicates that the refresh token is no longer valid, switch to that account, sign in again, and save it again through “添加当前账号”.
5. Avoid running multiple instances that frequently switch or precise-refresh the same account, because refresh-token rotation can still invalidate one of them.

#### 🌐 What can the Web dashboard do?

- Show the current account, plan, quota, and reset time
- Show cards for all saved accounts
- Refresh quota or perform a precise refresh
- Save the current account
- Remove saved accounts
- Switch to any saved account
- Reset back to the default clean environment
- Manually enable or disable background token keepalive
- Hide or reveal email addresses
- Show reminders when the current account has not been saved yet

#### ⌨️ What can the CLI menu do?

1. Refresh local quota snapshot (fast, may be less accurate)
2. Save current login
3. Remove saved login
4. Switch account / default environment
5. Reset to clean session
p. Precise-refresh the current account
w. Open the full Web dashboard (recommended)
q. Quit

### 📁 Directory Layout

```text
.codex/
└── codex-dock/                    # Archived auth files for saved accounts
    ├── work/auth.json
    └── ...

codex-dock/
├── codex.py
├── start-codex-dock.bat
├── start-codex-dock.sh
├── install-codex-dock-command.ps1
├── install-codex-dock-command.sh
├── config/
│   └── accounts.json
└── scripts/
    ├── main.py
    ├── service.py
    ├── web.py
    └── mcp_stdio_proxy.py
```

- `start-codex-dock.bat` / `start-codex-dock.sh`: launch the tool directly and open the Web dashboard by default.
- `install-codex-dock-command.ps1` / `install-codex-dock-command.sh`: install the global `codex-dock` command.
- `config/accounts.json`: local account mapping and quota records used by this project.
- `scripts/service.py`: core logic for save/switch/refresh/sort flows.
- `scripts/web.py`: Web dashboard.
- `scripts/mcp_stdio_proxy.py`: MCP stdio compatibility proxy.

### ⚠️ Notes

- The current login state comes from `~/.codex/auth.json` by default, or `$CODEX_HOME/auth.json` when `CODEX_HOME` is set.
- Saved accounts are archived under `~/.codex/codex-dock/<alias>/auth.json` by default, or `$CODEX_HOME/codex-dock/<alias>/auth.json` when `CODEX_HOME` is set.
- Local quota snapshots are read from `~/.codex/sessions` by default, or `$CODEX_HOME/sessions` when `CODEX_HOME` is set.
- CLI local snapshots may be less accurate than the Web dashboard precise refresh flow.
- Keepalive reduces credential-expiry interruptions, but it still cannot recover an account whose refresh token has already been rotated, invalidated, or used by another instance.
- Emails can be masked by default to protect privacy.
- The tool does not upload local auth files; data stays on the local machine by default.

### 📄 License

This project is licensed under the [MIT License](LICENSE).
