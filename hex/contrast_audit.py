"""
配色对比度自动校验器

把「这套配色能不能用」从肉眼判断变成可计算结论。

WCAG 2.1 相对亮度与对比度:
    L = 0.2126R + 0.7152G + 0.0722B   (R/G/B 为线性化后的 sRGB 分量)
    ratio = (L_light + 0.05) / (L_dark + 0.05)

判定基准（按角色分档，不是一刀切）:
    正文 / 文字  >= 4.5   (WCAG AA)
    图形 / 轮廓  >= 3.0   (WCAG AA 非文本图形)
    装饰 / 点睛  >= 1.5   (纯视觉点睛，不承载信息)

★ 关键：同一套配色有三种上色方式，必须分别对承载面评估。
  单色版 mono    —— 整个标志用一个颜色（pal.main）
  全色版 full    —— 主色画结构 + 强调色画内核（pal.main / pal.accent）
  反白版 reverse —— 主色换浅色 + 强调色保留（LIGHT / pal.accent）

  只判「全色版在白底」是错的：墨黑锈红在墨黑底上，全色版必然糊掉，
  但反白版正是它的标准用法。所以三种渲染方式必须各自独立评估。

用法:
    python contrast_audit.py             # 输出审计报告
    python contrast_audit.py --json      # 输出 JSON
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import palettes

LIGHT = "#F2F0EC"   # 反白版使用的浅色主色
DEEP = "#0D1117"    # 深底参考色

SURFACES = {
    "white": ("纯白底", "#FFFFFF"),
    "paper": ("纸本底", "#F2F0EC"),
    "sand":  ("沙色底", "#F7F4EF"),
    "ink":   ("墨黑底", "#1A1A1A"),
    "deep":  ("深空底", "#0D1117"),
}

T_BODY = 4.5   # 正文级
T_GRAPH = 3.0  # 图形级
T_DECOR = 1.5  # 装饰级


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _lin(c):
    """sRGB 分量 → 线性分量"""
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color):
    r, g, b = (_lin(c) for c in hex_to_rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    """fg 在 bg 上的对比度"""
    l1, l2 = luminance(fg), luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def cmyk_of(hex_color):
    """粗略 CMYK（印刷参考值，非色彩管理转换）"""
    r, g, b = hex_to_rgb(hex_color)
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return tuple(round(v * 100) for v in (c, m, y, k))


def grade(ratio, threshold):
    if ratio >= threshold:
        return "PASS"
    if ratio >= threshold - 1.0:
        return "MARGINAL"
    return "FAIL"


def _modes(p):
    """一套配色对应的三种上色方式 → [(模式名, 结构色, 点睛色 or None, 品牌优先级)]

    品牌优先级用于「多种上色方式都可用时选哪个」：
    全色版 > 反白版 > 单色版。标志的识别性来自主色+强调色的组合，
    单色版虽然对比度最高，但只在承载面实在放不下双色时作为退路。
    """
    out = [("全色版", p["main"], p["accent"], 0)]
    out.append(("反白版", LIGHT, p["accent"], 1))
    out.append(("单色版", p["main"], None, 2))
    if p.get("reverse"):
        # 反白专用配色没有「全色版」——主色+白强调在白底上必然糊掉
        out = [x for x in out if x[0] != "全色版"]
    return out


def audit():
    results = []
    for p in palettes.PALETTES:
        rec = {
            "id": p["id"], "name": p["name"], "en": p["en"],
            "main": p["main"], "accent": p["accent"],
            "note": p.get("note", ""), "usage": p.get("usage", ""),
            "is_reverse": p.get("reverse", False),
            "cmyk_main": cmyk_of(p["main"]),
            "cmyk_accent": cmyk_of(p["accent"]),
            "surface_rows": [],
        }

        for s_key, (s_name, s_hex) in SURFACES.items():
            best = None
            for mode, struct_c, dot_c, prio in _modes(p):
                r_struct = contrast(struct_c, s_hex)
                ok = r_struct >= T_GRAPH
                r_dot = None
                if dot_c is not None:
                    r_dot = contrast(dot_c, s_hex)
                    # 点睛色若为白/浅色（在深底上承载信息），按正文级要求
                    t_dot = T_BODY if dot_c.upper() in ("#FFFFFF", "#F2F0EC") else T_DECOR
                    if r_dot < t_dot:
                        ok = False
                if ok:
                    # 品牌优先级为主：同优先级下再比对比度（更保险）
                    key = (prio, -r_struct)
                    if best is None or key < best[0]:
                        best = (key, mode, struct_c, dot_c, r_struct, r_dot)
            rec["surface_rows"].append({
                "surface_key": s_key, "surface_name": s_name, "surface_hex": s_hex,
                "usable": best is not None,
                "mode": best[1] if best else None,
                "struct_color": best[2] if best else None,
                "dot_color": best[3] if best else None,
                "struct_ratio": round(best[4], 2) if best else None,
                "dot_ratio": round(best[5], 2) if best and best[5] is not None else None,
            })

        rec["usable_surfaces"] = [r["surface_name"] for r in rec["surface_rows"] if r["usable"]]
        rec["verdict"] = "OK" if rec["usable_surfaces"] else "UNUSABLE"
        results.append(rec)
    return results


def print_report(results):
    print("=" * 100)
    print("配色对比度审计 —— Atom 标志系统")
    print("阈值：图形级 3.0 / 正文级 4.5 / 装饰级 1.5（WCAG 2.1 相对亮度公式）")
    print("判定含三种上色方式：单色版 / 全色版 / 反白版，各自独立对承载面评估")
    print("=" * 100)

    for r in results:
        print(f"\n【{r['name']}】 {r['en']}  ({r['id']})")
        print(f"  主色 {r['main']}  CMYK {tuple(r['cmyk_main'])}"
              f"    强调 {r['accent']}  CMYK {tuple(r['cmyk_accent'])}")
        print(f"  {r['note']}")
        print(f"  建议用途：{r['usage']}")
        print(f"  {'承载面':<12}{'可用':>6}{'推荐上色':>10}{'结构对比':>10}{'点睛对比':>10}")
        print("  " + "-" * 72)
        for c in r["surface_rows"]:
            mark = "✓" if c["usable"] else "—"
            mode = c["mode"] or "—"
            sr = f"{c['struct_ratio']:.2f}" if c["struct_ratio"] else "—"
            dr = f"{c['dot_ratio']:.2f}" if c["dot_ratio"] else "—"
            print(f"  {c['surface_name']:<12}{mark:>6}{mode:>10}{sr:>10}{dr:>10}")
        print(f"  → 可用承载面：{', '.join(r['usable_surfaces']) if r['usable_surfaces'] else '★ 无'}")

    print("\n" + "=" * 100)
    n_ok = sum(1 for r in results if r["verdict"] == "OK")
    print(f"总计 {len(results)} 套配色，全部可用 {n_ok} 套，不可用 {len(results) - n_ok} 套")
    print("=" * 100)


def main():
    results = audit()
    if "--json" in sys.argv:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_report(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
