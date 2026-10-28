#!/usr/bin/env python3
"""Atom 方法体系 Logo — SVG 生成器（数据源：variants.py）"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import variants
from variants import VARIANTS

OUT = pathlib.Path(__file__).parent
SVG_DIR = OUT / "svg"
PNG_DIR = OUT / "png"
SVG_DIR.mkdir(exist_ok=True)
PNG_DIR.mkdir(exist_ok=True)


def main():
    for v in VARIANTS:
        p = SVG_DIR / f"{v['id']}.svg"
        p.write_text(v["build"]().strip(), encoding="utf-8")
        print(f"  SVG  {p.name}")
    print(f"\n共 {len(VARIANTS)} 个方案 → {SVG_DIR}")

    try:
        import cairosvg
        for v in VARIANTS:
            src = SVG_DIR / f"{v['id']}.svg"
            cairosvg.svg2png(url=str(src), write_to=str(PNG_DIR / f"{v['id']}.png"),
                             output_width=1024, output_height=1024)
        print(f"PNG 全部导出 → {PNG_DIR}（1024×1024，透明底）")
    except Exception as e:
        print(f"PNG 导出失败：{e}")


if __name__ == "__main__":
    main()
