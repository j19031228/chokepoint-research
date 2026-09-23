import os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
html = os.path.join(HERE, "choke_map.html")
out = os.path.join(HERE, "A股AI基础设施链卡点地图.png")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1000, "height": 1400}, device_scale_factor=2)
    pg.goto("file:///" + html.replace("\\", "/"))
    pg.wait_for_timeout(1200)
    pg.screenshot(path=out, full_page=True)
    b.close()

from PIL import Image
im = Image.open(out).convert("RGB")
px = list(im.getdata())
uniq = len(set(px))
print("saved:", out)
print("size:", im.size, "bytes:", os.path.getsize(out))
print("unique_colors:", uniq)
from collections import Counter
print("top3:", Counter(px).most_common(3))
