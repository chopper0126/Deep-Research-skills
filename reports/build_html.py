#!/usr/bin/env python3
"""Convert the A-share deep research markdown report to a styled HTML page."""

import re
import html as html_mod
from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

# ---------------------------------------------------------------------------
# Custom extension: capture ```mermaid blocks so they survive markdown parsing
# ---------------------------------------------------------------------------
class MermaidPreprocessor(Preprocessor):
    """Lift ```mermaid blocks out of the markdown stream so they are not
    treated as regular code blocks.  Re-insert them after HTML conversion."""
    def __init__(self):
        self.blocks = {}

    def run(self, lines):
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Detect start of a fenced mermaid block
            m = re.match(r'^```mermaid\s*$', line)
            if m:
                buf = []
                i += 1
                while i < len(lines) and not re.match(r'^```\s*$', lines[i]):
                    buf.append(lines[i])
                    i += 1
                i += 1  # skip closing ```
                placeholder = f'<!--MERMAID_PLACEHOLDER_{len(self.blocks)}-->'
                self.blocks[placeholder] = '\n'.join(buf)
                out.append(placeholder)
            else:
                out.append(line)
                i += 1
        return out


class MermaidExtension(Extension):
    def extendMarkdown(self, md):
        pp = MermaidPreprocessor()
        md.preprocessors.register(pp, 'mermaid', 25)
        md.mermaid_blocks = pp.blocks  # attach for later use


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------
HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>中国A股发展历程与底层逻辑 —— 深度调研报告</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    themeVariables: {
      fontFamily: '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif'
    }
  });
