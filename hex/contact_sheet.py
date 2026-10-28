"""
蜂巢六边 —— 比色图生成器

用法:
  python contact_sheet.py            # 全部 10 样式 × 10 配色
  python contact_sheet.py styles     # 只看样式（统一用第一套配色）
  python contact_sheet.py palettes   # 只看配色（统一用第一个样式）
  python contact_sheet.py grid       # 网格速览：行=配色，列=样式
"""
import pathlib, sys, itertools
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import styles, palettes

D = pathlib.Path(__file__).parent
PNG = D / "png"

FONT = "C:/Windows/Fonts/msyh.ttc"
FONT_BD = "C:/Windows/Fonts/msyhbd.ttc"


def f(size, bold=False):
    try:
        return ImageFont.truetype(FONT_BD if bold else FONT, size)
    except Exception:
        return ImageFont.load_default()


def load(vid, size):
    p = PNG / f"{vid}.png"
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA").resize((size, size), Image.LANCZOS)
    return im


def card(im, size, bg, pad_ratio=0.22):
    """把 logo 放到带内边距的色卡上"""
    card = Image.new("RGBA", (size, size), bg)
    inner = int(size * (1 - pad_ratio))
    if im:
        resized = im.resize((inner, inner), Image.LANCZOS)
        card.alpha_composite(resized, ((size - inner) // 2, (size - inner) // 2))
    return card


def sheet_styles():
    """每行一个样式，10 套配色并排"""
    pal = palettes.PALETTES
    st = styles.STYLES
    CELL, PAD, HEAD, LBL = 130, 14, 34, 46
    COLS = len(pal)
    rows = len(st)
    W = PAD + COLS * (CELL + PAD)
    H = PAD + rows * (CELL + LBL + PAD) + HEAD + 20
    out = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(out)
    d.text((PAD, 8), "蜂巢六边 · 配色矩阵（行 = 样式，列 = 配色）", font=f(19, True), fill="#111111")
    for j, p in enumerate(pal):
        x = PAD + j * (CELL + PAD)
        d.text((x, HEAD + 2), p["name"], font=f(13, True), fill="#333333")
    for i, s in enumerate(st):
        y = PAD + HEAD + i * (CELL + LBL + PAD)
        d.text((4, y + CELL // 2 - 8), s["name"], font=f(13, True), fill="#111111")
        for j, p in enumerate(pal):
            vid = f"{s['id']}--{p['id']}"
            im = load(vid, CELL)
            x = PAD + j * (CELL + PAD)
            bg = p["on"] if p["id"] != "black-white" else "#FFFFFF"
            c = card(im, CELL, bg)
            out.paste(c.convert("RGB"), (x, y))
            d.rectangle([x, y, x + CELL, y + CELL], outline="#DDDDDD", width=1)
    path = D / "sheet-styles.png"
    out.save(path)
    print("saved:", path, out.size)


def sheet_palettes():
    """每个配色一整行，10 个样式并排 + 色卡信息"""
    pal = palettes.PALETTES
    st = styles.STYLES
    CELL, PAD, HEAD, LBL = 130, 14, 34, 56
    W = PAD + len(st) * (CELL + PAD)
    H = PAD + len(pal) * (CELL + LBL + PAD) + HEAD + 20
    out = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(out)
    d.text((PAD, 8), "蜂巢六边 · 样式矩阵（行 = 配色，列 = 样式）", font=f(19, True), fill="#111111")
    for j, s in enumerate(st):
        x = PAD + j * (CELL + PAD)
        d.text((x, HEAD + 2), s["name"], font=f(13, True), fill="#333333")
    for i, p in enumerate(pal):
        y = PAD + HEAD + i * (CELL + LBL + PAD)
        d.text((4, y + CELL // 2 - 8), p["name"], font=f(13, True), fill="#111111")
        for j, s in enumerate(st):
            vid = f"{s['id']}--{p['id']}"
            im = load(vid, CELL)
            x = PAD + j * (CELL + PAD)
            bg = p["on"]
            c = card(im, CELL, bg)
            out.paste(c.convert("RGB"), (x, y))
            d.rectangle([x, y, x + CELL, y + CELL], outline="#DDDDDD", width=1)
        # 色值
        d.text((4, y + CELL + 6), f"{p['main']} / {p['accent']}", font=f(11), fill="#666666")
    path = D / "sheet-palettes.png"
    out.save(path)
    print("saved:", path, out.size)


def sheet_grid():
    """紧凑网格：行=配色，列=样式，无标签"""
    pal = palettes.PALETTES
    st = styles.STYLES
    CELL, PAD = 92, 8
    W = PAD + len(st) * (CELL + PAD)
    H = PAD + len(pal) * (CELL + PAD)
    out = Image.new("RGB", (W, H), "#FFFFFF")
    for i, p in enumerate(pal):
        for j, s in enumerate(st):
            vid = f"{s['id']}--{p['id']}"
            im = load(vid, CELL)
            x = PAD + j * (CELL + PAD)
            y = PAD + i * (CELL + PAD)
            bg = p["on"]
            out.paste(card(im, CELL, bg, 0.26).convert("RGB"), (x, y))
    path = D / "sheet-grid.png"
    out.save(path)
    print("saved:", path, out.size)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "styles"
    if mode == "styles":
        sheet_styles()
    elif mode == "palettes":
        sheet_palettes()
    else:
        sheet_grid()
