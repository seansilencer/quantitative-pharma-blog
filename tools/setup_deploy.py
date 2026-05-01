#!/usr/bin/env python3
"""
Blog 部署设置向导 - 定量药理Blog
运行此脚本完成公网部署和微信推送的初始配置
"""

import os
import sys
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

BLOG_DIR = Path(__file__).parent.parent
WECHAT_CONFIG = BLOG_DIR / "tools" / "wechat_notify.py"
DEPLOY_GUIDE = BLOG_DIR / "DEPLOY.md"

def print_step(msg):
    print(f"\n{'='*50}")
    print(f"📌 {msg}")
    print('='*50)

def run_cmd(cmd, cwd=None, check=True):
    """执行shell命令"""
    result = subprocess.run(cmd, shell=True, cwd=cwd or BLOG_DIR,
                          capture_output=True, text=True)
    if result.returncode != 0 and check:
        print(f"❌ 命令执行失败: {cmd}")
        print(f"   错误: {result.stderr}")
        return None
    return result.stdout.strip()

def check_git_remote():
    """检查git远程仓库"""
    output = run_cmd("git remote -v")
    if output and "origin" in output:
        print("✅ 已配置Git远程仓库")
        return True
    return False

def check_github_cli():
    """检查gh CLI是否可用"""
    result = run_cmd("which gh", check=False)
    return result is not None

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║    定量药理Blog - 部署设置向导                            ║
║    部署到公网 + 配置微信推送                               ║
╚══════════════════════════════════════════════════════════╝
    """)

    # ---- 第1步: 检查当前状态 ----
    print_step("第1步: 检查当前状态")
    has_remote = check_git_remote()
    print(f"  Git远程仓库: {'已配置' if has_remote else '未配置'}")
    print(f"  Blog路径: {BLOG_DIR}")

    # ---- 第2步: GitHub仓库设置 ----
    print_step("第2步: 连接GitHub")

    if has_remote:
        print("✅ 已连接GitHub，跳过此步骤")
    else:
        print("""
  需要创建GitHub仓库来托管Blog代码

  请选择方式:
  A) 使用gh CLI自动创建（需要先登录: gh auth login）
  B) 手动创建（打开浏览器操作）

  """)
        choice = input("  请选择 [A/B]: ").strip().upper()

        if choice == 'A' and check_github_cli():
            print("\n  执行: gh repo create ...")
            repo_name = "quantitative-pharma-blog"
            output = run_cmd(f"gh repo create {repo_name} --public --source=. --push", check=False)
            if output and "Cloning" not in output:
                print(f"  仓库创建输出: {output}")
        else:
            print("""
  请手动操作:
  1. 打开 https://github.com/new
  2. 输入仓库名: quantitative-pharma-blog
  3. 选择 Public
  4. 点击 Create repository（不要勾选任何初始化选项）
  5. 复制仓库URL，然后运行:

     cd {blog_dir}
     git remote add origin 你的仓库URL
     git push -u origin master
            """.format(blog_dir=BLOG_DIR))
            input("\n  按回车键继续...")

    # ---- 第3步: Vercel部署 ----
    print_step("第3步: 部署到Vercel")

    remote_url = run_cmd("git remote get-url origin", check=False)
    if remote_url:
        print(f"  你的GitHub仓库: {remote_url}")
        print("""
  请按以下步骤操作:
  1. 打开 https://vercel.com 并用GitHub账号登录
  2. 点击 "Add New..." → "Project"
  3. 点击 "Import Git Repository"
  4. 选择你的 GitHub 仓库
  5. Framework Preset 选择 "Other"
  6. 点击 "Deploy"
  7. 等待部署完成（约1-2分钟）
  8. 在 Project Settings → Domains 中查看你的Blog地址

  部署完成后，你将获得一个类似以下地址:
  https://xxx.vercel.app
        """)
    else:
        print("⚠️  未检测到GitHub远程仓库，请先完成第2步")

    # ---- 第4步: 配置微信推送 ----
    print_step("第4步: 配置微信推送")

    print("""
  请选择微信推送方式:

  方式1: 企业微信群机器人（推荐，无需注册）
  ----------------------------------------
  1. 打开企业微信电脑客户端或手机APP
  2. 创建一个群（可以只有你一个人）
  3. 点击群右上角「...」→「群机器人」→「添加机器人」
  4. 机器人名称随意，如"Blog通知"
  5. 复制WebHook地址

  方式2: Server酱
  ----------------------------------------
  1. 打开 https://sct.ft07.com 并用微信扫码登录
  2. 复制你的 SCKEY

  方式3: PushPlus
  ----------------------------------------
  1. 打开 https://www.pushplus.plus 并用微信扫码登录
  2. 复制你的 Token
    """)

    provider = input("  请选择推送方式 [1/2/3] (默认1): ").strip() or "1"

    config_updates = {}
    if provider == "1":
        webhook = input("  请粘贴企业微信 WebHook URL: ").strip()
        config_updates['WECOM_WEBHOOK_URL'] = webhook
        config_updates['ACTIVE_PROVIDER'] = '"wecom"'
        print("\n  配置: WECOM_WEBHOOK_URL = " + webhook[:30] + "...")
    elif provider == "2":
        sckey = input("  请粘贴 Server酱 SCKEY: ").strip()
        config_updates['SERVERCHAN_SCKEY'] = sckey
        config_updates['ACTIVE_PROVIDER'] = '"serverchan"'
        print("\n  配置: SERVERCHAN_SCKEY = " + sckey[:20] + "...")
    elif provider == "3":
        token = input("  请粘贴 PushPlus Token: ").strip()
        config_updates['PUSHPLUS_TOKEN'] = token
        config_updates['ACTIVE_PROVIDER'] = '"pushplus"'
        print("\n  配置: PUSHPLUS_TOKEN = " + token[:20] + "...")

    # 更新配置文件
    if config_updates:
        try:
            with open(WECHAT_CONFIG, 'r') as f:
                content = f.read()
            for key, value in config_updates.items():
                import re
                pattern = rf'{key}\s*=\s*["\']?[^"\']*["\']?'
                if re.search(pattern, content):
                    content = re.sub(pattern, f'{key} = {value}', content)
                else:
                    print(f"  ⚠️  未找到 {key} 配置项")
            with open(WECHAT_CONFIG, 'w') as f:
                f.write(content)
            print("  ✅ 配置已保存")
        except Exception as e:
            print(f"  ❌ 保存配置失败: {e}")

    # ---- 第5步: 测试推送 ----
    print_step("第5步: 测试微信推送")

    test = input("  是否发送测试消息? [Y/n]: ").strip().upper()
    if test != 'N':
        print("  正在发送测试消息...")
        result = run_cmd("cd /home/xiaoyu/quantitative-pharma-blog && python3 tools/wechat_notify.py", check=False)
        if result:
            print(result)

    # ---- 完成 ----
    print_step("设置完成!")
    print(f"""
  你的 Blog 地址（Vercel部署后）: https://xxx.vercel.app

  下一步操作:
  1. 确保GitHub仓库代码已推送
  2. 登录 Vercel 确认部署状态
  3. 绑定自定义域名（如有）
  4. 在微信中查看推送测试消息

  手动更新并推送:
    cd {BLOG_DIR}
    git add -A && git commit -m "Update" && git push
    python3 tools/wechat_notify.py

  查看部署指南: {DEPLOY_GUIDE}
    """)

if __name__ == "__main__":
    main()