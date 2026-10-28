"""小尺寸可辨识度测试：16 / 32 / 64 px（全部方案）"""
import pathlib, sys
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import variants

D = pathlib.Path(__file__).parent
P = D / "png"
order = [v["id"] for v in variants.VARIANTS]
SIZES = [16, 32, 64]
LABEL_W = 150
CELL = 64
PAD = 18

W = LABEL_W + len(SIZES) * (CELL + PAD) + PAD
H = len(order) * (CELL + PAD) + PAD
sheet = Image.new("RGB", (W, H), "#FFFFFF")
draw = ImageDraw.Draw(sheet)

for r, name in enumerate(order):
    src = Image.open(P / f"{name}.png").convert("RGBA")
    y = PAD + r * (CELL + PAD)
    draw.text((PAD, y + CELL // 2 - 6), name, fill="#333333")
    for c, s in enumerate(SIZES):
        x = LABEL_W + c * (CELL + PAD)
        small = src.resize((s, s), Image.LANCZOS)
        big = small.resize((CELL, CELL), Image.NEAREST)
        cell = Image.new("RGBA", (CELL, CELL), (255, 255, 255, 255))
        cell.alpha_composite(big)
        sheet.paste(cell.convert("RGB"), (x, y))
        draw.rectangle([x, y, x + CELL, y + CELL], outline="#DDDDDD", width=1)
        draw.text((x + CELL // 2 - 6, y + CELL + 2), f"{s}px", fill="#888888")

out = D / "scale_test.png"
sheet.save(out)
print("saved:", out, sheet.size)
