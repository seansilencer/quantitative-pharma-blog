#!/usr/bin/env python3
"""
静态博客生成器 - build.py
docs/ 下的 Markdown → site/ 下的 HTML，零依赖
"""
import re, os, shutil
from pathlib import Path
from datetime import datetime

SRC = Path("docs")
DST = Path("site")
SITE_TITLE = "定量药理与临床药理前沿追踪"
NOW = datetime.now().strftime('%Y-%m-%d')

# ── 导航配置 ──────────────────────────────────────────────
NAV_TREE = [
    {"id": "home",     "label": "🏠 首页",              "file": "index.html"},
    {"id": "qpm",      "label": "📐 定量药理建模",        "file": "quantitative-pharmacology/index.html", "children": [
        {"id": "qpm-pbpk","label":"PBPK 建模",            "file":"quantitative-pharmacology/pbpk.html"},
        {"id": "qpm-poppk","label":"PopPK 建模",          "file":"quantitative-pharmacology/poppk.html"},
        {"id": "qpm-pkbd","label":"PK/PD 关联",            "file":"quantitative-pharmacology/pkbd.html"},
    ]},
    {"id": "cp",       "label": "💊 临床药理",            "file": "clinical-pharmacology/index.html", "children": [
        {"id": "cp-innov","label":"创新药临床药理",        "file":"clinical-pharmacology/innovative-drugs.html"},
        {"id": "cp-generic","label":"仿制药 / BE",        "file":"clinical-pharmacology/generic-drugs.html"},
        {"id": "cp-special","label":"特殊人群药理",       "file":"clinical-pharmacology/special-populations.html"},
    ]},
    {"id": "articles", "label": "📚 文章总目录",           "file": "articles/index.html"},
    {"id": "regulations","label":"📋 法规与指南",        "file":"regulations/index.html"},
    {"id": "conferences","label":"🎓 会议与培训",        "file":"conferences/index.html"},
    {"id": "experts",  "label": "👥 专家名录",            "file": "experts/index.html", "children": [
        {"id": "exp-dom","label":"国内专家",              "file":"experts/domestic.html"},
        {"id": "exp-intl","label":"国际专家",             "file":"experts/international.html"},
    ]},
    {"id": "resources","label": "🔧 学术资源",            "file": "resources/index.html", "children": [
        {"id": "res-journals","label":"期刊推荐",         "file":"resources/journals.html"},
        {"id": "res-tools","label":"工具软件",            "file":"resources/tools.html"},
    ]},
]

