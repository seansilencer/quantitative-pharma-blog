# 定量药理与临床药理前沿追踪 Blog

一个专注于临床药理、定量药理领域的专业技术博客，系统化收集整理国内外专家论文、公众号文章、会议报告等深度内容。

## 📁 目录结构

```
quantitative-pharma-blog/
├── index.md                    # 主页
├── articles/
│   └── index.md                # 文章总目录（树形分类）
├── experts/
│   ├── index.md                # 专家名录总览
│   ├── domestic.md             # 国内专家详细名录
│   └── international.md        # 国际专家详细名录
├── regulations/
│   └── index.md                # 法规与指南
├── conferences/
│   └── index.md                # 会议与培训
├── tools/
│   └── update_blog.py          # 每周更新脚本
└── README.md
```

## 🔄 手动更新

```bash
# 运行更新脚本
python3 tools/update_blog.py

# 查看当前状态
python3 tools/update_blog.py --status
```

## ⏰ 自动更新

设置为每周五自动运行：

```bash
# 添加到 crontab
crontab -e

# 添加以下行（每周五上午9点更新）
0 9 * * 5 cd /home/xiaoyu/quantitative-pharma-blog && python3 tools/update_blog.py >> logs/update.log 2>&1
```

## 📝 更新内容来源

### 论文追踪
- **中文核心期刊**: 药学学报、中国临床药理学杂志、中国新药杂志
- **英文期刊**: CPT, CPT-PSP, J Clin Pharmacol, Clinical Pharmacokinetics, Drug Metab Dispos

### 公众号/博客
- 定量药理公众号
- 药学研发进展
- 临床试验与循证医学
- 医药研发观察

### 会议论文
- 全国临床药理学学术年会
- 中国定量药理学大会
- ASCPT/ACCP/PAGE 等国际会议

## 🔧 维护

- 添加新文章: 编辑 `articles/index.md`，在对应分类下添加条目
- 添加新专家: 编辑 `experts/domestic.md` 或 `experts/international.md`
- 更新法规: 编辑 `regulations/index.md`

---

*本博客内容仅供信息聚合，版权归原作者所有*