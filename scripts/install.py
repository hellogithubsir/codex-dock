import os
import sys
from pathlib import Path

def install():
    # 获取当前脚本所在目录
    base_dir = Path(__file__).parent.parent.resolve()
    
    # 配置别名
    if os.name != 'nt':
        shell_profile = Path.home() / ".zshrc"
    else:
        # 确保目录存在
        profile_dir = Path.home() / "Documents" / "PowerShell"
        profile_dir.mkdir(parents=True, exist_ok=True)
        shell_profile = profile_dir / "Microsoft.PowerShell_profile.ps1"
    
    # 构造别名命令
    if os.name != 'nt':
        alias_cmd = f'\nalias codex-switch="python {base_dir}/codex.py"'
    else:
        # PowerShell 别名语法
        alias_cmd = f'\nSet-Alias codex-switch "{sys.executable} {base_dir}/codex.py"'
    
    with open(shell_profile, 'a') as f:
        f.write(alias_cmd)
    
    print(f"Installed! Please restart your terminal or run 'source {shell_profile}' / 安装成功！请重启终端或运行 'source {shell_profile}'")

if __name__ == "__main__":
    install()
