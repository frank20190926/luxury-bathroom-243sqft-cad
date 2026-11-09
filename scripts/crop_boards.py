#!/usr/bin/env python3
"""Crop the pure drawing areas out of the CAD presentation PNGs for the ID-01 / ID-02 boards.

Boxes are in source pixels. The supplied task boxes assumed 2400x1850 / 2400x1500 sources for the
cutaway and Existing/Option B sheets; the actual renders are 1800x1400 / 1600x1000, so those two
boxes are measured on the actual files. Internal coordination-hold tags (e.g. "/ C04") that sit
inside the drawing field are painted out with the local paper colour.
"""
from pathlib import Path
from PIL import Image, ImageDraw

A = Path(__file__).resolve().parent.parent / "assets"

JOBS = [
    # src, box, dst, [mask boxes in source px]
    ("cad_plan_option_a.png", (200, 250, 2200, 2070), "crop_plan_a.png", [(1596, 924, 1659, 948)]),
    ("cad_3d_cutaway_iso.png", (270, 235, 1545, 1110), "crop_cutaway_iso.png", []),
    ("cad_plan_existing_vs_option_b.png", (120, 120, 1467, 780), "crop_existing_vs_b.png", []),
    ("cad_4_elevations.png", (100, 190, 2300, 1380), "crop_4_elevations.png", []),
]


def main():
    for src, box, dst, masks in JOBS:
        im = Image.open(A / src).convert("RGB")
        w, h = im.size
        assert box[2] <= w and box[3] <= h, f"{src}: box {box} exceeds {w}x{h}"
        if masks:
            d = ImageDraw.Draw(im)
            for m in masks:
                fill = im.getpixel((m[0] - 3, m[1] - 3))
                d.rectangle(m, fill=fill)
            if src == "cad_plan_option_a.png":  # keep the 28" WC opening width, drop the hold tag
                from PIL import ImageFont
                f = ImageFont.truetype(str(A / "fonts" / "IBMPlexSans-400.ttf"), 17)
                d.text((1600, 928), '28"', font=f, fill=(51, 49, 46))
        out = im.crop(box)
        out.save(A / dst, optimize=True)
        print(f"{src} {w}x{h} -> {dst} {out.size[0]}x{out.size[1]}")


if __name__ == "__main__":
    main()
