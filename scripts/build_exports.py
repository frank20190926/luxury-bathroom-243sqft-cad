"""Build the A3 portfolio PDF, the CAD pack zip and boards.js (sheet list read by index.html).
Rerun after any board JPEG changes. Sheets ID-01/ID-02 fall back to the CAD sheet PNGs until board1_*.jpg /
board2_*.jpg exist in the project root."""
import json
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "exports"
SHEETS = [
    ("ID-01", "Option A plan", "board1_*.jpg", "assets/cad_plan_option_a.png"),
    ("ID-02", "3D cutaway & views", "board2_*.jpg", "assets/cad_3d_cutaway_iso.png"),
    ("ID-03", "Elevations, millwork & lighting", "board3_*.jpg", None),
    ("ID-04", "Materials & constructability", "board4_*.jpg", None),
]
PAGE = (3200, 2263)  # A3 landscape 420 x 297 mm at ~193.5 dpi


def resolve():
    out = []
    for sid, title, pat, fallback in SHEETS:
        hits = sorted(ROOT.glob(pat))
        src = hits[0].relative_to(ROOT).as_posix() if hits else fallback
        if src is None:
            raise SystemExit(f"{sid}: missing {pat}")
        out.append({"id": sid, "title": title, "src": src, "fallback": not hits})
    return out


def page(path):
    im = Image.open(ROOT / path).convert("RGB")
    im.thumbnail(PAGE, Image.Resampling.LANCZOS)
    pg = Image.new("RGB", PAGE, "white")
    pg.paste(im, ((PAGE[0] - im.width) // 2, (PAGE[1] - im.height) // 2))
    return pg


def main():
    sheets = resolve()
    pdf = EX / "Luxury_Bathroom_243sqft_Submission_A3.pdf"
    pages = [page(s["src"]) for s in sheets]
    pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=PAGE[0] / (420 / 25.4), quality=92)
    z = EX / "Luxury_Bathroom_243sqft_CAD_Pack.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
        for p in ["exports/Master_Bathroom_243sqft_Proposal.dxf", "exports/Master_Bathroom_243sqft_Proposal.dwg",
                  "layout_geometry.json", "exports/cad_validation.json", "exports/dwg_validation.json",
                  "exports/geometry_validation.json", pdf.relative_to(ROOT).as_posix()]:
            f.write(ROOT / p, Path(p).name)
    (ROOT / "boards.js").write_text("window.BOARDS = " + json.dumps(sheets, indent=1) + ";\n")
    for s in sheets:
        print(s["id"], s["src"], "(fallback CAD sheet)" if s["fallback"] else "")
    print(pdf.name, f"{pdf.stat().st_size/1e6:.1f} MB;", z.name, f"{z.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    main()
