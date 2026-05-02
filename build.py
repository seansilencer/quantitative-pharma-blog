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

# ── 标签 → 分类频道映射 ────────────────────────────────
TAG_MAP = {
    "pbpk":       "📐 PBPK / 生理药代动力学",
    "poppk":      "📐 PopPK / 群体药代动力学",
    "pkbd":       "📐 PK/PD 关联分析",
    "qpm":        "📐 临床获益与定量药理",
    "innovative": "💊 创新药临床药理",
    "generic":    "💊 仿制药/生物等效性",
    "special":   "💊 特殊人群药理",
    "regulation":"📋 法规与指南",
    "domestic":   "👥 国内专家与团队",
    "international": "👥 国际专家与团队",
}

# ── 导航配置 ──────────────────────────────────────────────
NAV_TREE = [
    {"id": "home",     "label": "🏠 首页",              "file": "/index.html"},
    {"id": "qpm",      "label": "📐 定量药理建模",        "file": "/quantitative-pharmacology/index.html", "children": [
        {"id": "qpm-pbpk","label":"PBPK 建模",            "file":"/quantitative-pharmacology/pbpk.html"},
        {"id": "qpm-poppk","label":"PopPK 建模",          "file":"/quantitative-pharmacology/poppk.html"},
        {"id": "qpm-pkbd","label":"PK/PD 关联",           "file":"/quantitative-pharmacology/pkbd.html"},
    ]},
    {"id": "cp",       "label": "💊 临床药理",            "file": "/clinical-pharmacology/index.html", "children": [
        {"id": "cp-innov","label":"创新药临床药理",         "file":"/clinical-pharmacology/innovative-drugs.html"},
        {"id": "cp-generic","label":"仿制药 / BE",         "file":"/clinical-pharmacology/generic-drugs.html"},
        {"id": "cp-special","label":"特殊人群药理",        "file":"/clinical-pharmacology/special-populations.html"},
    ]},
    {"id": "articles", "label": "📚 文章总目录",           "file": "/articles/index.html"},
    {"id": "regulations","label":"📋 法规与指南",         "file":"/regulations/index.html"},
    {"id": "conferences","label":"🎓 会议与培训",         "file":"/conferences/index.html"},
    {"id": "experts",  "label": "👥 专家名录",             "file": "/experts/index.html", "children": [
        {"id": "exp-dom","label":"国内专家",               "file":"/experts/domestic.html"},
        {"id": "exp-intl","label":"国际专家",              "file":"/experts/international.html"},
    ]},
    {"id": "resources","label": "🔧 学术资源",            "file": "/resources/index.html", "children": [
        {"id": "res-journals","label":"期刊推荐",          "file":"/resources/journals.html"},
        {"id": "res-tools","label":"工具软件",             "file":"/resources/tools.html"},
    ]},
]

