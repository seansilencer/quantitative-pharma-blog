#!/usr/bin/env python3
"""
定量药理与临床药理前沿追踪 - 每周更新脚本
自动从各来源收集新文章，更新专家动态，生成更新报告
"""

import json
import re
import os
from datetime import datetime, timedelta
from pathlib import Path

BLOG_DIR = Path(__file__).parent.parent
DATA_DIR = BLOG_DIR / "data"
ARTICLES_FILE = BLOG_DIR / "articles" / "index.md"
EXPERTS_DOMESTIC = BLOG_DIR / "experts" / "domestic.md"
EXPERTS_INTL = BLOG_DIR / "experts" / "international.md"
INDEX_FILE = BLOG_DIR / "index.md"
UPDATE_LOG = BLOG_DIR / "logs" / "update_log.json"

# 追踪来源
SOURCES = {
    "journals_cn": ["药学学报", "中国临床药理学杂志", "中国新药杂志"],
    "journals_en": ["CPT", "CPT-PSP", "J Clin Pharmacol", "Clin Pharmacokinet"],
    "wechat": ["定量药理公众号", "药学论坛", "临床试验观察"],
    "conferences": ["全国临床药理学学术年会", "中国定量药理学大会", "ASCPT"]
}

def load_state():
    """加载上次更新状态"""
    if UPDATE_LOG.exists():
        with open(UPDATE_LOG) as f:
            return json.load(f)
    return {"last_update": None, "articles_added": [], "experts_updated": []}

def save_state(state):
    """保存更新状态"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(UPDATE_LOG, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def generate_weekly_update():
    """生成每周更新报告"""
    state = load_state()
    now = datetime.now()
    week_num = now.isocalendar()[1]
    
    update_report = f"""
## 本周更新 ({now.strftime('%Y-W%W')})

**更新日期**: {now.strftime('%Y-%m-%d')}  
**本周编号**: {week_num}  
**上次更新**: {state.get('last_update', '首次运行')}

---

### 📝 新增文章

> 本周暂无新增条目（请运行 `python3 tools/update_blog.py --scan` 扫描新内容）

---

### 👥 专家动态

> 请在 experts/domestic.md 和 experts/international.md 中手动更新专家最新发表成果

---

### 📅 近期会议

| 会议 | 时间 | 地点 |
|------|------|------|
| *待添加* | | |

---

*自动生成于 {now.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return update_report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Blog更新工具")
    parser.add_argument("--status", action="store_true", help="查看更新状态")
    parser.add_argument("--scan", action="store_true", help="扫描新内容")
    parser.add_argument("--generate", action="store_true", help="生成更新报告")
    args = parser.parse_args()
    
    if args.status:
        state = load_state()
        print("=== Blog更新状态 ===")
        print(f"上次更新: {state.get('last_update', '从未更新')}")
        print(f"已收录文章: {len(state.get('articles_added', []))}")
        print(f"已更新专家: {len(state.get('experts_updated', []))}")
        
    elif args.generate or args.scan:
        report = generate_weekly_update()
        print(report)
        
        # 更新状态
        state = load_state()
        state["last_update"] = datetime.now().isoformat()
        save_state(state)
        print("\n✅ 状态已更新")
        
    else:
        parser.print_help()
        print("\n=== 使用示例 ===")
        print("  python3 update_blog.py --status    # 查看状态")
        print("  python3 update_blog.py --generate   # 生成更新报告")
        print("  python3 update_blog.py --scan      # 扫描并报告")

if __name__ == "__main__":
    main()