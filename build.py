#!/usr/bin/env python3
"""
静态博客生成器 - build.py v2
docs/ → site/ ，零依赖，升级版 UI
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
    "special":    "💊 特殊人群药理",
    "regulation": "📋 法规与指南",
    "domestic":   "👥 国内专家与团队",
    "international": "👥 国际专家与团队",
}

# ── 导航配置（v3） ─────────────────────────────────────
NAV_TREE = [
    {"id": "home",   "label": "🏠 首页",              "file": "/index.html"},
    {"id": "qpm",   "label": "📐 定量药理建模",        "file": "/quantitative-pharmacology/index.html", "children": [
        {"id": "qpm-pbpk",  "label": "PBPK 建模",    "file": "/quantitative-pharmacology/pbpk.html"},
        {"id": "qpm-poppk", "label": "PopPK 建模",   "file": "/quantitative-pharmacology/poppk.html"},
        {"id": "qpm-pkbd",  "label": "PK/PD 关联",   "file": "/quantitative-pharmacology/pkbd.html"},
    ]},
    {"id": "cp",    "label": "💊 临床药理",             "file": "/clinical-pharmacology/index.html", "children": [
        {"id": "cp-innov",  "label": "创新药临床药理", "file": "/clinical-pharmacology/innovative-drugs.html"},
        {"id": "cp-generic","label": "仿制药 / BE",    "file": "/clinical-pharmacology/generic-drugs.html"},
        {"id": "cp-special","label": "特殊人群药理",   "file": "/clinical-pharmacology/special-populations.html"},
    ]},
    {"id": "regulations","label":"📋 法规与指南",       "file": "/regulations/index.html"},
    {"id": "conferences","label":"🎓 会议与培训",       "file": "/conferences/index.html"},
    {"id": "journals",  "label": "📚 期刊推荐",         "file": "/resources/journals.html"},
    {"id": "tools",     "label": "🔧 工具软件",         "file": "/resources/tools.html"},
    {"id": "tutorials", "label": "📖 学习资源",         "file": "/tutorials/index.html", "children": [
        {"id": "tut-intro",    "label": "入门教程",    "file": "/tutorials/index.html"},
        {"id": "tut-advanced", "label": "进阶教程",   "file": "/tutorials/index.html"},
        {"id": "tut-practice", "label": "实战资源",    "file": "/tutorials/index.html"},
        {"id": "tut-expert",   "label": "专家分享",    "file": "/tutorials/index.html"},
    ]},
    {"id": "experts",  "label": "👥 专家名录",          "file": "/experts/index.html", "children": [
        {"id": "exp-dom",  "label": "国内专家",        "file": "/experts/domestic.html"},
        {"id": "exp-intl", "label": "国际专家",        "file": "/experts/international.html"},
    ]},
]

# ── CSS v2 ──────────────────────────────────────────────
CSS = """
:root{
  --bg:#f8f9fc;--sb:#13182a;--sb-fg:#9aa3b8;--sb-hover:#1e2540;
  --sb-active:#5c6bc0;--accent:#5c6bc0;--accent2:#7986cb;
  --acc-bg:#eef0fb;--text:#1a1e2e;--muted:#8892a4;
  --card:#fff;--border:#e4e8f0;--card2:#f0f2f8;
  --shadow:0 2px 12px rgba(92,107,192,.12);
  --shadow-hover:0 8px 30px rgba(92,107,192,.22);
  --radius:14px;--radius-sm:8px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{display:flex;min-height:100vh;background:var(--bg);color:var(--text);
     font-family:"PingFang SC","Microsoft YaHei",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
     line-height:1.7}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

/* ── 侧边栏 ── */
#sidebar{width:268px;min-width:268px;background:var(--sb);color:var(--sb-fg);
        position:fixed;top:0;left:0;height:100vh;overflow-y:auto;
        display:flex;flex-direction:column;
        scrollbar-width:thin;scrollbar-color:#2a3050 #13182a}
#sidebar::-webkit-scrollbar{width:4px}
#sidebar::-webkit-scrollbar-thumb{background:#2a3050;border-radius:2px}
#sb-header{padding:1.4rem 1.2rem 1.1rem;
           border-bottom:1px solid rgba(255,255,255,.06);
           color:#fff;font-weight:700;font-size:.88rem;line-height:1.5;
           background:linear-gradient(135deg,#1a2050 0%,#13182a 100%)}
#sb-header span{font-size:.7rem;opacity:.4;font-weight:400;display:block;margin-top:.2rem;
                 letter-spacing:.5px}
#nav-tree{padding:.6rem 0 2rem}

/* 搜索框 */
#sb-search{margin:.8rem .8rem .4rem;position:relative}
#sb-search input{width:100%;padding:.5rem .75rem .5rem 2rem;background:#1e2540;border:1px solid #2a3050;
                 border-radius:var(--radius-sm);color:#fff;font-size:.8rem;outline:none;
                 transition:border .2s,box-shadow .2s}
#sb-search input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(92,107,192,.2)}
#sb-search::before{content:"🔍";position:absolute;left:.55rem;top:50%;transform:translateY(-50%);
                   font-size:.7rem;opacity:.5}

/* 一级导航项 */
.nav-item{padding:0;position:relative}
.nav-link{display:flex;align-items:center;padding:.52rem 1rem;font-size:.85rem;
          color:var(--sb-fg);cursor:pointer;transition:background .15s,color .15s,padding-left .15s;
          text-decoration:none;user-select:none;border-left:3px solid transparent}
.nav-link:hover{background:var(--sb-hover);color:#c8d0e8;padding-left:1.15rem}
.nav-link.active{background:rgba(92,107,192,.18);color:#fff;border-left-color:var(--accent);font-weight:600}
.nav-link .arrow{margin-left:auto;font-size:.6rem;transition:transform .25s;color:#4a5580}
.nav-link.open .arrow{transform:rotate(90deg)}
.nav-children{display:none;padding-left:.5rem}
.nav-children .nav-link{padding:.32rem 1rem .32rem 2rem;font-size:.8rem}

/* 子导航展开动效 */
.nav-children.open{display:block;animation:slideDown .2s ease}
@keyframes slideDown{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}

/* ── 主区 ── */
#main{margin-left:268px;flex:1;display:flex;flex-direction:column;min-width:0}
#topbar{background:rgba(255,255,255,.92);backdrop-filter:blur(12px);
        border-bottom:1px solid var(--border);padding:.7rem 2rem;
        display:flex;align-items:center;gap:1rem;position:sticky;top:0;z-index:10}
#topbar .sec-title{flex:1;font-size:.88rem;font-weight:600;color:var(--text)}
#breadcrumb{font-size:.8rem;color:var(--muted)}
#breadcrumb a{color:var(--accent)}
#breadcrumb span{margin:0 .3rem;opacity:.4}
#topbar-right{margin-left:auto;font-size:.76rem;color:var(--muted);display:flex;align-items:center;gap:.4rem}
#topbar-right::before{content:"●";color:#4caf50;font-size:.5rem}
#content{padding:2.2rem 2.8rem 5rem}
footer{background:#fff;border-top:1px solid var(--border);padding:.9rem 2rem;
       text-align:center;font-size:.78rem;color:var(--muted)}
footer a{color:var(--accent)}

/* ── 卡片网格 ── */
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:1.1rem;margin-top:1rem}
.card-grid.wide{grid-template-columns:repeat(auto-fill,minmax(340px,1fr))}

/* 主导航大卡片 */
.hero-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);
          padding:1.4rem 1.5rem;display:flex;flex-direction:column;gap:.5rem;
          transition:box-shadow .25s,transform .25s,border-color .25s;cursor:pointer;
          position:relative;overflow:hidden}