# ── CSS + JS ──────────────────────────────────────────────
CSS = """
:root{--bg:#f8f9fc;--sb:#1e2535;--sb-fg:#c8d0e0;--sb-active:#5c6bc0;
      --accent:#5c6bc0;--acc-bg:#e8eaf6;--text:#1a1e2e;--muted:#6b7280;
      --card:#fff;--border:#e2e8f0}
*{box-sizing:border-box;margin:0;padding:0}
body{display:flex;min-height:100vh;background:var(--bg);color:var(--text);
     font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.6}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

/* ── 侧边栏 ── */
#sidebar{width:260px;min-width:260px;background:var(--sb);color:var(--sb-fg);
         position:fixed;top:0;left:0;height:100vh;overflow-y:auto;
         display:flex;flex-direction:column}
#sb-header{padding:1.2rem 1rem;border-bottom:1px solid rgba(255,255,255,.08);color:#fff;font-weight:700;font-size:.95rem;line-height:1.4}
#sb-header span{font-size:.75rem;opacity:.55;font-weight:400;display:block;margin-top:.2rem}
.nav-item{padding:0}
.nav-link{display:flex;align-items:center;padding:.55rem 1rem;font-size:.9rem;
          color:var(--sb-fg);cursor:pointer;transition:background .15s,color .15s;
          text-decoration:none;user-select:none}
.nav-link:hover{background:rgba(255,255,255,.07);color:#fff}
.nav-link.active{background:var(--sb-active);color:#fff;font-weight:500}
.nav-link .arrow{margin-left:auto;font-size:.7rem;transition:transform .2s}
.nav-link.open .arrow{transform:rotate(90deg)}
.nav-children{display:none;padding-left:.8rem}
.nav-children .nav-link{padding:.4rem 1rem .4rem 1.8rem;font-size:.85rem}

/* ── 主区 ── */
#main{margin-left:260px;flex:1;display:flex;flex-direction:column;min-width:0}
#topbar{background:#fff;border-bottom:1px solid var(--border);padding:.85rem 2rem;
        display:flex;align-items:center;gap:1rem;position:sticky;top:0;z-index:10}
#breadcrumb{font-size:.85rem;color:var(--muted)}
#breadcrumb a{color:var(--accent)}
#topbar-right{margin-left:auto;font-size:.82rem;color:var(--muted)}
#content{padding:2rem 2.5rem;flex:1;max-width:1100px}
footer{background:#fff;border-top:1px solid var(--border);padding:.8rem 2rem;
       text-align:center;font-size:.8rem;color:var(--muted)}
footer a{color:var(--accent)}

/* ── 卡片网格 ── */
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem;margin-top:1rem}
.article-card{background:var(--card);border:1px solid var(--border);border-radius:10px;
              padding:1.1rem 1.2rem;transition:box-shadow .2s,transform .2s;
              display:flex;flex-direction:column;gap:.35rem}
.article-card:hover{box-shadow:0 6px 20px rgba(92,107,192,.18);transform:translateY(-2px)}
.card-meta{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap}
.card-status{padding:.1rem .45rem;border-radius:99px;font-size:.72rem;font-weight:600}
.s-new{background:#e8f5e9;color:#2e7d32}
.s-old{background:#e3f2fd;color:#1565c0}
.s-classic{background:#f3e5f5;color:#6a1b9a}
.card-source{font-size:.78rem;color:var(--muted)}
.card-title{font-size:.98rem;font-weight:600;line-height:1.4}
.card-title a{color:var(--text)}
.article-card:hover .card-title a{color:var(--accent)}
.card-summary{font-size:.83rem;color:#555;flex:1;line-height:1.55}
.card-footer{margin-top:.35rem;display:flex;justify-content:space-between;align-items:center}
.card-date{font-size:.78rem;color:var(--muted)}
.card-link{font-size:.82rem;color:var(--accent);font-weight:500;white-space:nowrap}
.card-link:hover{text-decoration:underline}

/* ── 页面头部 ── */
.sec-header{margin-bottom:1.5rem;padding-bottom:.8rem;border-bottom:2px solid var(--accent)}
.sec-header h1{font-size:1.55rem}
.sec-header p{color:var(--muted);margin-top:.3rem;font-size:.88rem}
.sec-header .updated{font-size:.8rem;margin-top:.4rem}

/* ── 正文排版 ── */
.md-body h2{font-size:1.2rem;margin:1.6rem 0 .6rem;padding-bottom:.3rem;border-bottom:1px solid var(--border)}
.md-body h3{font-size:1.02rem;margin:1.2rem 0 .4rem}
.md-body p{margin:.5rem 0;line-height:1.75}
.md-body ul,.md-body ol{margin:.5rem 0;padding-left:1.4rem}
.md-body li{margin:.25rem 0}
.md-body blockquote{margin:.8rem 0;padding:.6rem 1rem;border-left:3px solid var(--accent);background:var(--acc-bg);border-radius:0 6px 6px 0}
.md-body table{width:100%;border-collapse:collapse;margin:.8rem 0;font-size:.88rem}
.md-body th,.md-body td{padding:.5rem .75rem;border:1px solid var(--border);text-align:left}
.md-body th{background:var(--accent);color:#fff;font-weight:500}
.md-body tr:nth-child(even){background:rgba(0,0,0,.03)}
.md-body code{background:#f0f0f0;padding:.1rem .35rem;border-radius:3px;font-size:.85em}
.md-body pre{background:#f4f4f4;padding:.9rem;border-radius:6px;overflow-x:auto;margin:.8rem 0}
.md-body pre code{background:none;padding:0}
.md-body hr{border:none;border-top:1px solid var(--border);margin:1.5rem 0}
.md-body strong{font-weight:600}

/* ── 响应式 ── */
@media(max-width:768px){
  #sidebar{transform:translateX(-100%);z-index:100}
  #sidebar.open{transform:translateX(0)}
  #main{margin-left:0}
  #sb-toggle{display:flex;align-items:center;justify-content:center;width:36px;height:36px;
             background:#f0f0f0;border-radius:6px;border:none;cursor:pointer;font-size:1.2rem}
  #content{padding:1.2rem}
  .card-grid{grid-template-columns:1fr}
}
"""

