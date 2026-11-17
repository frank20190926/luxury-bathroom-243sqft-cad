#!/usr/local/bin/python3.11
"""Render ID-01 / ID-02 HTML boards to 3200x2400 JPEG (1600x1200 CSS px @2x, quality 95)."""
import io
import sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BOARDS = {
    "board1.html": "board1_floorplan_storage.jpg",
    "board2.html": "board2_perspective_views.jpg",
    "board3.html": "board3_elevations_millwork.jpg",
    "board4.html": "board4_materials_constructability.jpg",
}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 1200}, device_scale_factor=2)
    for html, jpg in BOARDS.items():
        if len(sys.argv) > 1 and html not in sys.argv[1:]:
            continue
        pg.goto((ROOT / html).as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        over = pg.evaluate("[...document.querySelectorAll('.sheet *')].filter(e=>e.scrollHeight>e.clientHeight+1 && getComputedStyle(e).overflow!='visible').length")
        bottom = pg.evaluate("Math.max(...[...document.querySelectorAll('.sheet *')].map(e=>e.getBoundingClientRect().bottom))")
        im = Image.open(io.BytesIO(pg.screenshot(full_page=False))).convert("RGB")
        im.save(ROOT / jpg, "JPEG", quality=95)
        print(f"{jpg} {im.size} max-element-bottom={bottom:.0f} overflow={over}")
    b.close()
