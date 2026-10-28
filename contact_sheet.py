"""把指定轮次的方案拼成对比大图"""
import pathlib, sys
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import variants

D = pathlib.Path(__file__).parent
P = D / "png"

rnd = int(sys.argv[1]) if len(sys.argv) > 1 else 0
order = [v["id"] for v in variants.VARIANTS if rnd == 0 or v["round"] == rnd]
if len(sys.argv) > 2 and sys.argv[2] == "all":
    order = [v["id"] for v in variants.VARIANTS]

CELL, PAD, LABEL_H = 380, 34, 40
COLS = 4
rows = (len(order) + COLS - 1) // COLS
W = COLS * (CELL + PAD) + PAD
H = rows * (CELL + PAD + LABEL_H) + PAD

sheet = Image.new("RGB", (W, H), "#FFFFFF")
draw = ImageDraw.Draw(sheet)
for idx, name in enumerate(order):
    p = P / f"{name}.png"
    if not p.exists():
        continue
    im = Image.open(p).convert("RGBA").resize((CELL, CELL), Image.LANCZOS)
    card = Image.new("RGBA", (CELL, CELL), (255, 255, 255, 255))
    card.alpha_composite(im)
    col, row = idx % COLS, idx // COLS
    x = PAD + col * (CELL + PAD)
    y = PAD + row * (CELL + PAD + LABEL_H)
    sheet.paste(card.convert("RGB"), (x, y))
    draw.rectangle([x, y, x + CELL, y + CELL], outline="#E2E2E2", width=1)
    draw.text((x + 4, y + CELL + 10), name, fill="#333333")

out = D / (f"contact_sheet_r{rnd}.png" if rnd else "contact_sheet.png")
sheet.save(out)
print("saved:", out, sheet.size)
