"""
锁定组合比色图
  python lockup_sheet.py styles    # 行=样式，列=配色
  python lockup_sheet.py palettes  # 行=配色，列=样式
"""
import pathlib, sys, itertools
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import styles, palettes

D = pathlib.Path(__file__).parent
LK = D / "lockup" / "png"

FONT = "C:/Windows/Fonts/msyh.ttc"
FONT_BD = "C:/Windows/Fonts/msyhbd.ttc"


def f(size, bold=False):
    try:
        return ImageFont.truetype(FONT_BD if bold else FONT, size)
    except Exception:
        return ImageFont.load_default()


def load(vid, width):
    p = LK / f"{vid}.png"
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA")
    h = int(im.height * width / im.width)
    return im.resize((width, h), Image.LANCZOS)


def compose(st, pal, width=210):
    im = load(f"{st['id']}--{pal['id']}", width)
    if im is None:
        return None
    bg = Image.new("RGBA", im.size, pal["on"] if pal["on"] != "#FFFFFF" else (255, 255, 255, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def sheet_styles():
    CELL, PAD, HEAD, LBL = 230, 12, 34, 40
    rows, cols = len(styles.STYLES), len(palettes.PALETTES)
    W = PAD + cols * (CELL + PAD)
    H = PAD + rows * (100 + LBL + PAD) + HEAD + 20
    out = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(out)
    d.text((PAD, 8), "锁定组合 · 样式 × 配色", font=f(19, True), fill="#111111")
    for j, p in enumerate(palettes.PALETTES):
        d.text((PAD + j * (CELL + PAD), HEAD + 2), p["name"], font=f(12, True), fill="#333333")
    for i, s in enumerate(styles.STYLES):
        y = PAD + HEAD + i * (100 + LBL + PAD)
        d.text((4, y + 40), s["name"], font=f(12, True), fill="#111111")
        for j, p in enumerate(palettes.PALETTES):
            c = compose(s, p, CELL)
            if c is None:
                continue
            x = PAD + j * (CELL + PAD)
            out.paste(c, (x, y))
    path = D / "sheet-lockup-styles.png"
    out.save(path)
    print("saved:", path, out.size)


def sheet_palettes():
    CELL, PAD, HEAD, LBL = 190, 12, 34, 44
    rows, cols = len(palettes.PALETTES), len(styles.STYLES)
    W = PAD + cols * (CELL + PAD)
    H = PAD + rows * (82 + LBL + PAD) + HEAD + 20
    out = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(out)
    d.text((PAD, 8), "锁定组合 · 配色 × 样式", font=f(19, True), fill="#111111")
    for j, s in enumerate(styles.STYLES):
        d.text((PAD + j * (CELL + PAD), HEAD + 2), s["name"], font=f(11, True), fill="#333333")
    for i, p in enumerate(palettes.PALETTES):
        y = PAD + HEAD + i * (82 + LBL + PAD)
        d.text((4, y + 32), p["name"], font=f(12, True), fill="#111111")
        for j, s in enumerate(styles.STYLES):
            c = compose(s, p, CELL)
            if c is None:
                continue
            x = PAD + j * (CELL + PAD)
            out.paste(c, (x, y))
        d.text((4, y + 86), f"{p['main']} / {p['accent']}", font=f(10), fill="#666666")
    path = D / "sheet-lockup-palettes.png"
    out.save(path)
    print("saved:", path, out.size)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "styles"
    (sheet_palettes if mode == "palettes" else sheet_styles)()