JS = """
function toggleNav(id){var el=document.getElementById('nav-'+id);if(el){el.style.display=el.style.display==='block'?'none':'block';var parent=document.getElementById('nav-item-'+id);if(parent)parent.classList.toggle('open')}}
function setActive(path){document.querySelectorAll('.nav-link').forEach(function(el){el.classList.remove('active');if(el.getAttribute('href')===path){el.classList.add('active');var p=el.closest('.nav-children');if(p){p.style.display='block';var pi=p.previousElementSibling;if(pi)pi.classList.add('open')}}});var crumbs=document.getElementById('breadcrumb');if(crumbs){var parts=path.split('/').filter(Boolean);var html='<a href="index.html">首页</a>';var acc='';parts.forEach(function(p,i){acc+='/'+p;var label=document.querySelector('.nav-link[href="'+acc+'"]');if(label&&i<parts.length-1){html+=' > <a href="'+acc+'">'+label.textContent.trim()+'</a>'}});crumbs.innerHTML=html}}
"""

# ── Markdown → HTML ───────────────────────────────────────
def md_to_html(text):
    lines = text.split('\n')
    out, i = [], 0
    in_pre = in_table = in_ul = in_ol = False

    while i < len(lines):
        l = lines[i]

        if l.strip().startswith('```'):
            if not in_pre:
                out.append('<pre><code>')
                in_pre = True
            else:
                out.append('</code></pre>')
                in_pre = False
            i += 1
            continue
        if in_pre:
            out.append(l)
            i += 1
            continue

        if re.match(r'^---+$', l.strip()):
            out.append('<hr>')
            i += 1
            continue

        hm = re.match(r'^(#{1,3}) (.+)$', l)
        if hm:
            lvl = len(hm.group(1)) + 1
            out.append('<h' + str(lvl) + '>' + hm.group(2) + '</h' + str(lvl) + '>')
            i += 1
            continue

        if l.startswith('>'):
            out.append('<blockquote>' + l[1:].strip() + '</blockquote>')
            i += 1
            continue

        # 表格行
        if '|' in l and l.strip().startswith('|'):
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            if not any(re.match(r'^[-:]+$', c) for c in cells):
                if not in_table:
                    out.append('<table><thead>')
                    in_table = True
                tag = 'th' if any('-' in c or ':' in c for c in cells) else 'td'
                if tag == 'th':
                    out.append('</thead><tbody>')
                out.append('<tr>' + ''.join('<' + tag + '>' + c + '</' + tag + '>' for c in cells if c) + '</tr>')
            i += 1
            continue
        else:
            if in_table:
                out.append('</tbody></table>')
                in_table = False

        # ul
        if l.strip().startswith('- ') or l.strip().startswith('* '):
            if not in_ul:
                out.append('<ul>')
                in_ul = True
            out.append('<li>' + l.strip()[2:] + '</li>')
            i += 1
            continue
        else:
            if in_ul:
                out.append('</ul>')
                in_ul = False

        # ol
        m = re.match(r'^(\d+)\. (.+)$', l.strip())
        if m:
            if not in_ol:
                out.append('<ol>')
                in_ol = True
            out.append('<li>' + m.group(2) + '</li>')
            i += 1
            continue
        else:
            if in_ol:
                out.append('</ol>')
                in_ol = False

        stripped = l.strip()
        if stripped:
            stripped = re.sub(r'`([^`]+)`', r'<code>\1</code>', stripped)
            stripped = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', stripped)
            out.append('<p>' + stripped + '</p>')
        i += 1

    if in_pre: out.append('</code></pre>')
    if in_table: out.append('</tbody></table>')
    if in_ul: out.append('</ul>')
    if in_ol: out.append('</ol>')
    return '\n'.join(out)

def get_title(md):
    m = re.search(r'^# (.+)$', md, re.MULTILINE)
    return (m.group(1) or '无标题').strip()

def get_desc(md):
    m = re.search(r'^> (.+)$', md, re.MULTILINE)
    return (m.group(1) or '').strip() if m else ''

# ── 导航树 HTML ────────────────────────────────────────────
def nav_html(current):
    lines = ['<div id="nav-tree">']
    for item in NAV_TREE:
        children = item.get('children', [])
        has_kids = bool(children)
        is_active = (current == item['file'])
        if has_kids:
            lines.append('<div class="nav-item" id="nav-item-' + item['id'] + '">')
            cls = 'nav-link'
            if is_active: cls += ' active'
            lines.append('<div class="' + cls + '" onclick="toggleNav(\'' + item['id'] + '\')">'
                         + item['label'] + '<span class="arrow">&#9658;</span></div>')
            lines.append('<div class="nav-children" id="nav-' + item['id'] + '" style="display:none">')
            for child in children:
                c_active = (current == child['file'])
                c_cls = 'nav-link'
                if c_active: c_cls += ' active'
                lines.append('<a class="' + c_cls + '" href="' + child['file'] + '">'
                             + child['label'] + '</a>')
            lines.append('</div></div>')
        else:
            cls = 'nav-link'
            if is_active: cls += ' active'
            lines.append('<a class="' + cls + '" href="' + item['file'] + '">'
                         + item['label'] + '</a>')
    lines.append('</div>')
    return '\n'.join(lines)

