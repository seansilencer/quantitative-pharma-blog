# 🚀 部署指南

## 方案一: Vercel 一键部署（推荐，5分钟完成）

### 步骤

**1. 推送代码到 GitHub**
```bash
# 创建GitHub仓库（需要先安装gh CLI或手动在GitHub网页创建）
gh auth login
gh repo create quantitative-pharma-blog --public --push
# 或手动在 https://github.com/new 创建空仓库后:
git remote add origin https://github.com/你的用户名/quantitative-pharma-blog.git
git push -u origin master
```

**2. 导入 Vercel**
1. 访问 https://vercel.com 并登录（可用GitHub账号）
2. 点击 "Add New..." → "Project"
3. 选择 "Import Git Repository"
4. 选择 `quantitative-pharma-blog` 仓库
5. Framework Preset 选择 "Other"
6. 点击 "Deploy"

**3. 访问你的 Blog**
- 部署完成后 Vercel 会给你一个 `xxx.vercel.app` 的域名
- 在 Project Settings → Domains 可绑定自定义域名

---

## 方案二: GitHub Pages + Cloudflare 加速（完全免费）

### 步骤

**1. 启用 GitHub Pages**
1. 在 GitHub 仓库页面 → Settings → Pages
2. Source 选择 "Deploy from a branch"
3. Branch 选择 `master` `/ (root)`
4. 点击 Save

**2. 设置自定义域名（可选）**
- 在 Custom domain 输入你的域名
- 选择 "Enforce HTTPS"

**3. 用 Cloudflare 加速（可选）**
1. 注册 https://dash.cloudflare.com
2. 添加你的域名
3. 更新域名 NS 服务器为 Cloudflare 提供的地址
4. 在 DNS 设置中，添加一条 CNAME 记录指向你的GitHub Pages地址

---

## 配置微信推送通知

编辑 `tools/wechat_notify.py` 文件，填入你的推送渠道信息：

### 方式1: 企业微信群机器人（推荐，无需注册）

1. 打开企业微信电脑客户端
2. 创建一个群（或用现有群）
3. 群设置 → 群机器人 → 添加机器人
4. 复制 Webhook URL
5. 填入配置：
```python
WECOM_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key"
ACTIVE_PROVIDER = "wecom"
```

### 方式2: Server酱（需要注册）

1. 访问 https://sct.ft07.com 并扫码登录
2. 复制你的 SCKEY
3. 填入配置：
```python
SERVERCHAN_SCKEY = "你的SCKEY"
ACTIVE_PROVIDER = "serverchan"
```

### 方式3: PushPlus（需要注册）

1. 访问 https://www.pushplus.plus 并扫码登录
2. 复制你的 Token
3. 填入配置：
```python
PUSHPLUS_TOKEN = "你的Token"
ACTIVE_PROVIDER = "pushplus"
```

---

## 设置自动更新和推送

### 方式A: 本地 cronjob（需要电脑长期开机）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每周五上午9点更新并推送）
0 9 * * 5 cd /home/xiaoyu/quantitative-pharma-blog && python3 tools/update_blog.py && python3 tools/wechat_notify.py
```

### 方式B: GitHub Actions 自动部署和推送（推荐）

在仓库中创建 `.github/workflows/deploy.yml`:

```yaml
name: Weekly Update and Deploy

on:
  schedule:
    - cron: '0 1 * * 5'  # 每周五凌晨1点（北京时间9点）
  workflow_dispatch:  # 手动触发

jobs:
  update-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Update Blog
        run: |
          python3 tools/update_blog.py --generate
          git config user.email "action@github.com"
          git config user.name "GitHub Action"
          git add -A && git commit -m "Weekly update $(date +'%Y-%m-%d')" || echo "No changes"
      
      - name: Push updates
        run: git push
      
      - name: Send WeChat notification
        env:
          WECOM_WEBHOOK_URL: ${{ secrets.WECOM_WEBHOOK_URL }}
        run: python3 tools/wechat_notify.py
```

然后在 GitHub 仓库 Settings → Secrets 中添加 `WECOM_WEBHOOK_URL`。

---

## 快速检查清单

- [ ] GitHub 仓库已创建并推送代码
- [ ] Vercel 部署成功，域名可访问
- [ ] 微信推送配置完成（已测试收到通知）
- [ ] 自动更新 cronjob / GitHub Actions 已设置

---

## 手动部署命令

```bash
# 1. 更新内容后提交
git add -A && git commit -m "Update: 2025-05-XX" && git push

# 2. 测试微信推送
python3 tools/wechat_notify.py

# 3. 查看更新状态
python3 tools/update_blog.py --status
```