</script>
<style>
  /* ============================================================
     CSS Custom Properties (light theme)
     ============================================================ */
  :root {
    --bg: #fafbfc;
    --bg-sidebar: #1a1a2e;
    --bg-content: #ffffff;
    --text: #2d3436;
    --text-muted: #636e72;
    --text-sidebar: #cdd6f4;
    --text-sidebar-hover: #ffffff;
    --heading: #1a1a2e;
    --border: #e0e0e0;
    --accent: #1a56db;
    --accent-light: #e8f0fe;
    --table-stripe: #f8f9fa;
    --table-header-bg: #1a1a2e;
    --table-header-text: #ffffff;
    --blockquote-bg: #f0f7ff;
    --blockquote-border: #1a56db;
    --code-bg: #f4f4f5;
    --code-text: #2d3436;
    --mermaid-bg: #fafbfc;
    --warn-bg: #fff8e1;
    --warn-border: #f9a825;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
    --radius: 8px;
    --sidebar-width: 280px;
  }

  /* ============================================================
     Reset & Base
     ============================================================ */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; font-size: 16px; }
  body {
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.75;
    display: flex;
    min-height: 100vh;
  }

  /* ============================================================
     Sidebar Navigation
     ============================================================ */
  nav#toc {
    position: fixed; top: 0; left: 0; bottom: 0;
    width: var(--sidebar-width);
    background: var(--bg-sidebar);
    color: var(--text-sidebar);
    overflow-y: auto;
    padding: 24px 20px;
    z-index: 100;
    box-shadow: 2px 0 16px rgba(0,0,0,0.15);
  }
  nav#toc h2 {
    font-size: 1.05rem;
    color: #fff;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    letter-spacing: 0.04em;
  }
  nav#toc a {
    display: block;
    color: var(--text-sidebar);
    text-decoration: none;
    padding: 5px 0;
    font-size: 0.85rem;
    transition: color 0.15s;
    line-height: 1.5;
  }
  nav#toc a:hover,
  nav#toc a.active {
    color: var(--text-sidebar-hover);
  }
  nav#toc a.toc-h2 { font-weight: 600; margin-top: 8px; }
  nav#toc a.toc-h3 { padding-left: 16px; font-size: 0.8rem; }
  nav#toc a.toc-h4 { padding-left: 32px; font-size: 0.76rem; color: #a0a8c0; }

  /* ============================================================
     Main Content Area
     ============================================================ */
  main {
    margin-left: var(--sidebar-width);
    max-width: 960px;
    width: 100%;
    padding: 48px 56px 80px;
    background: var(--bg-content);
    min-height: 100vh;
    box-shadow: var(--shadow-md);
  }

  /* ============================================================
     Typography
     ============================================================ */
  h1 { font-size: 2rem; margin: 0 0 8px; color: var(--heading); font-weight: 800; letter-spacing: 0.02em; }
  h2 { font-size: 1.5rem; margin: 48px 0 16px; padding-bottom: 8px; border-bottom: 2px solid var(--accent); color: var(--heading); font-weight: 700; }
  h3 { font-size: 1.2rem; margin: 32px 0 12px; color: var(--heading); font-weight: 700; }
  h4 { font-size: 1.05rem; margin: 24px 0 8px; color: var(--heading); font-weight: 600; }
  h5 { font-size: 0.95rem; margin: 16px 0 6px; color: var(--text-muted); font-weight: 600; }
  p { margin: 10px 0; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  strong { color: var(--heading); }
  hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }

  /* ============================================================
     Blockquote
     ============================================================ */
  blockquote {
    background: var(--blockquote-bg);
    border-left: 4px solid var(--blockquote-border);
    margin: 16px 0;
    padding: 12px 18px;
    border-radius: 0 var(--radius) var(--radius) 0;
    color: #4a5568;
  }
  blockquote p { margin: 4px 0; }
  blockquote strong { color: var(--accent); }

  /* ============================================================
     Tables
     ============================================================ */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0 24px;
    font-size: 0.88rem;
    box-shadow: var(--shadow-sm);
    border-radius: var(--radius);
    overflow: hidden;
  }
  thead { background: var(--table-header-bg); color: var(--table-header-text); }
  th {
    padding: 11px 14px;
    text-align: left;
    font-weight: 600;
    white-space: nowrap;
  }
  td {
    padding: 9px 14px;
    border-bottom: 1px solid var(--border);
  }
  tbody tr:nth-child(even) { background: var(--table-stripe); }
  tbody tr:hover { background: var(--accent-light); }

  /* ============================================================
     Code and Pre
     ============================================================ */
  code {
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace;
    font-size: 0.85em;
    background: var(--code-bg);
    padding: 2px 6px;
    border-radius: 3px;
    color: var(--code-text);
  }
  pre {
    background: var(--code-bg);
    padding: 16px 20px;
    border-radius: var(--radius);
    overflow-x: auto;
    margin: 12px 0;
    font-size: 0.82rem;
    line-height: 1.5;
    border: 1px solid var(--border);
  }
  pre code { background: none; padding: 0; }

  /* Mermaid diagrams */
  pre.mermaid {
    background: var(--mermaid-bg);
    border: 1px dashed var(--border);
    padding: 20px;
    text-align: center;
    overflow-x: auto;
  }

  /* ============================================================
     Lists
     ============================================================ */
  ul, ol { margin: 8px 0 8px 20px; }
  li { margin: 3px 0; }
  ul ul, ol ol, ul ol, ol ul { margin: 4px 0 4px 16px; }

  /* ============================================================
     Images (SVG rendered by mermaid)
     ============================================================ */
  main svg { max-width: 100%; height: auto; }

  /* ============================================================
     Warning / disclaimer callouts
     ============================================================ */
  .warn {
    background: var(--warn-bg);
    border-left: 4px solid var(--warn-border);
    padding: 12px 18px;
    margin: 20px 0;
    border-radius: 0 var(--radius) var(--radius) 0;
    font-size: 0.9rem;
  }

  /* ============================================================
     Responsive
     ============================================================ */
  @media (max-width: 900px) {
    nav#toc { display: none; }
    main { margin-left: 0; padding: 24px 20px; }
    table { font-size: 0.78rem; }
    th, td { padding: 6px 8px; }
    h1 { font-size: 1.5rem; }
    h2 { font-size: 1.25rem; }
  }

  /* ============================================================
     Print
     ============================================================ */
  @media print {
    nav#toc { display: none; }
    main { margin-left: 0; max-width: 100%; padding: 20px; box-shadow: none; }
    pre.mermaid { break-inside: avoid; }
    table { break-inside: avoid; }
    h2 { break-before: page; }
  }
</style>
</head>
<body>

<nav id="toc">
  <h2>📋 目录导航</h2>
  <!--TOC-->
</nav>

<main>
<!--CONTENT-->
</main>

