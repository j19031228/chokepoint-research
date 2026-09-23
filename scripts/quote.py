#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""免登录行情快照 —— 走东方财富公开接口,用于卡点研究的「位置/财务/资金」粗筛。

用法:
  python quote.py 000988 300308 600498        # 个股快照
  python quote.py --bk BK0896                  # 概念/行业板块成分股涨跌
  python quote.py --bk BK0896 --top 20

说明:
  - 数字为盘中/最近收盘快照,仅作参考;财务数据请回到定期报告核对。
  - 接口可能因东财调整而失效,失败时改用 browser_exec 打开 quote.eastmoney.com。
"""
import sys, json, urllib.request, urllib.parse

BASE = "https://push2.eastmoney.com/api/qt"
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def secid(code):
    """6 开头=沪市(1.),其余(0/3/8/4)=深市(0.)"""
    code = code.strip()
    return ("1." if code.startswith(("6", "5", "9")) else "0.") + code


def quote(codes):
    rows = []
    for c in codes:
        try:
            d = _get(f"{BASE}/stock/get?secid={secid(c)}&fields=f43,f57,f58,f169,f170,f116,f117,f162,f167,f168")
            q = d.get("data") or {}
            rows.append({
                "代码": q.get("f57", c), "名称": q.get("f58", "?"),
                "最新价": _num(q.get("f43"), 100), "涨跌幅%": _num(q.get("f170"), 100),
                "总市值(亿)": _num(q.get("f116"), 1e8), "流通市值(亿)": _num(q.get("f117"), 1e8),
                "PE(动)": _num(q.get("f162"), 100), "PB": _num(q.get("f167"), 100),
                "换手%": _num(q.get("f168"), 100),
            })
        except Exception as e:
            rows.append({"代码": c, "名称": f"ERROR {e}"})
    return rows


def board(bk, top=30):
    q = urllib.parse.urlencode({
        "pn": 1, "pz": top, "po": 1, "np": 1, "fltt": 2, "invt": 2, "fid": "f3",
        "fs": f"b:{bk}", "fields": "f12,f14,f2,f3,f20,f8",
    })
    d = _get(f"{BASE}/clist/get?{q}")
    out = []
    for it in (d.get("data") or {}).get("diff", []) or []:
        out.append({"代码": it.get("f12"), "名称": it.get("f14"), "最新价": it.get("f2"),
                    "涨跌幅%": it.get("f3"), "总市值(亿)": _num(it.get("f20"), 1e8),
                    "换手%": it.get("f8")})
    return out


def _num(v, div):
    try:
        if v in ("-", None, ""):
            return None
        return round(float(v) / div, 2)
    except Exception:
        return v


def _print(rows):
    if not rows:
        print("(空)")
        return
    cols = list(rows[0].keys())
    w = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print(" | ".join(c.ljust(w[c]) for c in cols))
    print("-+-".join("-" * w[c] for c in cols))
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(w[c]) for c in cols))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "--bk":
        top = int(a[a.index("--top") + 1]) if "--top" in a else 30
        _print(board(a[1], top))
    else:
        _print(quote(a))
