"""
蜂巢六边 —— 交付资产导出

输出目录:
  svg/        全色版 SVG（主色+强调色写死，可直接嵌入网页）
  svg-mono/   单色版 SVG（主色=currentColor，方便继承文字颜色）
  png/        1024 透明底 PNG
  png-512/    512 透明底 PNG
  favicon/    16 / 32 / 48 / 512
  reverse/    反白版（深底专用）
"""
import pathlib, sys, io, itertools
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import styles, palettes

D = pathlib.Path(__file__).parent
SVG = D / "svg"
SVG_MONO = D / "svg-mono"
PNG = D / "png"
PNG512 = D / "png-512"
FAV = D / "favicon"
REV = D / "reverse"
for p in (SVG, SVG_MONO, PNG, PNG512, FAV, REV):
    p.mkdir(exist_ok=True)


def render(svg_text, size, main=None, accent=None):
    import cairosvg
    s = svg_text
    if main:
        s = s.replace("%%MAIN%%", main)
    if accent:
        s = s.replace("%%ACCENT%%", accent)
    png = cairosvg.svg2png(bytestring=s.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def fit_center(im, out_size, safe=0.80, bg=None):
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
    combos = list(itertools.product(styles.STYLES, palettes.PALETTES))
    for st, pal in combos:
        base = st["build"]()
        vid = f"{st['id']}--{pal['id']}"

        # 全色 SVG
        colored = base.replace("%%MAIN%%", pal["main"]).replace("%%ACCENT%%", pal["accent"])
        (SVG / f"{vid}.svg").write_text(colored, encoding="utf-8")

        # 单色 SVG：主色交给 currentColor
        mono = base.replace("%%MAIN%%", "currentColor").replace("%%ACCENT%%", pal["accent"])
        (SVG_MONO / f"{vid}.svg").write_text(mono, encoding="utf-8")

        # PNG
        im = render(base, 1024, pal["main"], pal["accent"])
        fit_center(im, 1024).save(PNG / f"{vid}.png")
        fit_center(im, 512).save(PNG512 / f"{vid}.png")

        # favicon
        for s in (16, 32, 48):
            fit_center(render(base, 512, pal["main"], pal["accent"]), s).save(
                FAV / f"{vid}-{s}.png")
        fit_center(render(base, 512, pal["main"], pal["accent"]), 512,
                   bg=(255, 255, 255, 255)).save(FAV / f"{vid}-icon512.png")

        # 反白版：深底专用 —— 主色换成浅色，强调色保留
        light = "#F2F0EC"
        rev_base = base.replace("%%MAIN%%", light).replace("%%ACCENT%%", pal["accent"])
        (REV / f"{vid}-reverse.svg").write_text(rev_base, encoding="utf-8")
        fit_center(render(base, 1024, light, pal["accent"]), 1024).save(
            REV / f"{vid}-reverse.png")

    print(f"样式 {len(styles.STYLES)} × 配色 {len(palettes.PALETTES)} = {len(combos)} 组合")
    print(f"  SVG        {SVG}")
    print(f"  SVG-mono   {SVG_MONO}")
    print(f"  PNG 1024   {PNG}")
    print(f"  PNG 512    {PNG512}")
    print(f"  favicon    {FAV}")
    print(f"  reverse    {REV}")


if __name__ == "__main__":
    main()
