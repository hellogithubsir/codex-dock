from __future__ import annotations

import os
import shutil
import sys
import traceback
from pathlib import Path

from .service import CodexService
from .web import launch_dashboard


APP_FOLDER = "codex-dock-app"
COMMAND_NAME = "codex-dock"


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _codex_home() -> Path:
    custom = str(os.environ.get("CODEX_HOME") or "").strip()
    return Path(custom).expanduser() if custom else Path.home() / ".codex"


def _install_dir() -> Path:
    return _codex_home() / APP_FOLDER


def _ignore(_directory: str, names: list[str]) -> set[str]:
    ignored = {".git", ".gitignore", "__pycache__", ".DS_Store", "launch_error.log"}
    ignored |= {name for name in names if name.endswith(".pyc")}
    return ignored


def _copy_project(source: Path, target: Path) -> None:
    source_config = source / "config" / "accounts.json"
    target_config = target / "config" / "accounts.json"
    previous_config = None
    if target_config.exists():
        previous_config = target_config.read_text(encoding="utf-8")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=_ignore)
    (target / "config").mkdir(parents=True, exist_ok=True)
    if previous_config is not None:
        target_config.write_text(previous_config, encoding="utf-8")
    elif source_config.exists():
        target_config.write_text(source_config.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        target_config.write_text("{}", encoding="utf-8")


def _shell_profile() -> Path:
    if os.name == "nt":
        return Path.home() / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
    shell = os.environ.get("SHELL", "")
    if "bash" in shell:
        return Path.home() / ".bashrc"
    return Path.home() / ".zshrc"


def _entry_line(install_dir: Path) -> str:
    if os.name == "nt":
        run_path = install_dir / "start-codex-dock.bat"
        return f'function {COMMAND_NAME} {{ & "{run_path}" @args }}'
    run_path = install_dir / "start-codex-dock.sh"
    return f"alias {COMMAND_NAME}='\"{run_path}\"'"


def _upsert_profile_entry(content: str, entry: str) -> str:
    lines = content.splitlines()
    kept = [
        line
        for line in lines
        if f"function {COMMAND_NAME} " not in line and not line.strip().startswith(f"alias {COMMAND_NAME}=")
    ]
    kept.append(entry)
    return "\n".join(kept).rstrip() + "\n"


def install() -> None:
    source = _project_root()
    target = _install_dir()
    target.parent.mkdir(parents=True, exist_ok=True)
    _copy_project(source, target)
    if os.name != "nt":
        try:
            os.chmod(target / "start-codex-dock.sh", 0o755)
        except Exception:
            pass

    profile = _shell_profile()
    profile.parent.mkdir(parents=True, exist_ok=True)
    if not profile.exists():
        profile.write_text("", encoding="utf-8")
    entry = _entry_line(target)
    content = profile.read_text(encoding="utf-8", errors="ignore")
    updated = _upsert_profile_entry(content, entry)
    if updated != content:
        profile.write_text(updated, encoding="utf-8")

    print(f"Installed to {target}")
    print(f"Shortcut name: {COMMAND_NAME}")
    print(f"Profile updated: {profile}")


class TerminalApp:
    def __init__(self, service: CodexService | None = None):
        self.service = service or CodexService()

    @staticmethod
    def _ansi(text: str, *codes: str) -> str:
        if not sys.stdout.isatty() or os.getenv("NO_COLOR") is not None or not codes:
            return text
        return "\033[" + ";".join(codes) + "m" + text + "\033[0m"

    @staticmethod
    def _mask(email: str) -> str:
        if not email or "@" not in email:
            return email or "N/A"
        local, domain = email.split("@", 1)
        keep = 1 if len(local) <= 2 else 3
        return f"{local[:keep]}**@{domain}"

    def _is_installed(self) -> bool:
        profile = _shell_profile()
        if not profile.exists():
            return False
        return COMMAND_NAME in profile.read_text(encoding="utf-8", errors="ignore")

    def _render_accounts(self) -> None:
        dashboard = self.service.build_dashboard_snapshot(include_live_current_snapshot=True)
        accounts = dashboard["accounts"]
        if not accounts:
            print("没有已保存账号。")
            return
        width = 108
        print("=" * width)
        print(f"{'别名':<18}{'邮箱':<34}{'套餐':<10}{'额度':<22}{'重置时间':<24}")
        print("-" * width)
        for payload in accounts:
            alias = payload.get("alias", "Unknown")
            email = payload.get("email", "Unknown")
            quota = payload.get("usage_left", "N/A")
            reset = payload.get("reset_at", "N/A")
            marker = "*" if payload.get("is_current") else ""
            print(f"{alias:<18}{email:<34}{payload.get('plan', 'Unknown'):<10}{quota:<22}{reset:<24}{marker}")
        print("=" * width)

    def _render_header(self) -> None:
        print(self._ansi("codex-dock", "36", "1"))
        print(self._ansi("Codex 本地账号切换工具", "2"))
        current = self.service.get_current_account_info()
        quota = self.service.get_usage_stats()
        print("")
        print(f"当前账号: {current['alias']}")
        print(f"当前邮箱: {self._mask(current['email'])}")
        print(f"当前套餐: {str(current['plan']).upper()}")
        print(f"当前额度: {quota}")
        print(self._ansi("提示: CLI 的本地快照可能不如网页精准；完整功能建议按 w 打开网页面板。", "33"))

    def _choose_alias(self, action: str, allow_default: bool = False) -> str | None:
        accounts = self.service.get_accounts()
        if not accounts and not allow_default:
            print("没有已保存账号。")
            return None
        aliases = list(accounts.keys())
        print("")
        if allow_default:
            print("0. 默认 / 干净状态")
        for index, alias in enumerate(aliases, start=1):
            payload = accounts[alias]
            print(f"{index}. {alias} ({payload.get('email', 'Unknown')} · {payload.get('plan', 'Unknown')})")
        print("q. 取消")
        raw = input(f"{action}序号: ").strip().lower()
        if raw == "q":
            return None
        if allow_default and raw == "0":
            return "__default__"
        if raw.isdigit():
            number = int(raw)
            if 1 <= number <= len(aliases):
                return aliases[number - 1]
        print("选择无效。")
        return None

    def _precise_refresh_current(self) -> None:
        current = self.service.get_current_account_info()
        alias = str(current.get("alias") or "").strip()
        accounts = self.service.get_accounts()
        if not alias or alias not in accounts:
            print("当前账号还没有保存到本工具，无法通过 CLI 精准刷新。请先按 2 保存，或按 w 打开网页面板。")
            return
        try:
            self.service.refresh_precise_usage_for_alias(alias)
            print(f"已精准刷新当前账号: {alias}")
        except Exception as exc:
            print(f"精准刷新失败: {exc}")

    def run(self) -> None:
        if not self._is_installed():
            answer = input("是否现在安装 shell 快捷命令？(y/n): ").strip().lower()
            if answer == "y":
                install()
                return

        while True:
            print("")
            self._render_header()
            print("")
            self._render_accounts()
            print("")
            print("1. 刷新本地额度快照（快速，可能不准）")
            print("2. 保存当前登录")
            print("3. 删除已保存账号")
            print("4. 切换账号 / 默认环境")
            print("5. 重置为干净会话")
            print("p. 精准刷新当前账号")
            print("w. 打开完整功能网页面板（推荐）")
            print("q. 退出")
            choice = input("请选择操作: ").strip().lower()

            if choice == "1":
                self.service.refresh_current_account_usage_snapshot(wait_seconds=1.0, retries=1)
                print("已刷新本地额度快照。如需更准确数据，请按 p 精准刷新，或按 w 打开网页面板。")
            elif choice == "2":
                alias = input("请输入当前登录账号的别名: ").strip()
                if alias:
                    self.service.add_account(alias)
            elif choice == "3":
                alias = self._choose_alias("删除")
                if alias:
                    self.service.remove_account(alias)
            elif choice == "4":
                alias = self._choose_alias("切换", allow_default=True)
                if alias == "__default__":
                    self.service.switch_to_default()
                    print("已切换到默认 / 干净状态。")
                elif alias:
                    self.service.switch_account(alias)
            elif choice == "5":
                self.service.switch_to_default()
                print("已恢复为干净会话。")
            elif choice == "p":
                self._precise_refresh_current()
            elif choice == "w":
                print("正在启动完整功能网页面板。关闭网页服务后会回到命令行。")
                launch_dashboard()
            elif choice == "q":
                print("已退出。")
                return
            else:
                print("未知操作。")


def main() -> int:
    if any(arg in {"--cli", "-c"} for arg in sys.argv[1:]):
        TerminalApp().run()
        return 0

    try:
        launch_dashboard()
        return 0
    except Exception:
        has_console = bool(sys.stdout and sys.stdout.isatty())
        if has_console:
            print("网页面板启动失败，已回退到命令行模式。")
            TerminalApp().run()
            return 0

        log_path = Path(__file__).resolve().parent.parent / "launch_error.log"
        log_path.write_text("Dashboard launch failed.\n\n" + traceback.format_exc(), encoding="utf-8")
        raise