# ── 页面包装 ──────────────────────────────────────────────
def wrap(content, current, title, desc):
    n = nav_html(current)
    bc = ''
    if current != 'index.html':
        bc = '<a href="index.html">首页</a> &rsaquo; ' + title
    return (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
        '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>' + title + ' | ' + SITE_TITLE + '</title>\n'
        '<meta name="description" content="' + desc + '">\n'
        '<style>' + CSS + '</style>\n'
        '</head>\n<body>\n'
        '<div id="sidebar">\n'
        '<div id="sb-header">' + SITE_TITLE + '<span>定量药理 · 临床药理 · 前沿追踪</span></div>\n'
        + n + '\n</div>\n'
        '<div id="main">\n'
        '<div id="topbar">\n'
        '<button id="sb-toggle" onclick="document.getElementById(\'sidebar\').classList.toggle(\'open\')">&#9776;</button>\n'
        '<div id="breadcrumb">' + bc + '</div>\n'
        '<div id="topbar-right">更新: ' + NOW + '</div>\n'
        '</div>\n'
        '<div id="content">\n' + content + '\n</div>\n'
        '<footer>© 2025 定量药理与临床药理前沿追踪 · 内容版权归属原作者 · '
        '<a href="https://github.com/seansilencer/quantitative-pharma-blog">GitHub</a></footer>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '<script>setActive("' + current + '")</script>\n'
        '</body>\n</html>'
    )

# ── 文章卡片解析 ──────────────────────────────────────────
def render_cards(md_text):
    rows = []
    for l in md_text.split('\n'):
        if '|' in l and l.strip().startswith('|'):
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            if not any(re.match(r'^[-:]+$', c) for c in cells):
                rows.append(cells)

    if not rows:
        return ''

    hdr = rows[0]
    t_idx = next((j for j, c in enumerate(hdr) if '标题' in c or '文章' in c or '名称' in c), 1)
    s_idx = next((j for j, c in enumerate(hdr) if '来源' in c or '作者' in c or '期刊' in c), 2)
    d_idx = next((j for j, c in enumerate(hdr) if '日期' in c or '时间' in c), 3)
    st_idx = next((j for j, c in enumerate(hdr) if '状态' in c), 0)
    sm_idx = next((j for j, c in enumerate(hdr) if '摘要' in c or '描述' in c), -1)

    cards = []
    for row in rows[1:]:
        if len(row) <= t_idx:
            continue
        title_cell = row[t_idx].strip()
        if not title_cell:
            continue

        # 提取链接
        lnk = '#'
        lnk_ext = False
        link_m = re.search(r'\[([^\]]+)\]\(([^)]+)\)', title_cell)
        if link_m:
            title_text = link_m.group(1)
            raw_link = link_m.group(2)
            lnk_ext = raw_link.startswith('http')
            lnk = raw_link if lnk_ext else ('#' if raw_link == '#' else raw_link)
        else:
            title_text = title_cell

        title_text = re.sub(r'^[\U0001F195\U00002705\U0001F512]+', '', title_text).strip()

        src = row[s_idx].strip() if s_idx >= 0 and s_idx < len(row) else ''
        dt  = row[d_idx].strip() if d_idx >= 0 and d_idx < len(row) else ''
        st  = row[st_idx].strip() if st_idx >= 0 and st_idx < len(row) else ''
        sm  = row[sm_idx].strip() if sm_idx >= 0 and sm_idx < len(row) else ''

        if '🆕' in st or '新增' in st:
            sc = 's-new'; st_text = '新增'
        elif '✅' in st or '近期' in st or '收录' in st:
            sc = 's-old'; st_text = '收录'
        else:
            sc = 's-classic'; st_text = '经典'

        ext_attr = ' target="_blank" rel="noopener"' if lnk_ext else ''
        card = (
            '<div class="article-card">'
            '<div class="card-meta">'
            '<span class="card-status ' + sc + '">' + st_text + '</span>'
            '<span class="card-source">' + src + '</span>'
            '</div>'
            '<div class="card-title"><a href="' + lnk + '"' + ext_attr + '>' + title_text + '</a></div>'
            '<div class="card-summary">' + sm + '</div>'
            '<div class="card-footer">'
            '<span class="card-date">' + dt + '</span>'
            '<a class="card-link" href="' + lnk + '"' + ext_attr + '>阅读 &#8594;</a>'
            '</div>'
            '</div>'
        )
        cards.append(card)

    return '<div class="card-grid">' + '\n'.join(cards) + '</div>' if cards else ''