# ── CSS ──────────────────────────────────────────────────
CSS = """
:root{--bg:#f4f6fb;--sb:#1a1f2e;--sb-fg:#a8b3cf;--sb-active:#5c6bc0;
      --accent:#5c6bc0;--acc-bg:#e8eaf6;--text:#1a1e2e;--muted:#6b7280;
      --card:#fff;--border:#e2e8f0;--card-shadow:0 2px 8px rgba(92,107,192,.1)}
*{box-sizing:border-box;margin:0;padding:0}
body{display:flex;min-height:100vh;background:var(--bg);color:var(--text);
     font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.6}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

/* ── 侧边栏 ── */
#sidebar{width:270px;min-width:270px;background:var(--sb);color:var(--sb-fg);
         position:fixed;top:0;left:0;height:100vh;overflow-y:auto;
         display:flex;flex-direction:column}
#sb-header{padding:1.2rem 1rem 1rem;border-bottom:1px solid rgba(255,255,255,.07);
           color:#fff;font-weight:700;font-size:.95rem;line-height:1.4}
#sb-header span{font-size:.72rem;opacity:.45;font-weight:400;display:block;margin-top:.25rem}
#nav-tree{padding:.5rem 0 2rem}
.nav-item{padding:0}
.nav-link{display:flex;align-items:center;padding:.55rem 1rem;font-size:.88rem;
          color:var(--sb-fg);cursor:pointer;transition:background .15s,color .15s;
          text-decoration:none;user-select:none}
.nav-link:hover{background:rgba(255,255,255,.06);color:#fff}
.nav-link.active{background:var(--sb-active);color:#fff;font-weight:500}
.nav-link .arrow{margin-left:auto;font-size:.65rem;transition:transform .2s;color:#566480}
.nav-link.open .arrow{transform:rotate(90deg)}
.nav-children{display:none;padding-left:.6rem}
.nav-children .nav-link{padding:.38rem 1rem .38rem 2rem;font-size:.82rem}

/* ── 主区 ── */
#main{margin-left:270px;flex:1;display:flex;flex-direction:column;min-width:0}
#topbar{background:#fff;border-bottom:1px solid var(--border);padding:.75rem 2rem;
        display:flex;align-items:center;gap:1rem;position:sticky;top:0;z-index:10}
#topbar .sec-title{flex:1;font-size:.9rem;font-weight:600;color:var(--text)}
#breadcrumb{font-size:.82rem;color:var(--muted)}
#breadcrumb a{color:var(--accent)}
#topbar-right{margin-left:auto;font-size:.78rem;color:var(--muted)}
#content{padding:2rem 2.5rem 4rem}
footer{background:#fff;border-top:1px solid var(--border);padding:.8rem 2rem;
       text-align:center;font-size:.78rem;color:var(--muted)}
footer a{color:var(--accent)}

/* ── 卡片网格 ── */
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem;margin-top:1rem}
.article-card{background:var(--card);border:1px solid var(--border);border-radius:12px;
              padding:1.1rem 1.2rem;transition:box-shadow .2s,transform .2s;
              display:flex;flex-direction:column;gap:.4rem;cursor:pointer}
.article-card:hover{box-shadow:0 6px 20px rgba(92,107,192,.15);transform:translateY(-2px)}
.card-meta{display:flex;gap:.4rem;align-items:center;flex-wrap:wrap}
.card-status{padding:.1rem .5rem;border-radius:99px;font-size:.7rem;font-weight:600}
.s-new{background:#e8f5e9;color:#2e7d32}
.s-old{background:#e3f2fd;color:#1565c0}
.s-classic{background:#f3e5f5;color:#6a1b9a}
.card-source{font-size:.76rem;color:var(--muted)}
.card-title{font-size:.95rem;font-weight:600;line-height:1.4}
.card-title a{color:var(--text)}
.article-card:hover .card-title a{color:var(--accent)}
.card-summary{font-size:.82rem;color:#555;flex:1;line-height:1.6}
.card-footer{margin-top:.3rem;display:flex;justify-content:space-between;align-items:center}
.card-date{font-size:.76rem;color:var(--muted)}
.card-link{font-size:.8rem;color:var(--accent);font-weight:500}
.card-link:hover{text-decoration:underline}

/* ── 页面头部 ── */
.sec-header{margin-bottom:1.5rem;padding-bottom:.8rem;border-bottom:2px solid var(--accent)}
.sec-header h1{font-size:1.5rem}
.sec-header p{color:var(--muted);margin-top:.3rem;font-size:.88rem}
.sec-header .updated{font-size:.78rem;margin-top:.4rem}

/* ── 标签过滤栏 ── */
.filter-bar{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1.5rem}
.filter-tag{padding:.3rem .85rem;border-radius:99px;font-size:.78rem;background:var(--card);
            border:1px solid var(--border);color:var(--muted);cursor:pointer;transition:all .15s}
.filter-tag:hover{background:var(--acc-bg);color:var(--accent);border-color:var(--accent)}
.filter-tag.active{background:var(--accent);color:#fff;border-color:var(--accent)}

/* ── 响应式 ── */
@media(max-width:768px){
  #sidebar{transform:translateX(-100%);transition:transform .3s;z-index:100}
  #sidebar.open{transform:translateX(0)}
  #main{margin-left:0}
  #sb-toggle{display:flex;align-items:center;justify-content:center;width:36px;height:36px;
             background:#f0f0f0;border-radius:6px;border:none;cursor:pointer;font-size:1.2rem}
  #content{padding:1.2rem}
  .card-grid{grid-template-columns:1fr}
}
"""

