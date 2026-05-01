#!/usr/bin/env python3
"""
微信推送模块 - 支持 Server酱/PushPlus/企业微信机器人
每周更新后自动推送通知
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

# ==================== 配置区 ====================
# 请填入你的推送渠道信息

# 方案1: Server酱 (sct.ft07.com) - 微信推送，扫码注册获取SCKEY
# 注册地址: https://sct.ft07.com
SERVERCHAN_SCKEY = ""   # 例: "SCT1234567890abcdef"

# 方案2: PushPlus (pushplus.plus) - 微信推送，扫码获取Token
# 注册地址: https://www.pushplus.plus
PUSHPLUS_TOKEN = ""      # 例: "1234567890abcdef"

# 方案3: 企业微信群机器人 (推荐，无需注册)
# 在企业微信群设置中添加机器人，复制Webhook URL
WECOM_WEBHOOK_URL = ""   # 例: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx"

# 默认推送方案: 留空则不推送
ACTIVE_PROVIDER = "wecom"  # 可选: "serverchan", "pushplus", "wecom"

# ==================== 推送函数 ====================

def send_serverchan(title: str, content: str) -> bool:
    """Server酱推送"""
    if not SERVERCHAN_SCKEY:
        print("⚠️  Server酱 SCKEY 未配置")
        return False
    url = f"https://sct.ft07.com/send?title={urllib.parse.quote(title)}&desp={urllib.parse.quote(content)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if result.get("code") == 0:
                print("✅ Server酱 推送成功")
                return True
            else:
                print(f"❌ Server酱 推送失败: {result}")
                return False
    except Exception as e:
        print(f"❌ Server酱 推送异常: {e}")
        return False

def send_pushplus(title: str, content: str) -> bool:
    """PushPlus推送"""
    if not PUSHPLUS_TOKEN:
        print("⚠️  PushPlus Token 未配置")
        return False
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "markdown"
    }
    try:
        req = urllib.request.Request(url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if result.get("code") == 200:
                print("✅ PushPlus 推送成功")
                return True
            else:
                print(f"❌ PushPlus 推送失败: {result}")
                return False
    except Exception as e:
        print(f"❌ PushPlus 推送异常: {e}")
        return False

def send_wecom(title: str, content: str) -> bool:
    """企业微信群机器人推送"""
    if not WECOM_WEBHOOK_URL:
        print("⚠️  企业微信 Webhook URL 未配置")
        return False
    # 合并标题和内容
    full_content = f"**{title}**\n\n{content}\n\n---\n更新于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": full_content
        }
    }
    try:
        req = urllib.request.Request(WECOM_WEBHOOK_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if result.get("errcode") == 0:
                print("✅ 企业微信 推送成功")
                return True
            else:
                print(f"❌ 企业微信 推送失败: {result}")
                return False
    except Exception as e:
        print(f"❌ 企业微信 推送异常: {e}")
        return False

def send_notification(title: str, content: str) -> bool:
    """统一推送入口"""
    if ACTIVE_PROVIDER == "serverchan":
        return send_serverchan(title, content)
    elif ACTIVE_PROVIDER == "pushplus":
        return send_pushplus(title, content)
    elif ACTIVE_PROVIDER == "wecom":
        return send_wecom(title, content)
    else:
        print("⚠️  未配置推送渠道，跳过微信通知")
        return False

def send_weekly_update(article_count: int = 0, expert_count: int = 0) -> bool:
    """发送每周更新通知"""
    title = "📚 定量药理Blog - 本周更新"
    content = f"""## 本周更新摘要

- 📝 新增文章: {article_count} 篇
- 👥 更新专家: {expert_count} 位

### 主要内容
- 定量药理建模 (PBPK/PopPK/PKPD)
- 临床药理研究进展
- 法规与指导原则

### 查看方式
访问 Blog 首页查看完整内容"""
    return send_notification(title, content)

if __name__ == "__main__":
    # 测试推送
    print("=== 微信推送配置测试 ===")
    send_notification("📚 定量药理Blog推送测试", "如果你看到这条消息，说明推送配置成功！")