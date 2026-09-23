#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""极简 Markdown → 自包含 HTML(零依赖,支持标题/表格/列表/引用/粗体/行内代码/链接/hr)。
用法: python3 md2html.py <input.md> <output.html> "<标题>"
"""
import sys, io, html, re


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def convert(md):
    out, i, lines = [], 0, md.split("\n")
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            head = [c.strip() for c in s.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>")
            for r in rows:
                cells = "".join(
                    '<td data-label="%s">%s</td>' % (html.escape(head[k] if k < len(head) else "", quote=True), inline(c))
                    for k, c in enumerate(r))
                out.append("<tr>" + cells + "</tr>")
            out.append("</tbody></table>")
            continue

        if re.match(r"^#{1,6}\s", s):
            n = len(s) - len(s.lstrip("#"))
            out.append(f"<h{n}>{inline(s[n:].strip())}</h{n}>")
        elif s in ("---", "***", "___"):
            out.append("<hr>")
        elif s.startswith(">"):
            out.append(f"<blockquote>{inline(s.lstrip('> ').strip())}</blockquote>")
        elif re.match(r"^[-*]\s+", s):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif re.match(r"^\d+\.\s+", s):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                txt = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append("<li>" + inline(txt) + "</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        elif s:
            out.append(f"<p>{inline(s)}</p>")
        i += 1
    return "\n".join(out)


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Microsoft YaHei","Segoe UI",sans-serif;background:#eef1f5;color:#16212b;line-height:1.75;padding:30px 16px}
.doc{max-width:960px;margin:0 auto;background:#fff;border:1px solid #dbe2ea;border-radius:10px;padding:38px 44px 30px}
h1{font-size:29px;letter-spacing:-.6px;border-bottom:3px solid #c8362f;padding-bottom:12px;margin-bottom:6px}
h2{font-size:20px;margin:30px 0 12px;padding-left:10px;border-left:5px solid #c8362f}
h3{font-size:16px;margin:20px 0 8px;color:#2b3a48}
p{margin:9px 0}
ul,ol{margin:9px 0 9px 24px}
li{margin:5px 0}
blockquote{background:#f7f9fc;border-left:4px solid #b6c1cc;padding:9px 14px;margin:10px 0;color:#41505f;font-size:14px;border-radius:0 4px 4px 0}
hr{border:none;border-top:1px solid #e2e8ef;margin:26px 0}
table{width:100%;border-collapse:collapse;margin:14px 0;font-size:13.2px;border:1px solid #dbe2ea;border-radius:6px;overflow:hidden;display:table}
th{background:#f2f5f9;text-align:left;padding:8px 10px;font-size:12.8px;color:#41505f;border-bottom:1px solid #dbe2ea;white-space:nowrap}
td{padding:7px 10px;border-top:1px solid #eef2f7;vertical-align:top}
tbody tr:nth-child(even){background:#fbfcfe}
code{background:#f1f4f8;border:1px solid #e0e6ee;border-radius:3px;padding:1px 5px;font-size:12.5px;font-family:Consolas,monospace;color:#a3352c}
pre{background:#16212b;color:#dfe7ef;padding:14px 16px;border-radius:7px;overflow-x:auto;margin:12px 0}
pre code{background:none;border:none;color:inherit;padding:0}
a{color:#1a6db5;text-decoration:none;border-bottom:1px solid #cfe0f0}
a:hover{background:#eef6ff}
strong{color:#0d1a24}
.foot{margin-top:26px;font-size:12px;color:#7c8a98;border-top:1px solid #e2e8ef;padding-top:12px}
@media (prefers-color-scheme:dark){
 body{background:#0f1720;color:#dbe4ec} .doc{background:#16212b;border-color:#26323e}
 h3{color:#c3d0dc} blockquote{background:#1d2731;color:#a9b7c4;border-color:#3a4756}
 th{background:#1d2731;color:#a9b7c4;border-color:#2c3844} td{border-color:#222d38}
 tbody tr:nth-child(even){background:#1a232d} code{background:#1d2731;border-color:#2c3844}
 strong{color:#fff} a{color:#6db3ec;border-color:#2a4256}
}
@media(max-width:640px){
 body{padding:14px 8px} .doc{padding:18px 14px 20px;border-radius:8px}
 h1{font-size:21px} h2{font-size:17px;margin:22px 0 10px} h3{font-size:15px}
 p,li{font-size:13.8px} blockquote{font-size:13px;padding:8px 11px}
 pre{font-size:12px;padding:11px 12px}
 table{display:block;border:none} thead{display:block}
 thead tr{display:flex;flex-wrap:wrap;gap:6px}
 thead th{display:inline-block;border:1px solid #dbe2ea;border-radius:16px;padding:5px 11px;font-size:12px;background:#f7f9fc;white-space:normal}
 tbody{display:block}
 tbody tr{display:block;border:1px solid #dbe2ea;border-radius:8px;padding:10px 12px;margin-top:9px;background:#fff!important}
 tbody td{display:grid;grid-template-columns:84px 1fr;gap:8px;border:none;padding:3px 0;font-size:12.8px;text-wrap:pretty;word-break:break-word}
 tbody td::before{content:attr(data-label);color:#6b7a89;font-size:11.6px;font-weight:700}
}
@media(prefers-color-scheme:dark) and (max-width:640px){
 tbody tr{background:#1a232d!important;border-color:#2c3844}
 thead th{background:#1d2731;border-color:#2c3844}
}
"""


def main():
    src, dst = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "报告"
    body = convert(io.open(src, encoding="utf-8").read())
    doc = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head>
<body><div class="doc">{body}
<div class="foot">本页为自包含 HTML,可直接在浏览器打开或转发 · 生成于 2026-09-23 · 研究辅助,不构成投资建议</div>
</div></body></html>"""
    io.open(dst, "w", encoding="utf-8").write(doc)
    print("written:", dst, len(doc), "chars")


if __name__ == "__main__":
    main()
