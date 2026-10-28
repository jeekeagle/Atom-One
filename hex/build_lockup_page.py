"""
生成 lockup.html —— 联合锁定组合展示页（单文件，零外链）
样式与配色数据从 styles.py / palettes.py 注入，与其他页面同源。
"""
import pathlib, sys, json

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import styles, palettes, lockup

D = pathlib.Path(__file__).parent
TPL = D / "lockup.tpl.html"
OUT = D / "lockup.html"

st_data = [{"id": s["id"], "name": s["name"], "note": s["note"]} for s in styles.STYLES]
pal_data = [{"id": p["id"], "name": p["name"], "en": p["en"], "main": p["main"],
             "accent": p["accent"], "on": p["on"], "note": p["note"],
             "usage": p["usage"]} for p in palettes.PALETTES]

# 预生成 10 个样式的锁定组合 SVG（字形已转曲），页面内联使用
logo_svg = {}
for s in styles.STYLES:
    svg, _, _ = lockup.build_lockup(style_id=s["id"], main="__MAIN__", accent="__ACCENT__",
                                     size=100.0)
    # 副标题段落包上标记，页面可切换显示/隐藏
    svg = svg.replace('  <path d="', '  <!--TAGLINE--><path d="', 1) if False else svg
    logo_svg[s["id"]] = svg

# 副标题是最后一个 path，用注释标记以便页面剔除
def mark_tagline(svg):
    """把副标题那个 <path> 包进 TAGLINE 注释对，便于页面切换显隐"""
    marker = '<!--TAGLINE-->'
    endm = '<!--/TAGLINE-->'
    # 副标题 path 是最后一个 <path .../>
    i = svg.rfind('<path d="')
    if i < 0:
        return svg
    j = svg.find('/>', i) + 2
    return svg[:i] + marker + svg[i:j] + endm + svg[j:]

logo_svg = {k: mark_tagline(v) for k, v in logo_svg.items()}

html = TPL.read_text(encoding="utf-8")
if "__STYLES__" not in html or "__PALETTES__" not in html:
    sys.exit(f"模板缺少占位符：{TPL}")
html = html.replace("__STYLES__", json.dumps(st_data, ensure_ascii=False))
html = html.replace("__PALETTES__", json.dumps(pal_data, ensure_ascii=False))
html = html.replace("__LOGO_SVG__", json.dumps(logo_svg, ensure_ascii=False))
OUT.write_text(html, encoding="utf-8")
print(f"saved: {OUT}  ({len(html)} chars)")
print(f"  样式 {len(st_data)} / 配色 {len(pal_data)} / 预生成锁定 SVG {len(logo_svg)}")
