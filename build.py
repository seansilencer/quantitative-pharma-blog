#!/usr/bin/env python3
"""
纯 Python 静态博客生成器 - 零依赖版本
把 docs/ 下的 Markdown 文件递归渲染为 HTML 输出到 site/
"""
import re
import os
from pathlib import Path

SRC = Path("docs")
DST = Path("site")
DST.mkdir(exist_ok=True)

NAV = """
<nav>
  <a href="index.html">首页</a> ·
  <a href="quantitative-pharmacology/index.html">定量药理</a> ·
  <a href="clinical-pharmacology/index.html">临床药理</a> ·
  <a href="regulations/index.html">法规</a> ·
  <a href="conferences/index.html">会议</a> ·
  <a href="experts/index.html">专家</a> ·
  <a href="resources/index.html">资源</a>
</nav>
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root{{color-scheme:light;--bg:#fafafa;--fg:#1a1a2e;--accent:#5c6bc0;--link:#5c6bc0;--muted:#666;--border:#e0e0e0}}
    @media(prefers-color-scheme:dark){{:root{{--bg:#1a1a2e;--fg:#e0e0e0;--accent:#9fa8da;--link:#9fa8da;--muted:#999;--border:#333}}}}
   *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--fg);line-height:1.7;max-width:860px;margin:0 auto;padding:2rem 1rem}}
    a{{color:var(--link);text-decoration:none}}
    a:hover{{text-decoration:underline}}
    h1,h2,h3{{margin:1.5rem 0 .75rem;font-weight:600;line-height:1.3}}
    h1{{font-size:1.8rem;border-bottom:2px solid var(--accent);padding-bottom:.4rem}}
    h2{{font-size:1.4rem;border-bottom:1px solid var(--border);padding-bottom:.25rem}}
    h3{{font-size:1.15rem}}
    p{{margin:.6rem 0}}
    ul,ol{{margin:.6rem 0;padding-left:1.5rem}}
    li{{margin:.3rem 0}}
    blockquote{{margin:1rem 0;padding:.6rem 1rem;border-left:4px solid var(--accent);background:rgba(92,107,192,.06)}}
    table{{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.9rem}}
    th,td{{padding:.5rem .75rem;border:1px solid var(--border);text-align:left}}
    th{{background:var(--accent);color:#fff;font-weight:600}}
    tr:nth-child(even){{background:rgba(0,0,0,.03)}}
    @media(prefers-color-scheme:dark){{tr:nth-child(even){{background:rgba(255,255,255,.04)}}}}
    code{{background:rgba(0,0,0,.07);padding:.15rem .35rem;border-radius:3px;font-size:.88em}}
    pre{{background:#f4f4f4;padding:1rem;overflow-x:auto;border-radius:6px;margin:1rem 0}}
    @media(prefers-color-scheme:dark){{pre{{background:#111}}}}
    pre code{{background:none;padding:0}}
    hr{{border:none;border-top:1px solid var(--border);margin:2rem 0}}
    header{{margin-bottom:2rem;padding-bottom:1rem;border-bottom:1px solid var(--border)}}
    header span{{color:var(--muted);font-size:.85rem}}
    footer{{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--border);color:var(--muted);font-size:.85rem;text-align:center}}
    .hero{{background:linear-gradient(135deg,#5c6bc0,#3949ab);color:#fff;padding:2rem;border-radius:8px;margin-bottom:2rem;text-align:center}}
    .hero h1{{color:#fff;border:none;margin:0}}
    .hero p{{opacity:.9;margin-top:.5rem}}
    .tag{{display:inline-block;background:var(--accent);color:#fff;padding:.1rem .5rem;border-radius:99px;font-size:.75rem;margin:.2rem}}
    nav{{margin-bottom:2rem;font-size:.9rem}}
    nav a{{margin-right:.5rem}}
    .updated{{color:var(--muted);font-size:.8rem;margin-top:2rem}}
  </style>
</head>
<body>
  <header>{nav}</header>
  <main>{content}</main>
  <footer>© 2025 定量药理与临床药理前沿追踪 · 内容版权归属原作者 · <a href="https://github.com/seansilencer/quantitative-pharma-blog">GitHub</a></footer>
</body>
</html>"""


def md_to_html(text):
    """把 Markdown 转成 HTML（简化实现，够用即可）"""
    # 代码块
    text = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', text, flags=re.DOTALL)
    # 行内代码
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # 标题（h1~h3）
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    # 引用块
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    # 水平线
    text = re.sub(r'^---+$', '<hr>', text, flags=re.MULTILINE)
    # 表格（简化）
    lines = text.split('\n')
    result = []
    i = 0
    in_table = False
    while i < len(lines):
        line = lines[i]
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                result.append('<table>')
                in_table = True
            row_cells = [c.strip() for c in line.strip().strip('|').split('|')]
            tag = 'th' if any('-' in c for c in row_cells) else ('th' if in_table and 'th' not in locals() else 'td')
            # header row 检测
            if all(re.match(r'^[-:]+$', c.strip()) for c in row_cells):
                i += 1
                continue
            result.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in row_cells if c) + '</tr>')
        else:
            if in_table:
                result.append('</table>')
                in_table = False
            result.append(line)
        i += 1
    if in_table:
        result.append('</table>')
    text = '\n'.join(result)
    # 段落（双换行分隔）
    text = re.sub(r'\n\n+', '\n\n', text)
    paragraphs = []
    for block in re.split(r'\n\n+', text):
        block = block.strip()
        if not block:
            continue
        if block.startswith('<h') or block.startswith('<pre') or block.startswith('<blockquote') or block.startswith('<table') or block.startswith('<ul') or block.startswith('<ol') or block.startswith('<hr'):
            paragraphs.append(block)
        else:
            # 把单行转成 <p>，保留换行
            block = block.replace('\n', '<br>')
            paragraphs.append(f'<p>{block}</p>')
    return '\n'.join(paragraphs)


def extract_title(md):
    m = re.search(r'^# (.+)$', md, re.MULTILINE)
    return m.group(1) if m else '无标题'


def process_file(src_path, dst_path):
    with open(src_path, encoding='utf-8') as f:
        md = f.read()
    html_body = md_to_html(md)
    title = extract_title(md)
    html = TEMPLATE.format(title=title, content=html_body, nav=NAV)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  {src_path} → {dst_path}")


def main():
    print(f"Building site: {SRC} → {DST}")
    count = 0
    for md_file in SRC.rglob('*.md'):
        rel = md_file.relative_to(SRC)
        # 跳过隐藏/样式文件
        if any(p.startswith('.') or p == 'extra.css' for p in rel.parts):
            continue
        html_rel = rel.with_suffix('.html')
        dst_file = DST / html_rel
        process_file(md_file, dst_file)
        count += 1
    print(f"Done: {count} pages generated")
    # 生成 index.html（根目录）
    src_index = SRC / 'index.md'
    if src_index.exists():
        process_file(src_index, DST / 'index.html')
    # 复制 docs/stylesheets 到 site/
    css_src = SRC / 'stylesheets' / 'extra.css'
    if css_src.exists():
        import shutil
        css_dst = DST / 'stylesheets' / 'extra.css'
        css_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(css_src, css_dst)

if __name__ == '__main__':
    main()