<script>
  // Simple scroll-spy for TOC
  (function() {
    const nav = document.getElementById('toc');
    const links = nav.querySelectorAll('a');
    const sections = [];
    links.forEach(a => {
      const href = a.getAttribute('href');
      if (href && href.startsWith('#')) {
        const el = document.getElementById(href.slice(1));
        if (el) sections.push({ el, a });
      }
    });
    window.addEventListener('scroll', function() {
      let current = '';
      sections.forEach(s => {
        const top = s.el.getBoundingClientRect().top;
        if (top < 120) current = s.a.getAttribute('href');
      });
      links.forEach(a => a.classList.remove('active'));
      if (current) {
        const active = nav.querySelector('a[href="' + current + '"]');
        if (active) active.classList.add('active');
      }
    });
  })();
</script>

</body>
</html>'''


# ---------------------------------------------------------------------------
# Main conversion
# ---------------------------------------------------------------------------
def build_toc(html_body: str) -> str:
    """Extract headings from HTML and build a nested TOC."""
    heading_re = re.compile(r'<h([234])\s+id="([^"]+)"[^>]*>(.*?)</h\1>', re.DOTALL)
    items = []
    for m in heading_re.finditer(html_body):
        level = int(m.group(1))
        anchor = m.group(2)
        # Strip any inner HTML tags for the TOC text
        text = re.sub(r'<[^>]+>', '', m.group(3))
        items.append((level, anchor, text))

    if not items:
        return ''

    lines = []
    for level, anchor, text in items:
        cls = f'toc-h{level}'
        lines.append(f'    <a class="{cls}" href="#{anchor}">{text}</a>')

    return '\n'.join(lines)


def slugify(text: str) -> str:
    """Generate a URL-friendly slug from heading text."""
    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Keep Chinese characters, alphanumeric, spaces
    text = re.sub(r'[^\w\s一-鿿-]', '', text)
    text = text.strip().lower()
    text = re.sub(r'\s+', '-', text)
    return text


def add_heading_ids(html_body: str) -> str:
    """Add id attributes to h2/h3/h4 headings."""
    def replacer(m):
        tag = m.group(1)
        content = m.group(2)
        sid = slugify(content)
        return f'<{tag} id="{sid}">{content}</{tag}>'
    return re.sub(r'<h([234])>(.*?)</h\1>', replacer, html_body, flags=re.DOTALL)


def convert_md_to_html(md_text: str) -> str:
    # Step 1: Extract mermaid blocks manually before markdown conversion
    mermaid_blocks = {}
    lines = md_text.split('\n')
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^```mermaid\s*$', line)
        if m:
            buf = []
            i += 1
            while i < len(lines) and not re.match(r'^```\s*$', lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            placeholder = f'<!--MERMAID_PLACEHOLDER_{len(mermaid_blocks)}-->'
            mermaid_blocks[placeholder] = '\n'.join(buf)
            out_lines.append(placeholder)
        else:
            out_lines.append(line)
            i += 1
    preprocessed_md = '\n'.join(out_lines)

    # Step 2: Convert markdown to HTML
    md = Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html_body = md.convert(preprocessed_md)

    # Step 3: Restore mermaid blocks (placeholder → <pre class="mermaid">)
    for placeholder, mermaid_src in mermaid_blocks.items():
        escaped = html_mod.escape(mermaid_src)
        # The placeholder might be wrapped in <p> tags by markdown parser
        html_body = html_body.replace(
            f'<p>{placeholder}</p>',
            f'<pre class="mermaid">{escaped}</pre>'
        )
        html_body = html_body.replace(
            placeholder,
            f'<pre class="mermaid">{escaped}</pre>'
        )

    # Step 4: Add heading IDs
    html_body = add_heading_ids(html_body)

    return html_body


def main():
    md_path = '/home/yxj/deep-research-skills/reports/A股发展历程与底层逻辑深度调研报告.md'
    html_path = '/home/yxj/deep-research-skills/reports/A股发展历程与底层逻辑深度调研报告.html'

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    html_body = convert_md_to_html(md_text)
    toc_html = build_toc(html_body)

    final_html = HTML_TEMPLATE.replace('<!--CONTENT-->', html_body)
    final_html = final_html.replace('<!--TOC-->', toc_html)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f'HTML report written to: {html_path}')
    print(f'Size: {len(final_html):,} bytes')


if __name__ == '__main__':
    main()