# ── 构建单个 md 页面 ──────────────────────────────────────
def build_page(src, dst, is_article=False):
    with open(src, encoding='utf-8') as f:
        raw = f.read()

    title = get_title(raw)
    desc  = get_desc(raw)
    body_html = ''

    if is_article:
        body_html = (
            '<div class="sec-header"><h1>📚 文章总目录</h1>'
            '<p>' + desc + '</p>'
            '<p class="updated">🆕本周新增 · ✅近期收录 · 🔒历史经典 — 点击卡片访问原文</p></div>'
            + render_cards(raw)
        )
    else:
        body_html = (
            '<div class="sec-header"><h1>' + title + '</h1>'
            + ('<p>' + desc + '</p>' if desc else '')
            + '</div>'
            '<div class="md-body">' + md_to_html(raw) + '</div>'
        )

    html = wrap(body_html, str(dst).replace('site/', ''), title, desc)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)
    print('  ✓', src.relative_to(SRC))

# ── 首页 ──────────────────────────────────────────────────
def build_home():
    with open(SRC / 'index.md', encoding='utf-8') as f:
        raw = f.read()
    title = get_title(raw)
    desc  = get_desc(raw)

    sections = [
        ("📐","定量药理建模","PBPK · PopPK · PK/PD","quantitative-pharmacology/index.html"),
        ("💊","临床药理","创新药 · 仿制药 · 特殊人群","clinical-pharmacology/index.html"),
        ("📚","文章总目录","同行评审 · 公众号解读 · 会议报告","articles/index.html"),
        ("📋","法规与指南","NMPA · FDA · EMA 指导原则","regulations/index.html"),
        ("🎓","会议与培训","国内外学术会议","conferences/index.html"),
        ("👥","专家名录","国内 · 国际专家动态","experts/index.html"),
        ("🔧","学术资源","期刊推荐 · 工具软件","resources/index.html"),
    ]

    sc = []
    for icon, name, d, href in sections:
        sc.append(
            '<div class="article-card">'
            '<div style="font-size:2rem;margin-bottom:.4rem">' + icon + '</div>'
            '<div class="card-title"><a href="' + href + '">' + name + '</a></div>'
            '<div class="card-summary">' + d + '</div>'
            '<div class="card-footer"><a class="card-link" href="' + href + '">进入 ›</a></div>'
            '</div>'
        )

    cards_html = render_cards((SRC / 'articles' / 'index.md').read_text(encoding='utf-8')) if (SRC / 'articles' / 'index.md').exists() else ''

    body = (
        '<div class="sec-header"><h1>🏠 ' + title + '</h1><p>' + desc + '</p>'
        '<p class="updated">更新: ' + NOW + ' · 每周五更新</p></div>'
        '<div class="card-grid" style="margin-bottom:2rem">' + '\n'.join(sc) + '</div>'
        '<h2 style="margin-top:2rem;margin-bottom:1rem">📰 本周新增文章</h2>'
        + cards_html
        + '<p style="margin-top:2rem;color:var(--muted);font-size:.85rem">'
        '本站在 tools/update_blog.py 的协助下，每周自动追踪更新同行评审论文、专业公众号解读、行业会议报告等。</p>'
    )

    html = wrap(body, 'index.html', title, desc)
    with open(DST / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('  ✓ index.html')

# ── main ─────────────────────────────────────────────────
def main():
    print('\n=== Building site: docs/ → site/ ===\n')
    DST.mkdir(exist_ok=True)

    build_home()

    n = 0
    for md_file in SRC.rglob('*.md'):
        rel = md_file.relative_to(SRC)
        if rel.parts[0] in ('.', 'stylesheets') or rel.name == 'index.md':
            continue
        is_article = bool('articles/index' in str(rel))
        dst_file = DST / rel.with_suffix('.html')
        build_page(md_file, dst_file, is_article=is_article)
        n += 1

    print('\n✓ Done:', n, 'content pages')

    # copy CSS if any
    css_src = SRC / 'stylesheets' / 'extra.css'
    if css_src.exists():
        css_dst = DST / 'stylesheets' / 'extra.css'
        css_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(css_src, css_dst)

if __name__ == '__main__':
    main()