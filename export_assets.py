"""
导出交付资产：多尺寸 PNG / favicon / 反白 / 单黑
做法：先用 cairosvg 渲染到透明底，再用 PIL 裁切真实图形包围盒，
      最后按统一安全边距重新居中 —— 保证方形图标里视觉重心一致。
"""
import pathlib, sys
import cairosvg
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import variants

D = pathlib.Path(__file__).parent
PNG = D / "png"
ASSETS = D / "assets"
FAV = ASSETS / "favicon"
REV = ASSETS / "reverse"
MONO = ASSETS / "mono"
for p in (FAV, REV, MONO):
    p.mkdir(parents=True, exist_ok=True)

SIZES = [16, 32, 48, 64, 128, 256, 512, 1024]
INK, LIGHT = "#1A1A1A", "#F2F0EC"
SAFE = 0.80   # 图标内图形占画布比例


def render(svg_text, size, color=None):
    """渲染透明底 PNG 并返回 PIL Image"""
    s = svg_text.replace("currentColor", color) if color else svg_text
    png = cairosvg.svg2png(bytestring=s.encode(), output_width=size, output_height=size)
    import io
    return Image.open(io.BytesIO(png)).convert("RGBA")


def fit_center(im, out_size, safe=SAFE, bg=None):
    """裁掉透明边，按安全比例缩放，居中放到 out_size 画布"""
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    side = int(out_size * safe)
    scale = side / max(w, h)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (out_size, out_size), bg or (0, 0, 0, 0))
    canvas.alpha_composite(im, ((out_size - nw) // 2, (out_size - nh) // 2))
    return canvas


def main():
    print("── 多尺寸 PNG（原始比例，透明底）──")
    for v in variants.VARIANTS:
        vid = v["id"]
        src = D / "svg" / f"{vid}.svg"
        for s in SIZES:
            cairosvg.svg2png(url=str(src), write_to=str(PNG / f"{vid}-{s}.png"),
                             output_width=s, output_height=s)
    print(f"  {len(variants.VARIANTS)} 方案 × {len(SIZES)} 档")

    print("\n── favicon（自动裁切居中）──")
    for v in variants.VARIANTS:
        vid = v["id"]
        svg_text = (D / "svg" / f"{vid}.svg").read_text(encoding="utf-8")
        for s in (16, 32, 48):
            fit_center(render(svg_text, 512), s).save(FAV / f"{vid}-{s}.png")
        fit_center(render(svg_text, 512), 512, bg=(255, 255, 255, 255)).save(
            FAV / f"{vid}-icon512.png")
    print(f"  {len(variants.VARIANTS)} 套就绪")

    print("\n── 反白版本（深色底）──")
    for v in variants.VARIANTS:
        vid = v["id"]
        svg_text = (D / "svg" / f"{vid}.svg").read_text(encoding="utf-8")
        (REV / f"{vid}-light.svg").write_text(
            svg_text.replace("currentColor", LIGHT), encoding="utf-8")
        fit_center(render(svg_text, 1024, LIGHT), 1024).save(REV / f"{vid}-light.png")
        fit_center(render(svg_text, 1024, LIGHT), 512).save(REV / f"{vid}-light-512.png")
    print(f"  {len(variants.VARIANTS)} 套就绪")

    print("\n── 单黑版本（印刷/烫印）──")
    for v in variants.VARIANTS:
        vid = v["id"]
        svg_text = (D / "svg" / f"{vid}.svg").read_text(encoding="utf-8")
        fit_center(render(svg_text, 1024, INK), 1024).save(MONO / f"{vid}-black.png")
        (MONO / f"{vid}-black.svg").write_text(
            svg_text.replace("currentColor", INK), encoding="utf-8")
    print(f"  {len(variants.VARIANTS)} 套就绪")

    print("\n全部资产导出完成")


if __name__ == "__main__":
    main()
