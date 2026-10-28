"""
生成 preview.html —— 把 styles.py / palettes.py 的数据与 SVG 源码注入模板
（单一数据源：页面永远跟着定义走，不手抄）
"""
import pathlib, sys, json

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import styles, palettes

D = pathlib.Path(__file__).parent
TPL = D / "preview.tpl.html"     # 模板（手写，不注入数据）
OUT = D / "preview.html"         # 产物（注入数据，单文件可直接打开）

st_data = []
for s in styles.STYLES:
    st_data.append({
        "id": s["id"],
        "name": s["name"],
        "en": s["en"],
        "note": s["note"],
        "raw": s["build"]().strip(),
    })

pal_data = []
for p in palettes.PALETTES:
    pal_data.append({
        "id": p["id"],
        "name": p["name"],
        "en": p["en"],
        "main": p["main"],
        "accent": p["accent"],
        "on": p["on"],
        "note": p["note"],
        "usage": p["usage"],
    })

html = TPL.read_text(encoding="utf-8")
if "__STYLES__" not in html or "__PALETTES__" not in html:
    sys.exit(f"模板缺少占位符：{TPL}")
html = html.replace("__STYLES__", json.dumps(st_data, ensure_ascii=False))
html = html.replace("__PALETTES__", json.dumps(pal_data, ensure_ascii=False))
OUT.write_text(html, encoding="utf-8")
print(f"saved: {OUT}  ({len(html)} chars)")
print(f"  样式 {len(st_data)} / 配色 {len(pal_data)}")