# ── JavaScript ──────────────────────────────────────────
JS = """
function toggleNav(id){
  var el=document.getElementById('nav-'+id);
  if(el){el.style.display=el.style.display==='block'?'none':'block';
  var parent=document.getElementById('nav-item-'+id);
  if(parent)parent.classList.toggle('open')}}
function setActive(path){
  var np=path.startsWith('/')?path:'/'+path;
  document.querySelectorAll('.nav-link').forEach(function(el){
    el.classList.remove('active');
    var href=el.getAttribute('href')||'';
    var nh=href.startsWith('/')?href:'/'+href;
    if(nh===np){
      el.classList.add('active');
      var p=el.closest('.nav-children');
      if(p){p.style.display='block';var pi=p.previousElementSibling;
      if(pi&&pi.classList.contains('nav-link'))pi.classList.add('open')}
    }
  });
  var crumbs=document.getElementById('breadcrumb');
  if(crumbs){
    var parts=path.split('/').filter(Boolean);
    var html='<a href="/index.html">首页</a>';
    var acc='';
    for(var i=0;i<parts.length-1;i++){
      acc+='/'+parts[i];
      var label=document.querySelector('.nav-link[href="'+acc+'.html"],.nav-link[href="'+acc+'/index.html"]');
      if(label){html+=' > <a href="'+acc+'/index.html">'+label.textContent.trim()+'</a>'}
    }
    crumbs.innerHTML=html;
  }
}
function filterCards(tag){
  var cards=document.querySelectorAll('.article-card');
  cards.forEach(function(c){
    var show=(tag==='all'||c.getAttribute('data-tag')===tag);
    c.style.display=show?'flex':'none';
  });
  document.querySelectorAll('.filter-tag').forEach(function(t){
    t.classList.toggle('active',t.getAttribute('data-tag')===tag);
  });
}
"""

# ── Markdown → HTML ─────────────────────────────────────
def md_to_html(text):
    lines = text.split('\n')
    out, i = [], 0
    in_pre = in_table = in_ul = in_ol = False

    while i < len(lines):
        l = lines[i]
        if l.strip().startswith('```'):
            if not in_pre:
                out.append('<pre><code>'); in_pre = True
            else:
                out.append('</code></pre>'); in_pre = False
            i += 1; continue
        if in_pre:
            out.append(l); i += 1; continue
        if re.match(r'^---+$', l.strip()):
            out.append('<hr>'); i += 1; continue
        hm = re.match(r'^(#{1,3}) (.+)$', l)
        if hm:
            lvl = len(hm.group(1)) + 1
            out.append('<h' + str(lvl) + '>' + hm.group(2) + '</h' + str(lvl) + '>')
            i += 1; continue
        if l.startswith('>'):
            out.append('<blockquote>' + l[1:].strip() + '</blockquote>'); i += 1; continue
        if '|' in l and l.strip().startswith('|'):
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            if not any(re.match(r'^[-:]+$', c) for c in cells):
                if not in_table: out.append('<table><thead>'); in_table = True
                tag = 'th'
                if any('-' in c or ':' in c for c in cells):
                    out.append('</thead><tbody>'); tag = 'td'
                out.append('<tr>' + ''.join('<' + tag + '>' + c + '</' + tag + '>' for c in cells if c) + '</tr>')
            i += 1; continue
        else:
            if in_table: out.append('</tbody></table>'); in_table = False
        if l.strip().startswith('- ') or l.strip().startswith('* '):
            if not in_ul: out.append('<ul>'); in_ul = True
            out.append('<li>' + l.strip()[2:] + '</li>'); i += 1; continue
        else:
            if in_ul: out.append('</ul>'); in_ul = False
        m = re.match(r'^(\d+)\. (.+)$', l.strip())
        if m:
            if not in_ol: out.append('<ol>'); in_ol = True
            out.append('<li>' + m.group(2) + '</li>'); i += 1; continue
        else:
            if in_ol: out.append('</ol>'); in_ol = False
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