.hero-card::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;
                   background:linear-gradient(90deg,var(--accent),var(--accent2));
                   opacity:0;transition:opacity .25s}
.hero-card:hover{box-shadow:var(--shadow-hover);transform:translateY(-3px);border-color:var(--accent)}
.hero-card:hover::before{opacity:1}
.hero-card .card-icon{font-size:2.2rem;line-height:1;margin-bottom:.2rem}
.hero-card .card-title{font-size:1rem;font-weight:700;color:var(--text);line-height:1.4}
.hero-card .card-sub{font-size:.8rem;color:var(--muted);flex:1;line-height:1.6}
.hero-card .card-footer{display:flex;justify-content:flex-end}
.hero-card .card-arrow{color:var(--accent);font-size:.85rem;font-weight:600;opacity:0;
                        transition:opacity .2s,transform .2s}
.hero-card:hover .card-arrow{opacity:1;transform:translateX(4px)}

/* 文章卡片 */
.article-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);
             padding:1.1rem 1.3rem;display:flex;flex-direction:column;gap:.4rem;
             transition:box-shadow .2s,transform .2s,border-color .2s}
.article-card:hover{box-shadow:var(--shadow-hover);transform:translateY(-2px);border-color:#c5cae9}
.card-meta{display:flex;gap:.35rem;align-items:center;flex-wrap:wrap}
.card-status{padding:.1rem .55rem;border-radius:99px;font-size:.68rem;font-weight:600;letter-spacing:.3px}
.s-new{background:linear-gradient(135deg,#e8f5e9,#c8e6c9);color:#2e7d32}
.s-old{background:linear-gradient(135deg,#e3f2fd,#bbdefb);color:#1565c0}
.s-classic{background:linear-gradient(135deg,#f3e5f5,#e1bee7);color:#6a1b9a}
.card-tag{padding:.1rem .5rem;border-radius:99px;font-size:.65rem;background:var(--card2);color:var(--muted)}
.card-source{font-size:.75rem;color:var(--muted)}
.card-title{font-size:.92rem;font-weight:600;line-height:1.45;color:var(--text)}
.card-title a{color:var(--text)}
.article-card:hover .card-title a{color:var(--accent)}
.card-summary{font-size:.8rem;color:#5a6178;flex:1;line-height:1.65;display:-webkit-box;
              -webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.card-footer{margin-top:.2rem;display:flex;justify-content:space-between;align-items:center}
.card-date{font-size:.73rem;color:var(--muted)}
.card-link{font-size:.78rem;color:var(--accent);font-weight:600}
.card-link:hover{text-decoration:underline}

/* ── 页面头部 ── */
.sec-header{margin-bottom:2rem;padding-bottom:1.2rem;border-bottom:2px solid var(--border);
            position:relative}
.sec-header::after{content:"";position:absolute;bottom:-2px;left:0;width:80px;height:2px;
                    background:linear-gradient(90deg,var(--accent),var(--accent2))}
.sec-header h1{font-size:1.55rem;font-weight:800;color:var(--text);line-height:1.3}
.sec-header p{color:var(--muted);margin-top:.4rem;font-size:.88rem}
.sec-header .updated{font-size:.76rem;margin-top:.5rem;color:var(--accent);font-weight:500}

/* ── 标签过滤栏 ── */
.filter-bar{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1.8rem}
.filter-tag{padding:.35rem .9rem;border-radius:99px;font-size:.78rem;
            background:var(--card);border:1px solid var(--border);color:var(--muted);
            cursor:pointer;transition:all .15s;font-weight:500}
.filter-tag:hover{background:var(--acc-bg);color:var(--accent);border-color:var(--accent)}
.filter-tag.active{background:var(--accent);color:#fff;border-color:var(--accent);box-shadow:0 2px 8px rgba(92,107,192,.3)}

/* ── 树形列表（工具页/学习资源页） ── */
.tree-layout{display:grid;grid-template-columns:280px 1fr;gap:1.5rem;align-items:start}
.tree-nav{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);
         padding:1rem 0;position:sticky;top:70px}
.tree-nav-header{padding:.5rem 1.1rem .8rem;font-size:.78rem;font-weight:700;color:var(--muted);
                text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid var(--border);
                margin-bottom:.5rem}
.tree-item{padding:.55rem 1.1rem;font-size:.85rem;color:var(--text);cursor:pointer;
           transition:background .12s,color .12s;border-left:3px solid transparent;
           display:flex;align-items:center;gap:.5rem}
.tree-item:hover{background:var(--card2);color:var(--accent)}
.tree-item.active{background:rgba(92,107,192,.1);color:var(--accent);border-left-color:var(--accent);font-weight:600}
.tree-item .tree-icon{font-size:1rem}

/* 工具详情面板 */
.tool-panel{display:flex;flex-direction:column;gap:.8rem}
.tool-detail{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);
            padding:1.5rem;opacity:0;transition:opacity .25s,box-shadow .25s}
.tool-detail.visible{opacity:1;box-shadow:var(--shadow)}
.tool-detail h2{font-size:1.2rem;font-weight:800;margin-bottom:.3rem;display:flex;align-items:center;gap:.5rem}
.tool-detail .tool-badge{padding:.15rem .6rem;border-radius:99px;font-size:.68rem;
                         background:var(--acc-bg);color:var(--accent);font-weight:600}
.tool-detail .tool-desc{font-size:.85rem;color:#5a6178;line-height:1.7;margin:.6rem 0}
.tool-detail .tool-meta{display:flex;flex-wrap:wrap;gap:.5rem;margin:.6rem 0}
.tool-detail .meta-chip{padding:.2rem .7rem;background:var(--card2);border-radius:99px;
                        font-size:.73rem;color:var(--muted)}
.tool-detail h3{font-size:.88rem;font-weight:700;margin-top:1rem;margin-bottom:.5rem;
                color:var(--text);padding-bottom:.3rem;border-bottom:1px solid var(--border)}
.tool-detail ul{margin-left:1.2rem;font-size:.82rem;color:#5a6178;line-height:1.9}
.tool-detail ul li{list-style:disc}
.tool-detail .resource-links{display:flex;flex-direction:column;gap:.4rem;margin-top:.6rem}
.tool-detail .res-link{display:flex;align-items:center;gap:.4rem;padding:.5rem .8rem;
                        background:var(--card2);border-radius:var(--radius-sm);font-size:.8rem;
                        color:var(--accent);transition:background .12s}
.tool-detail .res-link:hover{background:var(--acc-bg);text-decoration:none}

/* ── 动态数字统计 ── */
.stats-row{display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0}
.stat-card{background:linear-gradient(135deg,var(--accent),#3949ab);color:#fff;
           border-radius:var(--radius);padding:1rem 1.4rem;flex:1;min-width:120px;
           box-shadow:0 4px 15px rgba(92,107,192,.3)}
.stat-card .stat-num{font-size:1.6rem;font-weight:800;line-height:1.2}
.stat-card .stat-label{font-size:.73rem;opacity:.8;margin-top:.2rem}

/* ── 学习资源页标签切换 ── */
.tutorial-tabs{display:flex;gap:.3rem;border-bottom:2px solid var(--border);margin-bottom:1.5rem}
.tut-tab{padding:.55rem 1.2rem;font-size:.85rem;color:var(--muted);cursor:pointer;
         border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s;font-weight:600}
.tut-tab:hover{color:var(--accent)}
.tut-tab.active{color:var(--accent);border-bottom-color:var(--accent)}
.tut-content{display:none}
.tut-content.active{display:block;animation:fadeIn .2s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}

/* ── 引用块 ── */
blockquote{margin:1rem 0;padding:.8rem 1.2rem;background:linear-gradient(135deg,var(--acc-bg),#e8eaf6);
           border-left:4px solid var(--accent);border-radius:0 var(--radius-sm) var(--radius-sm) 0;
           font-size:.88rem;color:#4a5580;line-height:1.7}

/* ── 首页公告栏 ── */
.announcement{background:linear-gradient(135deg,#fff9c4,#fff59d);border:1px solid #f9a825;
              border-radius:var(--radius);padding:.9rem 1.2rem;margin-bottom:1.5rem;
              display:flex;align-items:flex-start;gap:.7rem;font-size:.83rem;color:#5d4037}
.announcement::before{content:"📢";font-size:1.1rem;flex-shrink:0}

/* ── 辅助类 ── */
.section-title{font-size:1rem;font-weight:700;color:var(--text);margin:1.8rem 0 .8rem;
               display:flex;align-items:center;gap:.5rem}
.section-title::after{content:"";flex:1;height:1px;background:var(--border)}
.text-muted{color:var(--muted);font-size:.82rem}
.divider{border:none;border-top:1px solid var(--border);margin:1.5rem 0}

/* ── 响应式 ── */
@media(max-width:900px){
  .tree-layout{grid-template-columns:1fr}
  .tree-nav{position:static}
}
@media(max-width:768px){
  #sidebar{transform:translateX(-100%);transition:transform .3s;z-index:100}
  #sidebar.open{transform:translateX(0)}
  #main{margin-left:0}
  #sb-toggle{display:flex;align-items:center;justify-content:center;width:36px;height:36px;
             background:#f0f0f0;border-radius:var(--radius-sm);border:none;cursor:pointer;font-size:1.2rem}
  #content{padding:1.2rem}
  .card-grid{grid-template-columns:1fr}
  .stats-row{flex-direction:column}
}
"""

# ── JavaScript v2 ─────────────────────────────────────────
JS = """
// 搜索高亮
function highlight(text, term){
  if(!term)return text;
  var re=new RegExp('('+term.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+')','gi');
  return text.replace(re,'<mark style="background:#fff176;padding:0 2px;border-radius:2px">$1</mark>');
}

// 导航切换
function toggleNav(id){
  var el=document.getElementById('nav-'+id);
  if(!el)return;
  var isOpen=el.style.display==='block';
  el.style.display=isOpen?'none':'block';
  el.classList.toggle('open',!isOpen);
  var parent=document.getElementById('nav-item-'+id);
  if(parent)parent.classList.toggle('open',!isOpen);
}

// 设置当前活跃导航
function setActive(path){
  var np=path.startsWith('/')?path:'/'+path;
  document.querySelectorAll('.nav-link').forEach(function(el){
    el.classList.remove('active');
    var href=el.getAttribute('href')||'';
    var nh=href.startsWith('/')?href:'/'+href;
    if(nh===np){
      el.classList.add('active');
      var p=el.closest('.nav-children');
      if(p){p.style.display='block';p.classList.add('open');
      var pi=p.previousElementSibling;
      if(pi&&pi.classList.contains('nav-link'))pi.classList.add('open')}
    }
  });
  // 面包屑
  var crumbs=document.getElementById('breadcrumb');
  if(crumbs){
    var parts=path.split('/').filter(Boolean);
    var html='<a href="/index.html">首页</a>';
    var acc='';
    for(var i=0;i<parts.length-1;i++){
      acc+='/'+parts[i];
      var label=document.querySelector('.nav-link[href="'+acc+'.html"],.nav-link[href="'+acc+'/index.html"]');
      if(label){html+=' <span>›</span> <a href="'+acc+'/index.html">'+label.textContent.trim()+'</a>'}
    }
    crumbs.innerHTML=html;
  }
}

// 卡片标签过滤
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

// 工具详情面板切换（树形列表点击）
function showTool(id){
  document.querySelectorAll('.tool-detail').forEach(function(el){el.classList.remove('visible')});
  var el=document.getElementById('tool-'+id);
  if(el)el.classList.add('visible');
  document.querySelectorAll('.tree-item').forEach(function(el){el.classList.remove('active')});
  var active=document.querySelector('.tree-item[data-tool="'+id+'"]');
  if(active)active.classList.add('active');
  // 移动端跳到详情
  if(window.innerWidth<=900){
    document.getElementById('tool-detail-container').scrollIntoView({behavior:'smooth'});
  }
}

// 学习资源标签页
function switchTutorial(id){
  document.querySelectorAll('.tut-content').forEach(function(el){el.classList.remove('active')});
  document.querySelectorAll('.tut-tab').forEach(function(el){el.classList.remove('active')});
  var el=document.getElementById('tut-'+id);
  if(el)el.classList.add('active');
  var tab=document.querySelector('.tut-tab[data-tut="'+id+'"]');
  if(tab)tab.classList.add('active');
}

// 工具页初始化
function initToolPage(firstId){
  if(firstId)showTool(firstId);
  else{
    var first=document.querySelector('.tool-detail');
    if(first)first.classList.add('visible');
  }
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
            out.append('<hr class="divider">'); i += 1; continue
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
                if not in_table: out.append('<div class="table-wrap"><table><thead>'); in_table = True
                tag = 'th'
                if any('-' in c or ':' in c for c in cells):
                    out.append('</thead><tbody>'); tag = 'td'
                out.append('<tr>' + ''.join('<' + tag + '>' + c + '</' + tag + '>' for c in cells if c) + '</tr>')
            i += 1; continue
        else:
            if in_table: out.append('</tbody></table></div>'); in_table = False
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
    if in_table: out.append('</tbody></table></div>')
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
    """从 articles/index.md 提取所有文章数据"""
    articles_path = SRC / 'articles' / 'index.md'
    if not articles_path.exists():
        return []
    raw = articles_path.read_text(encoding='utf-8')
    all_articles = []
    for l in raw.split('\n'):
        if '|' not in l or not l.strip().startswith('|'):
            continue
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if any(re.match(r'^[-:]+$', c) for c in cells): continue
        if len(cells) < 6: continue
        if not any('http' in c for c in cells): continue
        status_cell = cells[0]
        title_cell  = cells[1]
        source_cell = cells[2]
        date_cell   = cells[3]
        summary_cell = cells[4]
        tag_cell    = cells[5].lower().strip()
        link_m = re.search(r'\[([^\]]+)\]\((https?://[^)]+)\)', title_cell)
        if not link_m: continue
        title_text = re.sub(r'^[\U0001F195\U00002705\U0001F512🆕✅🔒]+', '', link_m.group(1)).strip()
        link = link_m.group(2).strip()
        all_articles.append({
            'title': title_text, 'link': link,
            'source': source_cell, 'date': date_cell,
            'status': status_cell, 'summary': summary_cell,
            'tag': tag_cell if tag_cell in TAG_MAP else ''
        })
    return all_articles

ALL_ARTICLES = None
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
    summary = re.sub(r'^[\U0001F195\U00002705\U0001F512🆕✅🔒]+', '', (art.get('summary') or '')).strip()
    tag_label = TAG_MAP.get(art.get('tag') or '', '')
    tag_html = '<span class="card-tag">' + tag_label + '</span>' if tag_label else ''
    parts = [
        '<div class="article-card" data-tag="' + art['tag'] + '">',
        '<div class="card-meta">',
        '<span class="card-status ' + sc + '">' + st + '</span>',
        tag_html,
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
        '</div></div>',
    ])
    return ''.join(parts)

def cards_by_tag(tag):
    arts = [a for a in get_articles() if a['tag'] == tag]
    if not arts:
        return '<p class="text-muted">该分类暂无文章，详见 <a href="/articles/index.html">文章总目录</a>。</p>'
    return '<div class="card-grid">' + '\n'.join(render_card(a) for a in arts) + '</div>'

def cards_all():
    arts = get_articles()
    if not arts:
        return ''
    return '<div class="card-grid">' + '\n'.join(render_card(a) for a in arts) + '</div>'

# ── 导航树 HTML ───────────────────────────────────────────
def nav_html(current):
    lines = ['<div id="sb-search"><input type="text" placeholder="搜索导航…" id="nav-search" oninput="handleSearch(this.value)"></div>']
    lines.append('<div id="nav-tree">')
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
def wrap(content, current, title, desc, extra_js=''):
    n = nav_html(current)
    bc = ''
    if current != '/index.html':
        bc = '<a href="/index.html">首页</a> <span>›</span> ' + title
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
        + extra_js + '\n'
        '</body>\n</html>'
    )

# ── 页面构建 ──────────────────────────────────────────────
def build_page(src, dst, page_type='md', tag=None, desc='', extra_js=''):
    with open(src, encoding='utf-8') as f:
        raw = f.read()
    title = get_title(raw)
    desc = desc or get_desc(raw)
    body_html = ''
    if page_type == 'cards-all':
        body_html = (
            '<div class="announcement">每周五更新 · 收录同行评审论文、专业公众号解读、行业会议报告</div>'
            '<div class="sec-header"><h1>📚 ' + title + '</h1>'
            '<p>' + desc + '</p>'
            '<p class="updated">🆕本周新增 · ✅近期收录 · 🔒历史经典 — 点击卡片访问原文</p></div>'
            '<div class="filter-bar">'
            '<span class="filter-tag active" data-tag="all" onclick="filterCards(\'all\')">全部</span>'
            + ''.join('<span class="filter-tag" data-tag="'+t+'" onclick="filterCards(\''+t+'\')">'+l+'</span>'
                      for t,l in TAG_MAP.items()) +
            '</div>'
            + cards_all()
        )
    elif page_type == 'cards-filter':
        body_html = (
            '<div class="sec-header"><h1>' + title + '</h1>'
            + ('<p>' + desc + '</p>' if desc else '') + '</div>'
            + cards_by_tag(tag)
        )
    else:
        body_html = (
            '<div class="sec-header"><h1>' + title + '</h1>'
            + ('<p>' + desc + '</p>' if desc else '') + '</div>'
            '<div class="md-body">' + md_to_html(raw) + '</div>'
        )
    html = wrap(body_html, '/' + str(dst).replace('site/', ''), title, desc, extra_js)
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
        ("📐","定量药理建模","PBPK · PopPK · PK/PD 建模","/quantitative-pharmacology/index.html"),
        ("💊","临床药理","创新药 · 仿制药 · 特殊人群","/clinical-pharmacology/index.html"),
        ("📚","文章总目录","同行评审 · 公众号解读 · 会议报告","/articles/index.html"),
        ("📋","法规与指南","NMPA · FDA · EMA 指导原则","/regulations/index.html"),
        ("🎓","会议与培训","国内外学术会议与培训资源","/conferences/index.html"),
        ("📖","学习资源","入门 · 进阶 · 实战 · 专家分享","/tutorials/index.html"),
        ("👥","专家名录","国内 · 国际专家动态","/experts/index.html"),
        ("🔧","学术资源","期刊推荐 · 工具软件","/resources/index.html"),
    ]

    sc = []
    for icon, name, d, href in sections:
        sc.append(
            '<div class="hero-card" onclick="location.href=\'' + href + '\'">'
            '<div class="card-icon">' + icon + '</div>'
            '<div class="card-title">' + name + '</div>'
            '<div class="card-sub">' + d + '</div>'
            '<div class="card-footer"><span class="card-arrow">进入 ›</span></div>'
            '</div>'
        )

    arts = get_articles()
    new_arts = [a for a in arts if a['tag'] in ('pbpk','poppk','pkbd','innovative')][:6]
    new_cards = ''.join(render_card(a) for a in new_arts)

    # 统计数字
    total = len(arts)
    stats_html = (
        '<div class="stats-row">'
        '<div class="stat-card"><div class="stat-num">' + str(total) + '+</div><div class="stat-label">已收录文章</div></div>'
        '<div class="stat-card"><div class="stat-num">8</div><div class="stat-label">内容板块</div></div>'
        '<div class="stat-card"><div class="stat-num">周</div><div class="stat-label">更新周期</div></div>'
        '</div>'
    )

    body = (
        '<div class="sec-header"><h1>🏠 ' + title + '</h1><p>' + desc + '</p>'
        '<p class="updated">📅 更新: ' + NOW + ' · 每周五更新</p></div>'
        + stats_html +
        '<h2 class="section-title">📌 内容板块</h2>'
        '<div class="card-grid" style="margin-top:.8rem">'
        + '\n'.join(sc) + '</div>'
        '<h2 class="section-title">📰 本周新增文章</h2>'
        '<div class="card-grid wide">' + new_cards + '</div>'
        '<p class="text-muted" style="margin-top:1.5rem">'
        '系统追踪同行评审论文、专业公众号解读、行业会议报告 · '
        '<a href="/articles/index.html">查看全部 ' + str(total) + ' 篇文章 ›</a></p>'
    )
    html = wrap(body, '/index.html', title, desc)
    with open(DST / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('  ✓ index.html')

# ── 工具软件页（树形+右侧详情面板） ──────────────────────
TOOL_DATA = {
    "simcyp": {
        "name": "SimCYP (Certara)", "badge": "金标准", "badge_color": "#4caf50",
        "desc": "全球监管申报使用最广泛的 PBPK 平台，FDA、EMA、PMDA 均认可。",
        "meta": ["商业软件", "Windows", "学术/商业许可证"],
        "features": [
            "Simcyp Reader：结果阅读器",
            "Population Simulator：虚拟人群模拟",
            "PBPK 吸收模型（IVIVE）",
            "DDI 预测模块",
            "儿科建模工具",
        ],
        "tutorials": [
            ("SimCYP 官方教程", "https://www.certara.com/simcyp/"),
            ("FDA PBPK 指南", "https://www.fda.gov/"),
        ],
        "cases": [
            "华法林种族差异 PBPK 预测（药学学报 2025）",
            "儿科剂量推导——基于生理学参数的年龄分层模型",
        ],
    },
    "gastroplus": {
        "name": "GastroPlus (Simulations Plus)", "badge": "口服吸收", "badge_color": "#ff9800",
        "desc": "专注于口服制剂吸收建模，ACAT 模型覆盖全胃肠道，适用于 BCS/BDDCS 分类预测。",
        "meta": ["商业软件", "Windows", "学术许可证可用"],
        "features": [
            "ACAT 模型：胃肠道吸收完整模型",
            "PBPK 体内相关性（IVIVC）",
            "BCS/BDDCS 分类预测",
            "DDI 模拟模块",
            "生物等效性（BE）预测",
        ],
        "tutorials": [
            ("GastroPlus 官网", "https://www.simulations-plus.com/products/gastroplus/"),
        ],
        "cases": [
            "BCS I 类药物溶解度-渗透性关系建模",
            "控释制剂的胃肠道吸收预测",
        ],
    },
    "pksim": {
        "name": "PK-Sim (Open Systems Pharmacology)", "badge": "开源免费", "badge_color": "#2196f3",
        "desc": "开源 PBPK 工具，可免费用于学术用途，器官级生理模型，与 MoBi 整合进行机制性 PD 建模。",
        "meta": ["开源免费", "Windows/Linux", "学术免费"],
        "features": [
            "器官级生理模型（心输出量分配）",
            "儿科建模工具 BOIV",
            "与 MoBi 整合进行 PK/PD 建模",
            "虚拟人群生成（质控参数库）",
            "IVIVE 模块",
        ],
        "tutorials": [
            ("PK-Sim 官网", "https://www.open-systems-pharmacology.org/"),
            ("OSP 文档", "https://docs.open-systems-pharmacology.org/"),
        ],
        "cases": [
            "基于 PK-Sim 重新定位老药剂量",
            "器官损伤患者的 PK 预测",
        ],
    },
    "mobot": {
        "name": "MoBot (MDIC)", "badge": "社区驱动", "badge_color": "#9c27b0",
        "desc": "基于 PK-Sim 的自动化工作流工具，适合教学和快速探索，社区驱动开发。",
        "meta": ["开源免费", "社区驱动", "教学友好"],
        "features": [
            "基于 PK-Sim 的自动化工作流",
            "图形化操作界面",
            "适合教学和快速探索",
            "开放 API 扩展",
        ],
        "tutorials": [
            ("MoBot GitHub", "https://github.com/moboid"),
        ],
        "cases": [
            "教学案例：阿司匹林 PK 建模入门",
        ],
    },
    "nonmem": {
        "name": "NONMEM", "badge": "金标准", "badge_color": "#4caf50",
        "desc": "金标准 PopPK 软件，监管申报必备，30年工业界积累，大量历史模型可参考。",
        "meta": ["商业软件", "Linux/Unix", "工业标准"],
        "features": [
            "混合效应建模（PopPK/PD）",
            "NONMEM 7+ 版本支持",
            "复杂给药方案设计",
            "监管申报标准格式",
            "与 PsN/Xpose 生态整合",
        ],
        "tutorials": [
            ("ICON plc 官网", "https://www.iconplc.com/solutions/software/nonmem/"),
            ("PsN 工具箱", "https://psnplugin.sourceforge.net/"),
        ],
        "cases": [
            "肿瘤药物 PopPK 模型——支持首次人体试验剂量预测",
        ],
    },
    "monolix": {
        "name": "MONOLIX", "badge": "贝叶斯", "badge_color": "#ff5722",
        "desc": "Lixoft 出品，图形化界面+自动化算法，贝叶斯混合效应建模，学术免费。",
        "meta": ["商业/学术免费", "Windows/Linux/Mac", "贝叶斯方法"],
        "features": [
            "自动化模型选择（SAEM 算法）",
            "贝叶斯估计（MLE/IMSE）",
            "图形化结果展示",
            "实时诊断指标",
            "与 R / Simulx 整合",
        ],
        "tutorials": [
            ("Lixoft MONOLIX", "https://lixoft.com/products/monolix/"),
        ],
        "cases": [
            "基于 MONOLIX 的时间-事件分析（TTE）",
        ],
    },
    "nlmixr2": {
        "name": "nlmixr2 / rxode3", "badge": "开源R", "badge_color": "#2196f3",
        "desc": "R 语言开源 NONMEM 替代方案，基于 rxode3 引擎，支持 ODE 建模，社区活跃。",
        "meta": ["开源免费", "R", "社区驱动"],
        "features": [
            "rxode3 ODE 求解引擎",
            "nlmixr2 混合效应接口",
            "与 tidyverse 生态整合",
            "支持贝叶斯（Stan）桥接",
            "Shiny 图形化界面",
        ],
        "tutorials": [
            ("nlmixr2 GitHub", "https://github.com/nlmixr2/nlmixr2"),
            ("rxode3 文档", "https://nlmixr2.github.io/rxode2/"),
        ],
        "cases": [
            "R 语言 PopPK 建模：从数据到图表",
        ],
    },
}

def build_tools_page():
    """构建工具软件页：左侧树形导航 + 右侧详情面板"""
    # 左侧树
    tree_items = []
    first_id = None
    for i, (tid, t) in enumerate(TOOL_DATA.items()):
        if i == 0: first_id = tid
        tree_items.append(
            '<div class="tree-item" data-tool="' + tid + '" onclick="showTool(\'' + tid + '\')">'
            '<span class="tree-icon">' + ('🔬' if i < 4 else '📊') + '</span>'
            + t['name'] + '</div>'
        )

    # 右侧详情面板
    panels = []
    for tid, t in TOOL_DATA.items():
        features_li = ''.join('<li>' + f + '</li>' for f in t['features'])
        cases_li = ''.join('<li>' + c + '</li>' for c in t['cases'])
        resources = ''.join(
            '<a class="res-link" href="' + r[1] + '" target="_blank" rel="noopener">🔗 ' + r[0] + '</a>'
            for r in t['tutorials']
        )
        panels.append(
            '<div class="tool-detail" id="tool-' + tid + '">'
            '<h2>' + t['name'] + ' <span class="tool-badge" style="background:'
            + ('#e8f5e9;color:#2e7d32' if '金标准' in t['badge'] else
               '#e3f2fd;color:#1565c0' if '免费' in t['badge'] or '开源' in t['badge'] else
               '#fff3e0;color:#e65100') + '">' + t['badge'] + '</span></h2>'
            '<p class="tool-desc">' + t['desc'] + '</p>'
            '<div class="tool-meta">' + ''.join('<span class="meta-chip">'+m+'</span>' for m in t['meta']) + '</div>'
            '<h3>📋 主要功能</h3><ul>' + features_li + '</ul>'
            '<h3>📖 教程资源</h3><div class="resource-links">' + resources + '</div>'
            '<h3>💡 实战案例</h3><ul>' + cases_li + '</ul>'
            '</div>'
        )

    body = (
        '<div class="sec-header"><h1>🔧 工具软件</h1>'
        '<p>覆盖 PBPK、PopPK、PK/PD 建模全流程的工具链。每款工具点击左侧目录查看详情、教程与实战案例。</p>'
        '<p class="updated">⚠️ 软件选型应根据具体项目需求、机构许可和监管要求综合考量</p></div>'
        '<div class="tree-layout">'
        '<div class="tree-nav">'
        '<div class="tree-nav-header">📂 工具分类</div>'
        + '\n'.join(tree_items) +
        '</div>'
        '<div id="tool-detail-container" class="tool-panel">'
        + '\n'.join(panels) +
        '</div></div>'
    )
    extra_js = '<script>initToolPage("' + (first_id or '') + '")</script>'
    html = wrap(body, '/resources/tools.html', '工具软件', '定量药理工具软件全列表', extra_js)
    with open(DST / 'resources' / 'tools.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('  ✓ tools.html (new design)')

# ── 学习资源页（标签切换） ──────────────────────────────
def build_tutorials_page():
    tut_sections = [
        ("introduction", "入门教程", [
            ("PBPK 建模入门：从生理学到数学模型", "📐", [
                "PBPK 基本原理与历史沿革",
                "生理学参数：心输出量、器官体积、血流",
                "Simple tank 模型与分布容积",
                "首个 PBPK 模型的构建（以乙醇为例）",
                "推荐阅读：Jager et al. 2021, CPT",
            ], [
                ("PBPK建模入门（中文）", "#"),
                ("Physiology-based pharmacokinetics - Wikipedia", "https://en.wikipedia.org/wiki/Physiology-based_pharmacokinetics"),
            ]),
            ("PopPK 入门：混合效应模型基础", "📊", [
                "固定效应 vs 随机效应",
                "典型的 PopPK 模型结构：CL, V, KA",
                "NONMEM 数据格式与控制流文件",
                "基础模型诊断：OFV, 残差, ETA shrink",
                "推荐练习：丙泊酚 PopPK 数据集",
            ], [
                ("NONMEM 入门指南", "https://iconpln.com/resources"),
                ("PopPK 公开数据集", "#"),
            ]),
            ("PK/PD 建模入门：链接药物与效应", "💊", [
                "直接效应模型与效应室模型",
                "Emax 模型与 IC50",
                "时间依赖性 PK/PD",
                "肿瘤 Gompertz 模型",
            ], [
                ("PK/PD建模基础（Certara blog）", "https://www.certara.com/blog/"),
            ]),
        ]),
        ("advanced", "进阶教程", [
            ("PBPK 模型验证与敏感性分析", "🔬", [
                "全身 PBPK 模型验证方法",
                "全身与器官水平敏感性分析",
                "参数优化：local/global methods",
                "FDA 儿科 PBPK 指南要点",
                "多药物 DDI 的 PBPK 建模策略",
            ], [
                ("FDA PBPK 指南（2024）", "https://www.fda.gov/"),
                ("PBPK 模型验证清单", "#"),
            ]),
            ("PopPK 进阶：模型优化与仿真", "📈", [
                "协变量筛选：CAT vs VPC",
                "Bootstrap 与 VPC 验证",
                "模型选择：OFV, AIC, 生物学合理性",
                "模拟（Simulation）：剂量调整与场景预测",
                "NCA 与 PopPK 的结合应用",
            ], [
                ("PsN 教程", "https://psnplugin.sourceforge.net/"),
                ("VPC 详解", "#"),
            ]),
            ("实时答疑：常见建模问题汇总", "❓", [
                "收敛失败：参数边界与初始值",
                "ETA shrink 过高的处理",
                "异常观测值（outlier）的识别",
                "模型不稳定：随机效应结构问题",
            ], [
                ("NONMEM 错误代码速查", "#"),
            ]),
        ]),
        ("practice", "实战资源", [
            ("精选数据集与代码仓库", "📦", [
                "PBPK 公开数据集：Certara model repository",
                "PopPK 经典数据集：丙泊酚、咖啡因、咪达唑仑",
                "PK-Sim 公开模型库",
                "R/Python 建模脚本分享（GitHub 仓库）",
            ], [
                ("Certara Model Repository", "https://www.certara.com/"),
                ("Open Systems Pharmacology models", "https://www.open-systems-pharmacology.org/"),
                ("GitHub: quantitative-pharma", "#"),
            ]),
            ("认证课程与工作坊", "🎓", [
                "Certara SimCYP 认证培训（线上/线下）",
                "FDA 定量药理 workshops",
                "ASCPT 年会 Short Course",
                "国内：CDE 定量药理培训班",
            ], [
                ("Certara Education", "https://www.certara.com/"),
                ("ASCPT Annual Meeting", "https://www.ascpt.org/"),
            ]),
            ("监管申报案例库", "📁", [
                "FDA NDA 中 PBPK 章节示例",
                "EMA CHMP PopPK 审评意见（公开发表）",
                "CDE 指导原则配套案例",
            ], [
                ("FDA Drug Approval Reports", "https://www.accessdata.fda.gov/"),
            ]),
        ]),
        ("expert", "专家分享", [
            ("国际专家访谈与观点", "🌍", [
                "Prof. Masoud Jamei (SimCYP 核心开发者) — 儿科 PBPK 建模展望",
                "Prof. Peru T. 论文合著 — PopPK 在肿瘤中的十年应用",
                "Prof. Wang L. — 中国定量药理发展现状与挑战",
                "Dr. Zhang M. — 从工业界到监管的转型路径",
            ], []),
            ("国内专家观点", "🇨🇳", [
                "定量药理专委会（CSPT）专家共识",
                "CDE 审评专家系列讲座笔记",
                "临床药理杂志专家约稿",
                "药学学报定量药理专栏作者",
            ], []),
            ("行业趋势与展望", "🔭", [
                "AI + 定量药理：大型语言模型辅助模型构建",
                "真实世界数据（RWD）与 PopPK 的融合",
                "定量药理在细胞与基因疗法中的应用前景",
                "监管科学推动下的 MIDD 未来",
            ], [
                ("MIDD 未来展望（NEJM 2024）", "#"),
            ]),
        ]),
    ]

    tabs_html = ''.join(
        '<div class="tut-tab' + (' active' if i == 0 else '') + '" data-tut="' + t[0] + '" onclick="switchTutorial(\'' + t[0] + '\')">' + t[1] + '</div>'
        for i, t in enumerate(tut_sections)
    )

    contents_html = ''
    for i, (tid, title, items) in enumerate(tut_sections):
        cards_html = ''
        for item_title, icon, bullets, links in items:
            links_html = ''.join(
                '<a class="res-link" href="' + l[1] + '" target="_blank" rel="noopener">🔗 ' + l[0] + '</a>'
                for l in links
            )
            bullets_html = ''.join('<li>' + b + '</li>' for b in bullets)
            cards_html += (
                '<div class="article-card" style="margin-bottom:.8rem">'
                '<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem">'
                '<span style="font-size:1.3rem">' + icon + '</span>'
                '<div class="card-title" style="font-size:.95rem">' + item_title + '</div></div>'
                '<ul style="margin-left:1.2rem;font-size:.8rem;color:#5a6178;line-height:1.9">' + bullets_html + '</ul>'
                + ('<div class="resource-links" style="margin-top:.6rem">' + links_html + '</div>' if links_html else '')
                + '</div>'
            )
        contents_html += (
            '<div id="tut-' + tid + '" class="tut-content' + (' active' if i == 0 else '') + '">'
            + cards_html + '</div>'
        )

    body = (
        '<div class="sec-header"><h1>📖 学习资源</h1>'
        '<p>从入门到进阶，从实战到专家分享，系统化学习路径助力从业者一站式成长。</p>'
        '<p class="updated">内容持续更新，欢迎推荐优质资源</p></div>'
        '<div class="tutorial-tabs">' + tabs_html + '</div>'
        + contents_html
    )
    html = wrap(body, '/tutorials/index.html', '学习资源', '定量药理学习资源与教程')
    (DST / 'tutorials').mkdir(parents=True, exist_ok=True)
    with open(DST / 'tutorials' / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('  ✓ tutorials/index.html')

# ── main ─────────────────────────────────────────────────
# ── 期刊推荐页（卡片分组布局） ──────────────────────────
JOURNAL_CATEGORIES = [
    {
        "label": "🌐 国际顶级期刊",
        "color": "#4caf50",
        "items": [
            {"name": "Clinical Pharmacology & Therapeutics (CPT)", "if_": "~7.0",
             "desc": "临床药理旗舰期刊，监管认可度最高，FDA/EMA 申报常引用"},
            {"name": "Clinical Pharmacokinetics", "if_": "~5.5",
             "desc": "PK/PD 经典期刊，理论与应用并重"},
            {"name": "Drug Metabolism and Disposition", "if_": "~3.8",
             "desc": "代谢与转运体定量研究首选"},
            {"name": "Pharmaceutical Research", "if_": "~4.4",
             "desc": "药剂学与建模方法综合期刊"},
            {"name": "Journal of Clinical Pharmacology", "if_": "~3.0",
             "desc": "临床药理综合，含大量 PopPK 建模文章"},
        ]
    },
    {
        "label": "📊 定量药理专刊",
        "color": "#2196f3",
        "items": [
            {"name": "CPT: Pharmacometrics & Systems Pharmacology", "if_": "~3.5",
             "desc": "PopPK/PD 建模专刊，NONMEM 方法论文章集中"},
            {"name": "Journal of Pharmacokinetics & Pharmacodynamics", "if_": "~2.5",
             "desc": "PK/PD 理论与建模方法学"},
        ]
    },
    {
        "label": "🇨🇳 中文核心期刊",
        "color": "#ff9800",
        "items": [
            {"name": "药学学报", "if_": "中文核心",
             "desc": "药物代谢与定量研究权威，PBPK 建模文章多"},
            {"name": "中国临床药理学杂志", "if_": "中文核心",
             "desc": "BE/PopPK 研究首选，含大量国内临床药理数据"},
            {"name": "中国新药杂志", "if_": "中文核心",
             "desc": "新药研发综合期刊，定量药理与临床研究并重"},
            {"name": "药物流行病学", "if_": "中文核心",
             "desc": "真实世界研究与药物流行病学"},
        ]
    },
    {
        "label": "🔍 检索与管理工具",
        "color": "#9c27b0",
        "items": [
            {"name": "PubMed", "if_": "—",
             "desc": "最全生物医学文献库，支持 PMID 直接跳转"},
            {"name": "Embase", "if_": "—",
             "desc": "药物文献覆盖最广，DDI 相关研究首选"},
            {"name": "Scopus", "if_": "—",
             "desc": "综合引文分析工具"},
            {"name": "Zotero", "if_": "免费",
             "desc": "免费开源文献管理，PDF 管理与引文生成"},
            {"name": "EndNote", "if_": "机构版",
             "desc": "机构授权，Word/LaTeX 集成最强"},
        ]
    },
]

def build_journals_page():
    cats = []
    for cat in JOURNAL_CATEGORIES:
        cards = []
        for item in cat["items"]:
            cards.append(
                '<div class="article-card" style="cursor:default">'
                '<div class="card-meta">'
                '<span class="card-status" style="background:linear-gradient(135deg,' + cat["color"] + '22,' + cat["color"] + '44);color:' + cat["color"] + '">' + item["if_"] + '</span>'
                '</div>'
                '<div class="card-title" style="font-size:.9rem">' + item["name"] + '</div>'
                '<div class="card-summary">' + item["desc"] + '</div>'
                '</div>'
            )
        cats.append(
            '<div style="margin-bottom:2rem">'
            '<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.8rem;padding-bottom:.5rem;border-bottom:2px solid ' + cat["color"] + '">'
            '<span style="font-size:.85rem;font-weight:700;color:' + cat["color"] + '">' + cat["label"] + '</span>'
            '</div>'
            '<div class="card-grid">' + ''.join(cards) + '</div>'
            '</div>'
        )
    body = (
        '<div class="sec-header"><h1>📚 期刊推荐</h1>'
        '<p>精选定量药理与临床药理领域核心期刊，标注影响因子与收录定位，助你快速定位目标读物。</p>'
        '<p class="updated">IF 数据来源：Journal Citation Reports 2024 / 中文核心期刊要目 2023</p></div>'
        + ''.join(cats) +
        '<blockquote>期刊选择建议：根据研究内容选择匹配期刊，优先考虑同行评审速度和接收率。中文期刊需关注「北大核心」与「科技核心」目录。</blockquote>'
    )
    html = wrap(body, '/resources/journals.html', '期刊推荐', '定量药理与临床药理核心期刊推荐')
    (DST / 'resources').mkdir(parents=True, exist_ok=True)
    with open(DST / 'resources' / 'journals.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('  ✓ journals.html (card layout)')

# ── 会议与培训页（卡片+表格布局） ───────────────────────
CONF_DOMESTIC = [
    {"name": "全国临床药理学学术年会", "time": "每年10月", "loc": "轮流举办",
     "desc": "中华医学会临床药理学分会主办，定量药理专题会场，论文报告与操作培训"},
    {"name": "中国定量药理学大会", "time": "每年7月", "loc": "轮流举办",
     "desc": "国内定量药理领域最专业会议，PBPK/PopPK/PKPD 建模技术研讨与案例分析"},
    {"name": "DIA中国年会", "time": "每年5月", "loc": "北京/上海",
     "desc": "药物研发全链条会议，设有定量药理分会场，国际与国内专家参与"},
    {"name": "北京大学临床药理年会", "time": "每年6月", "loc": "北京",
     "desc": "聚焦临床药理研究方法、监管要求与案例分析，附实际操作工作坊"},
    {"name": "药学学术年会（临床药理分场）", "time": "每年8-9月", "loc": "轮流举办",
     "desc": "中国药学会主办，临床药理与定量药理研究进展报告"},
]
CONF_INTL = [
    {"name": "ASCPT Annual Meeting", "time": "每年3月", "loc": "美国",
     "desc": "临床药理与定量药理领域顶级会议，年度最佳论文颁奖，PBPK/PopPK 分会"},
    {"name": "PAGE (Population Approach Group)", "time": "每年6月", "loc": "欧洲",
     "desc": "PopPK/PD 建模方法学专题，工作坊与论文报告，方法学论文金标准"},
    {"name": "ACoP (American Conference on Pharmacometrics)", "time": "每年10月", "loc": "美国",
     "desc": "定量药理建模与仿真，药物研发中的应用案例，工业界参与度高"},
    {"name": "ACCP Global Conference", "time": "每年10月", "loc": "轮流",
     "desc": "全球临床药理教育、研究与实践进展"},
    {"name": "AAPS (American Association of Pharmaceutical Scientists)", "time": "每年11月", "loc": "美国",
     "desc": "药物科学主流会议，含 PK/PD 与定量药理方向"},
]
CONF_TRAIN = [
    {"name": "NMPA/CDE 指导原则培训视频", "time": "随时", "loc": "CDE官网",
     "desc": "定量药理相关指导原则官方解读视频，含案例说明"},
    {"name": "FDA MIDD案例库", "time": "随时", "loc": "FDA Website",
     "desc": "MIDD 试点案例视频讲解，监管视角案例分析"},
    {"name": "PAGE Meeting Recordings", "time": "随时", "loc": "PAGE官网",
     "desc": "历年 PAGE 会议报告录像，含方法学与应用案例"},
    {"name": "Certara Academy", "time": "随到随学", "loc": "Certara",
     "desc": "GastroPlus、NONMEM 官方在线培训，证书认证"},
    {"name": "University of Pittsburgh PopPK Course", "time": "Coursera", "loc": "公开课",
     "desc": "PopPK 基础与进阶课程，英文授课配字幕"},
]
UPCOMING = [
    {"name": "ASCPT 2025", "time": "2025-03-18~21", "loc": "美国 奥斯汀"},
    {"name": "PAGE 2025", "time": "2025-06", "loc": "荷兰 阿姆斯特丹"},
    {"name": "ACoP 2025", "time": "2025-10", "loc": "美国"},
    {"name": "全国临床药理学学术年会 2025", "time": "2025-10（预计）", "loc": "待定"},
    {"name": "中国定量药理学大会 2025", "time": "2025-07（预计）", "loc": "待定"},
]

def _conf_table(items, color):
    rows = []
    for it in items:
        rows.append(
            '<tr><td style="font-weight:600;color:var(--text)">' + it["name"] + '</td>'
            '<td style="color:' + color + ';font-weight:600">' + it["time"] + '</td>'
            '<td style="color:var(--muted)">' + it["loc"] + '</td>'
            '<td style="font-size:.8rem;color:#5a6178">' + it["desc"] + '</td></tr>'
        )
    return ('<div class="table-wrap"><table><thead><tr><th>会议名称</th><th>时间</th><th>地点</th><th>主要内容</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>')

def build_conferences_page():
    upcoming = ''.join(
        '<div class="article-card" style="border-left:3px solid #4caf50">'
        '<div class="card-meta"><span class="card-status s-new">近期</span></div>'
        '<div class="card-title">' + e["name"] + '</div>'
        '<div class="card-summary">📅 ' + e["time"] + ' · 📍 ' + e["loc"] + '</div>'
        '</div>'
        for e in UPCOMING
    )
    body = (
        '<div class="sec-header"><h1>🎓 会议与培训</h1>'
        '<p>精选国内外临床药理与定量药理领域学术会议及在线培训资源，支持职业持续教育。</p>'
        '<p class="updated">会议时间仅供参考，以官方发布为准；建议提前6个月关注注册信息</p></div>'
        '<h2 class="section-title">📅 近期会议预告 (2025)</h2>'
        '<div class="card-grid" style="margin-bottom:2rem">' + upcoming + '</div>'
        '<div style="margin-bottom:2rem">'
        '<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.8rem;padding-bottom:.5rem;border-bottom:2px solid #e53935">'
        '<span style="font-size:.85rem;font-weight:700;color:#e53935">🇨🇳 国内会议</span></div>'
        + _conf_table(CONF_DOMESTIC, "#e53935") + '</div>'
        '<div style="margin-bottom:2rem">'
        '<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.8rem;padding-bottom:.5rem;border-bottom:2px solid #1565c0">'
        '<span style="font-size:.85rem;font-weight:700;color:#1565c0">🌐 国际会议</span></div>'
        + _conf_table(CONF_INTL, "#1565c0") + '</div>'
        '<div style="margin-bottom:2rem">'
        '<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.8rem;padding-bottom:.5rem;border-bottom:2px solid #2e7d32">'
        '<span style="font-size:.85rem;font-weight:700;color:#2e7d32">📚 在线培训资源</span></div>'
        + _conf_table(CONF_TRAIN, "#2e7d32") + '</div>'
    )
    html = wrap(body, '/conferences/index.html', '会议与培训', '定量药理与临床药理学术会议与培训资源')
    (DST / 'conferences').mkdir(parents=True, exist_ok=True)
    with open(DST / 'conferences' / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('  ✓ conferences/index.html (card+table layout)')


def main():
    print('\n=== Building site: docs/ → site/ (v2) ===\n')
    DST.mkdir(exist_ok=True)

    build_home()
    build_tools_page()
    build_tutorials_page()
    build_journals_page()
    build_conferences_page()

    n = 0
    for md_file in SRC.rglob('*.md'):
        rel = md_file.relative_to(SRC)
        if rel.parts[0] in ('.', 'stylesheets'):
            continue
        if rel.name == 'index.md' and len(rel.parts) == 1:
            continue
        # Skip pages with custom builders
        _ps = str(rel).replace('\\', '/')
        if _ps.startswith('tutorials/') or _ps.replace('.md','') in ('conferences/index', 'resources/journals'):
            continue
        dst_file = DST / rel.with_suffix('.html')
        path_str = str(rel).replace('\\', '/').replace('.md', '')

        if path_str == 'articles/index.md':
            build_page(md_file, dst_file, page_type='cards-all')
            n += 1; continue
        if path_str == 'resources/tools':
            n += 1; continue  # 已单独构建
        if path_str == 'tutorials/index':
            n += 1; continue  # 已单独构建

        tag = None
        for _t, _pf in TAG_TO_PAGE.items():
            _src = _pf.rsplit('.html', 1)[0].lstrip('/')
            if path_str == _src:
                tag = _t; break
        if tag:
            build_page(md_file, dst_file, page_type='cards-filter', tag=tag)
        else:
            build_page(md_file, dst_file, page_type='md')
        n += 1

    print('\n✓ Done:', n, 'content pages')

    css_src = SRC / 'stylesheets' / 'extra.css'
    if css_src.exists():
        css_dst = DST / 'stylesheets' / 'extra.css'
        css_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(css_src, css_dst)


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
if __name__ == '__main__':
    main()
