# 🚀 部署指南

> 本博客使用 **MkDocs** + **Material for MkDocs** 构建，Vercel 自动构建并托管。

---

## 目录结构

```
quantitative-pharma-blog/
├── docs/                      # 所有内容（MkDocs 源文件）
│   ├── index.md               # 首页
│   ├── quantitative-pharmacology/   # 定量药理建模
│   ├── clinical-pharmacology/        # 临床药理
│   ├── regulations/           # 法规指南
│   ├── conferences/            # 会议培训
│   ├── experts/               # 专家名录
│   ├── resources/             # 学术资源
│   └── stylesheets/extra.css  # 自定义样式
├── mkdocs.yml                 # MkDocs 配置文件
├── vercel.json               # Vercel 构建配置
├── requirements.txt          # Python 依赖
├── .github/workflows/
│   └── deploy.yml             # 自动构建部署
└── tools/
    ├── update_blog.py         # 内容更新脚本
    └── wechat_notify.py       # 微信推送
```

---

## 已完成自动部署 ✅

Vercel 已连接 GitHub，每次推送到 `master` 分支会自动：
1. 安装 `requirements.txt` 中的依赖
2. 运行 `mkdocs build` 生成静态网站
3. 将 `site/` 目录部署到 `xxx.vercel.app`

**你的博客地址**：https://seansilencer-quantitative-pharma-bl.vercel.app/

---

## 绑定自定义域名（可选）

1. Vercel Dashboard → 项目 → Settings → Domains
2. 输入你的域名（如 `blog.example.com`）
3. 按提示在 DNS 中添加记录

---

## 手动编辑内容

所有博客内容都在 `docs/` 目录下，用 Markdown 编写。

### 快速添加新文章

编辑 `docs/articles/index.md`，在表格中添加行：

```markdown
| 文章标题 | 来源 | 日期 | 分类 |
| 新研究进展 | 期刊名 | 2025-05 | PBPK |
```

### 添加新分类

在 `docs/` 下创建子目录和 `index.md` 文件，然后更新 `mkdocs.yml` 的 `nav:` 部分。

---

## 微信推送通知

编辑 `tools/wechat_notify.py`：

```python
# 方式1：企业微信群机器人
WECOM_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
ACTIVE_PROVIDER = "wecom"

# 方式2：Server酱
SERVERCHAN_SCKEY = "YOUR_SCKEY"
ACTIVE_PROVIDER = "serverchan"
```

---

## GitHub Actions 自动构建

`.github/workflows/deploy.yml` 已在每次 push 时自动：
1. 运行 `tools/update_blog.py --generate` 更新内容
2. 执行 `mkdocs build --strict` 生成 HTML
3. 推送构建产物并触发 Vercel 部署

### 手动触发构建

GitHub 仓库页面 → Actions → "Build and Deploy to Vercel" → Run workflow

---

## 本地预览

```bash
# 安装依赖
pip install -r requirements.txt

# 本地开发服务器（热重载）
mkdocs serve

# 构建静态文件（不部署）
mkdocs build --strict
```

---

## 常见问题

**Q: 部署后显示 404？**
A: 检查 `vercel.json` 是否存在且 `buildCommand` 为 `mkdocs build`，`outputDirectory` 为 `site`。

**Q: 样式丢失？**
A: 确认 `docs/stylesheets/extra.css` 存在且 `mkdocs.yml` 中有 `extra_css` 配置。

**Q: 微信推送失败？**
A: 确认 `wechat_notify.py` 中 `ACTIVE_PROVIDER` 与配置匹配，且 Webhook 地址正确。

---

*最后更新: 2025-05-02*