# ── 全局文章数据提取 ──────────────────────────────────────
def extract_all_articles():
    """从 articles/index.md 提取所有文章数据，表格列顺序：状态|标题|来源|日期|摘要|标签"""
    articles_path = SRC / 'articles' / 'index.md'
    if not articles_path.exists():
        return []
    raw = articles_path.read_text(encoding='utf-8')
    all_articles = []

    for l in raw.split('\n'):
        if '|' not in l or not l.strip().startswith('|'):
            continue
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        # 跳过分隔行
        if any(re.match(r'^[-:]+$', c) for c in cells): continue
        # 跳过列数不足
        if len(cells) < 6: continue
        # 跳过表头（不含 http 的行）
        if not any('http' in c for c in cells): continue

        # 固定列索引: 0=状态, 1=标题, 2=来源, 3=日期, 4=摘要, 5=标签
        status_cell = cells[0]
        title_cell  = cells[1]
        source_cell = cells[2]
        date_cell  = cells[3]
        summary_cell = cells[4]
        tag_cell   = cells[5].lower().strip()

        # 解析标题中的链接
        link_m = re.search(r'\[([^\]]+)\]\((https?://[^)]+)\)', title_cell)
        if not link_m: continue
        title_text = re.sub(r'^[\U0001F195\U00002705\U0001F512]+', '', link_m.group(1)).strip()
        link = link_m.group(2).strip()

        all_articles.append({
            'title': title_text, 'link': link,
            'source': source_cell, 'date': date_cell,
            'status': status_cell, 'summary': summary_cell,
            'tag': tag_cell if tag_cell in TAG_MAP else ''
        })
    return all_articles

ALL_ARTICLES = None  # lazy load

def get_articles():
    global ALL_ARTICLES
    if ALL_ARTICLES is None:
        ALL_ARTICLES = extract_all_articles()
    return ALL_ARTICLES

# ── 文章卡片渲染 ──────────────────────────────────────────
def render_card(art):
    if '🆕' in art['status'] or '新增' in art['status']:
        sc = 's-new'; st = '新增'
    elif '✅' in art['status'] or '收录' in art['status']:
        sc = 's-old'; st = '收录'
    else:
        sc = 's-classic'; st = '经典'

    summary = art.get('summary') or ''
    # 去掉可能残留的 emoji
    summary = re.sub(r'^[\U0001F195\U00002705\U0001F512🆕✅🔒]+', '', summary).strip()

    parts = [
        '<div class="article-card" data-tag="' + art['tag'] + '">',
        '<div class="card-meta">',
        '<span class="card-status ' + sc + '">' + st + '</span>',
        '<span class="card-source">' + art['source'] + '</span>',
        '</div>',
        '<div class="card-title"><a href="' + art['link'] + '" target="_blank" rel="noopener">' + art['title'] + '</a></div>',
    ]
    if summary:
        parts.append('<div class="card-summary">' + summary + '</div>')
    parts.extend([
        '<div class="card-footer">',
        '<span class="card-date">' + art['date'] + '</span>',
        '<a class="card-link" href="' + art['link'] + '" target="_blank" rel="noopener">阅读 →</a>',
        '</div>',
        '</div>',
    ])
    return ''.join(parts)

def cards_by_tag(tag):
    """返回指定标签的所有卡片 HTML"""
    arts = [a for a in get_articles() if a['tag'] == tag]
    if not arts:
        return '<p style="color:var(--muted);font-size:.88rem">该分类暂无文章，详见 <a href="/articles/index.html">文章总目录</a>。</p>'
    return '<div class="card-grid">' + '\n'.join(render_card(a) for a in arts) + '</div>'

def cards_all():
    arts = get_articles()
    if not arts:
        return ''
    return '<div class="card-grid">' + '\n'.join(render_card(a) for a in arts) + '</div>'

