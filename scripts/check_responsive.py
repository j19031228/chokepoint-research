#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""响应式回归:在 320/375/412/768/1280 下检查 document.scrollWidth <= innerWidth,
并列出溢出的元素(若有)。用法: python check_responsive.py file1.html file2.html ...
"""
import sys, os, json
from playwright.sync_api import sync_playwright

WIDTHS = [320, 375, 412, 768, 1280]
JS = """() => {
  const iw = window.innerWidth;
  const sw = document.documentElement.scrollWidth;
  const bad = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && (r.right > iw + 1.5 || r.left < -1.5)) {
      const c = el.className && typeof el.className === 'string' ? el.className.split(' ')[0] : '';
      bad.push(el.tagName + (c ? '.' + c : '') + ' [' + Math.round(r.left) + ',' + Math.round(r.right) + ']');
    }
  });
  return {iw, sw, bad: bad.slice(0, 8)};
}"""

fails = 0
with sync_playwright() as p:
    try:
        b = p.chromium.launch()
    except Exception:
        # 本机 playwright 版本与下载的 headless shell 不匹配 → 退回系统 Chrome
        try:
            b = p.chromium.launch(channel="chrome")
        except Exception:
            import glob
            cands = glob.glob(os.path.expandvars(
                r"%LOCALAPPDATA%\ms-playwright\chromium_headless_shell-*\chrome-win\chrome-headless-shell.exe"))
            b = p.chromium.launch(executable_path=sorted(cands)[-1])
    for f in sys.argv[1:]:
        url = "file:///" + os.path.abspath(f).replace("\\", "/")
        print("=" * 66)
        print(os.path.basename(f))
        for w in WIDTHS:
            pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=1)
            pg.goto(url)
            pg.wait_for_timeout(500)
            r = pg.evaluate(JS)
            ok = r["sw"] <= r["iw"] + 1
            if not ok:
                fails += 1
            print("  %5dpx  scrollWidth=%4d innerWidth=%4d  %s %s" % (
                w, r["sw"], r["iw"], "OK " if ok else "OVERFLOW",
                ("| " + "; ".join(r["bad"])) if r["bad"] else ""))
            pg.close()
    b.close()
print("=" * 66)
print("FAILS:", fails)
sys.exit(1 if fails else 0)
