"""
蜂巢六边 Logo —— 样式 × 配色矩阵生成器

输出：
  hex/svg/<style>--<palette>.svg     单色版（带 currentColor 主色 + 固定强调色）
  hex/svg/<style>--<palette>-solid.svg 全色版（主色+强调色都写死）
  hex/png/<style>--<palette>.png     1024 透明底
  hex/png/flat-<palette>.png         反白适配：主色换成底色，强调色保留
"""
import pathlib, sys, io, itertools
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import styles, palettes

D = pathlib.Path(__file__).parent
SVG = D / "svg"
PNG = D / "png"
SVG.mkdir(exist_ok=True)
PNG.mkdir(exist_ok=True)


def colorize(svg_text, main, accent):
    return (svg_text
            .replace("%%MAIN%%", main)
            .replace("%%ACCENT%%", accent))


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
    print(f"样式 {len(styles.STYLES)} × 配色 {len(palettes.PALETTES)} = {len(combos)} 组合\n")

    for st, pal in combos:
        base = st["build"]()
        vid = f"{st['id']}--{pal['id']}"

        # 全色版
        colored = colorize(base, pal["main"], pal["accent"])
        (SVG / f"{vid}.svg").write_text(colored, encoding="utf-8")
        fit_center(render(base, 1024, pal["main"], pal["accent"]), 1024).save(
            PNG / f"{vid}.png")

        # 单色版：主色留给 currentColor（便于上色），强调色写死
        mono = colorize(base, "currentColor", pal["accent"])
        (SVG / f"{vid}-mono.svg").write_text(mono, encoding="utf-8")

    print(f"SVG → {SVG}")
    print(f"PNG → {PNG}")
    print(f"\n共生成 {len(combos)} 套")


if __name__ == "__main__":
    main()