# ── 导航树 HTML ───────────────────────────────────────────
def nav_html(current):
    lines = ['<div id="nav-tree">']
    for item in NAV_TREE:
        children = item.get('children', [])
        has_kids = bool(children)
        is_active = (current == item['file'])
        if has_kids:
            lines.append('<div class="nav-item" id="nav-item-' + item['id'] + '">')
            cls = 'nav-link' + (' active' if is_active else '')
            lines.append('<div class="' + cls + '" onclick="toggleNav(\'' + item['id'] + '\')">'
                         + item['label'] + '<span class="arrow">&#9658;</span></div>')
            lines.append('<div class="nav-children" id="nav-' + item['id'] + '" style="display:none">')
            for child in children:
                c_active = (current == child['file'])
                c_cls = 'nav-link' + (' active' if c_active else '')
                lines.append('<a class="' + c_cls + '" href="' + child['file'] + '">'
                             + child['label'] + '</a>')
            lines.append('</div></div>')
        else:
            cls = 'nav-link' + (' active' if is_active else '')
            lines.append('<a class="' + cls + '" href="' + item['file'] + '">'
                         + item['label'] + '</a>')
    lines.append('</div>')
    return '\n'.join(lines)

# ── 页面包装 ──────────────────────────────────────────────
def wrap(content, current, title, desc):
    n = nav_html(current)
    bc = ''
    if current != '/index.html':
        bc = '<a href="/index.html">首页</a> &rsaquo; ' + title
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
        '<div class="sec-title">' + title + '</div>\n'
        '<div id="breadcrumb">' + bc + '</div>\n'
        '<div id="topbar-right">更新: ' + NOW + '</div>\n'
        '</div>\n'
        '<div id="content">\n' + content + '\n</div>\n'
        '<footer>© 2025 定量药理与临床药理前沿追踪 · '
        '<a href="https://github.com/seansilencer/quantitative-pharma-blog">GitHub</a></footer>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '<script>setActive("' + current + '")</script>\n'
        '</body>\n</html>'
    )

# ── 页面构建 ──────────────────────────────────────────────
def build_page(src, dst, page_type='md', tag=None, desc=''):
    with open(src, encoding='utf-8') as f:
        raw = f.read()

    title = get_title(raw)
    desc = desc or get_desc(raw)
    body_html = ''

    if page_type == 'cards-all':
        body_html = (
            '<div class="sec-header"><h1>📚 ' + title + '</h1>'
            '<p>' + desc + '</p>'
            '<p class="updated">🆕本周新增 · ✅近期收录 · 🔒历史经典 — 点击卡片访问原文</p></div>'
            + cards_all()
        )
    elif page_type == 'cards-filter':
        body_html = (
            '<div class="sec-header"><h1>' + title + '</h1>'
            + ('<p>' + desc + '</p>' if desc else '')
            + '</div>'
            + cards_by_tag(tag)
        )
    else:
        body_html = (
            '<div class="sec-header"><h1>' + title + '</h1>'
            + ('<p>' + desc + '</p>' if desc else '') + '</div>'
            '<div class="md-body">' + md_to_html(raw) + '</div>'
        )

    html = wrap(body_html, '/' + str(dst).replace('site/', ''), title, desc)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)
    print('  ✓', src.relative_to(SRC))

