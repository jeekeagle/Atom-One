"""
导出 Atom 联合锁定组合（Lockup）全套资产

图标在左 · 字标在右。字形已转曲，不依赖系统字体。

输出:
  lockup/svg/       全色 SVG（主色+强调色写死）
  lockup/svg-mono/  单色 SVG（主标 currentColor）
  lockup/png/       透明底 PNG
  lockup/png-rev/   反白版 PNG
"""
import pathlib, sys, io, itertools
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import styles, palettes, lockup

D = pathlib.Path(__file__).parent
SVG = D / "lockup" / "svg"
SVG_MONO = D / "lockup" / "svg-mono"
PNG = D / "lockup" / "png"
PNGREV = D / "lockup" / "png-rev"
for p in (SVG, SVG_MONO, PNG, PNGREV):
    p.mkdir(parents=True, exist_ok=True)

LIGHT = "#F2F0EC"


def render(svg_text, width):
    import cairosvg
    png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=width)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def main():
    combos = list(itertools.product(styles.STYLES, palettes.PALETTES))
    n = 0
    for st, pal in combos:
        vid = f"{st['id']}--{pal['id']}"

        # 全色
        svg, w, h = lockup.build_lockup(style_id=st["id"], main=pal["main"],
                                         accent=pal["accent"], size=100.0)
        (SVG / f"{vid}.svg").write_text(svg, encoding="utf-8")
        render(svg, 1200).save(PNG / f"{vid}.png")

        # 单色（主标 currentColor，强调色写死）
        svg_m, _, _ = lockup.build_lockup(style_id=st["id"], main="currentColor",
                                          accent=pal["accent"], size=100.0)
        (SVG_MONO / f"{vid}.svg").write_text(svg_m, encoding="utf-8")

        # 反白：主标转浅色，强调色保留
        svg_r, _, _ = lockup.build_lockup(style_id=st["id"], main=LIGHT,
                                          accent=pal["accent"], size=100.0)
        render(svg_r, 1200).save(PNGREV / f"{vid}-reverse.png")
        n += 1

    print(f"锁定组合 {n} 套")
    print(f"  SVG       {SVG}")
    print(f"  SVG-mono  {SVG_MONO}")
    print(f"  PNG       {PNG}")
    print(f"  PNG-rev   {PNGREV}")

    # ── 精选：网站与文档直接可用的几套 ──
    import shutil
    PICK = D / "pick"
    PICK.mkdir(exist_ok=True)
    picks = [
        ("s1-nested--ink-rust", "lockup-primary"),
        ("s2-solid-outer--navy-cyan", "lockup-digital"),
        ("s4-ring--sand-umber", "lockup-print"),
        ("s1-nested--plum-coral", "lockup-launch"),
    ]
    for vid, name in picks:
        shutil.copy(SVG / f"{vid}.svg", PICK / f"{name}.svg")
        shutil.copy(SVG_MONO / f"{vid}.svg", PICK / f"{name}-mono.svg")
        shutil.copy(PNG / f"{vid}.png", PICK / f"{name}.png")
        shutil.copy(PNGREV / f"{vid}-reverse.png", PICK / f"{name}-reverse.png")
    print(f"  精选      {PICK}")


if __name__ == "__main__":
    main()
