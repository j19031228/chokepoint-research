import os, json
from playwright.sync_api import sync_playwright

P = r"C:/Users/34567/AppData/Local/hermes/work/projects/chokepoint-research/reports/卡点面板.html"
errors = []

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1100, "height": 900})
    pg.on("console", lambda m: errors.append(m.type + ": " + m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    pg.goto("file:///" + P)
    pg.wait_for_timeout(600)

    r = {}
    r["rows_all"] = pg.eval_on_selector_all("#tb tr", "els => els.length")
    r["chain_levels"] = pg.eval_on_selector_all("#chain .lv", "els => els.length")
    r["details"] = pg.eval_on_selector_all("details", "els => els.length")
    r["title"] = pg.title()

    # 筛选:只看 ★★★
    pg.click(".ctrls button[data-f='3']")
    pg.wait_for_timeout(200)
    r["rows_star3"] = pg.eval_on_selector_all("#tb tr", "els => els.length")

    # 筛选:有 A 股标的
    pg.click(".ctrls button[data-f='cn']")
    pg.wait_for_timeout(200)
    r["rows_cn"] = pg.eval_on_selector_all("#tb tr", "els => els.length")

    # 回到全部,点表头排序
    pg.click(".ctrls button[data-f='all']")
    pg.wait_for_timeout(150)
    pg.click("th[data-k='name']")
    pg.wait_for_timeout(200)
    r["first_after_sort_name"] = pg.eval_on_selector("#tb tr td.nm", "e => e.textContent")

    # 展开链条第 5 层(上游材料)
    pg.click("#chain .lv:nth-child(5)")
    pg.wait_for_timeout(200)
    r["detail_visible"] = pg.eval_on_selector("#chain .lv:nth-child(5) .detail",
        "e => getComputedStyle(e).display")

    # 首屏截图(用于人工/像素核对)
    shot = r"C:/Users/34567/AppData/Local/hermes/work/projects/chokepoint-research/reports/_verify_panel.png"
    pg.screenshot(path=shot, full_page=False)
    r["shot"] = shot
    b.close()

print(json.dumps(r, ensure_ascii=False, indent=1))
print("console_errors:", errors if errors else "NONE")

from PIL import Image
im = Image.open(r["shot"]).convert("RGB")
px = list(im.getdata())
print("shot size:", im.size, "unique_colors:", len(set(px)))