# ── 首页 ─────────────────────────────────────────────────
def build_home():
    with open(SRC / 'index.md', encoding='utf-8') as f:
        raw = f.read()
    title = get_title(raw)
    desc  = get_desc(raw)

    sections = [
        ("📐","定量药理建模","PBPK · PopPK · PK/PD","/quantitative-pharmacology/index.html"),
        ("💊","临床药理","创新药 · 仿制药 · 特殊人群","/clinical-pharmacology/index.html"),
        ("📚","文章总目录","同行评审 · 公众号解读 · 会议报告","/articles/index.html"),
        ("📋","法规与指南","NMPA · FDA · EMA 指导原则","/regulations/index.html"),
        ("🎓","会议与培训","国内外学术会议","/conferences/index.html"),
        ("👥","专家名录","国内 · 国际专家动态","/experts/index.html"),
        ("🔧","学术资源","期刊推荐 · 工具软件","/resources/index.html"),
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

    # 首页「本周新增文章」取 tag='pbpk' 或 'poppk' 的前 6 篇
    arts = get_articles()
    new_arts = [a for a in arts if a['tag'] in ('pbpk','poppk','pkbd','innovative')][:6]
    new_cards = ''.join(render_card(a) for a in new_arts)

    body = (
        '<div class="sec-header"><h1>🏠 ' + title + '</h1><p>' + desc + '</p>'
        '<p class="updated">更新: ' + NOW + ' · 每周五更新</p></div>'
        '<div class="card-grid" style="margin-bottom:2rem">' + '\n'.join(sc) + '</div>'
        '<h2 style="margin-top:2rem;margin-bottom:1rem">📰 本周新增文章</h2>'
        '<div class="card-grid">' + new_cards + '</div>'
        '<p style="margin-top:2rem;color:var(--muted);font-size:.85rem">'
        '系统追踪同行评审论文、公众号解读、行业会议报告。'
        '<a href="/articles/index.html" style="margin-left:.5rem">查看全部文章 ›</a></p>'
    )

    html = wrap(body, '/index.html', title, desc)
    with open(DST / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('  ✓ index.html')

# tag → 目标页面（用于生成链接）
TAG_TO_PAGE = {
    'pbpk':       '/quantitative-pharmacology/pbpk.html',
    'poppk':      '/quantitative-pharmacology/poppk.html',
    'pkbd':       '/quantitative-pharmacology/pkbd.html',
    'qpm':        '/quantitative-pharmacology/index.html',
    'innovative': '/clinical-pharmacology/innovative-drugs.html',
    'generic':    '/clinical-pharmacology/generic-drugs.html',
    'special':    '/clinical-pharmacology/special-populations.html',
    'regulation': '/regulations/index.html',
    'domestic':   '/experts/domestic.html',
    'international': '/experts/international.html',
}

# 源文件相对路径 → tag（直接比对，无路径转换问题）
_SRC_TAG = {}
for _t, _pf in TAG_TO_PAGE.items():
    _src = _pf.rsplit('.html', 1)[0]   # 去掉 .html → '/quantitative-pharmacology/pbpk'
    _src = _src.lstrip('/')             # → 'quantitative-pharmacology/pbpk'
    _SRC_TAG[_src] = _t

# ── main ─────────────────────────────────────────────────
def main():
    print('\n=== Building site: docs/ → site/ ===\n')
    DST.mkdir(exist_ok=True)

    build_home()

    n = 0
    for md_file in SRC.rglob('*.md'):
        rel = md_file.relative_to(SRC)
        if rel.parts[0] in ('.', 'stylesheets'):
            continue
        if rel.name == 'index.md' and len(rel.parts) == 1:
            continue

        dst_file = DST / rel.with_suffix('.html')
        path_str = str(rel)

        # articles/index.md → 卡片总览页
        if path_str == 'articles/index.md':
            build_page(md_file, dst_file, page_type='cards-all')
            n += 1; continue

        # 已知 tag 的子分类页 → 过滤卡片页
        src_key = str(rel).replace('\\', '/')
        if src_key.endswith('.md'):
            src_key = src_key[:-3]   # 去掉 .md 后缀，与 _SRC_TAG 的 key 匹配
        tag = _SRC_TAG.get(src_key)
        if tag:
            build_page(md_file, dst_file, page_type='cards-filter', tag=tag)
            n += 1; continue

        # 其他页面 → 普通 md 渲染
        build_page(md_file, dst_file, page_type='md')
        n += 1

    print('\n✓ Done:', n, 'content pages')

    css_src = SRC / 'stylesheets' / 'extra.css'
    if css_src.exists():
        css_dst = DST / 'stylesheets' / 'extra.css'
        css_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(css_src, css_dst)

if __name__ == '__main__':
    main()