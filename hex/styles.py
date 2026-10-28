"""
蜂巢六边（v3-hex）Logo —— 样式变体定义（单一数据源）

结构基元来自用户已选定的 v3-hex：
  外层 = flat-top 六边形（左右为尖角，上下为平边）
  内层 = pointy-top 六边形（上下为尖角）—— 与外层交错 30°
  中心 = 实心圆核
这个"错位嵌套"是原设计的精髓，所有样式变体都保留它。

所有样式用 %%MAIN%% / %%ACCENT%% 占位，导出时按配色替换。
这样「样式 × 配色」是二维矩阵，只需维护两张表。
"""
import math

# ── 几何工具 ────────────────────────────────────────────────────────────


def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return round(cx + r * math.cos(a), 2), round(cy + r * math.sin(a), 2)


def flat_top(cx, cy, r):
    """平边朝上下、左右为尖角的六边形（蜂巢标准朝向）"""
    return [_pt(cx, cy, r, a) for a in (0, 60, 120, 180, 240, 300)]


def pointy_top(cx, cy, r):
    """尖角朝上下的六边形"""
    return [_pt(cx, cy, r, a) for a in (-90, -30, 30, 90, 150, 210)]


def _pts(points):
    return " ".join(f"{x},{y}" for x, y in points)


def _subpath(points):
    return "M " + " L ".join(f"{x} {y}" for x, y in points) + " Z"


def _evenodd(outer, inner):
    """带洞路径：外轮廓 + 内洞，配合 fill-rule=evenodd"""
    return f"{_subpath(outer)} {_subpath(inner)}"


def _ring(cx, cy, r_out, r_in):
    """flat-top 六边形环"""
    return _evenodd(flat_top(cx, cy, r_out), flat_top(cx, cy, r_in))


def _cluster(cx, cy, r, small_ratio=1.0):
    """蜂窝簇：中心单元 + 六个共享边的邻居

    几何要点：
    1) flat-top 六边形的边中点方向为 30/90/150/210/270/330 度，
       「共享一条边」的邻居正落在这六个方向上。
    2) 邻居与中心必须**同朝向**，否则不共边、会互相穿插。
    3) 多边形必须用 <path> 的多段闭合子路径表达 —— 塞进 <polygon points>
       会被当成单个 N 顶点图形，坐标串会被首尾相连画成横穿全图的乱线。
    """
    apothem = (r + r * small_ratio) * 0.8660254
    cells = [(cx, cy, r)]
    for a in (30, 90, 150, 210, 270, 330):
        cells.append((cx + apothem * math.cos(math.radians(a)),
                      cy + apothem * math.sin(math.radians(a)),
                      r * small_ratio))
    return " ".join(_subpath(flat_top(x, y, rr)) for x, y, rr in cells)


# ── 样式定义 ────────────────────────────────────────────────────────────


def _wrap(body):
    return (
        '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">\n'
        f"  {body}\n"
        "</svg>"
    )


def _nest(sw_out, sw_in, core_r=3.6, core_fill="%%MAIN%%"):
    """双层嵌套：外 flat-top + 内 pointy-top + 中心核"""
    return _wrap(
        '<g stroke-linejoin="round">\n'
        f'    <polygon points="{_pts(flat_top(50, 50, 34))}" stroke="%%MAIN%%" stroke-width="{sw_out}"/>\n'
        f'    <polygon points="{_pts(pointy_top(50, 50, 16))}" stroke="%%ACCENT%%" stroke-width="{sw_in}"/>\n'
        "  </g>\n"
        f'  <circle cx="50" cy="50" r="{core_r}" fill="{core_fill}"/>'
    )


def _s1():
    """标准嵌套 —— 与原选定稿结构一致"""
    return _nest(3, 2.6)


def _s2():
    """外实心中空 —— 实心外壳 + 镂空内核 + 强调色核"""
    return _wrap(
        f'  <path d="{_evenodd(flat_top(50, 50, 34), pointy_top(50, 50, 16))}" '
        'fill="%%MAIN%%" fill-rule="evenodd"/>\n'
        '  <circle cx="50" cy="50" r="3.6" fill="%%ACCENT%%"/>'
    )


def _s3():
    """内实心 —— 外描边 + 内层实心"""
    return _wrap(
        '<g stroke-linejoin="round">\n'
        f'    <polygon points="{_pts(flat_top(50, 50, 34))}" stroke="%%MAIN%%" stroke-width="3"/>\n'
        "  </g>\n"
        f'  <polygon points="{_pts(pointy_top(50, 50, 16))}" fill="%%ACCENT%%"/>'
    )


def _s4():
    """蜂房环 —— 六边形环 + 中心核"""
    return _wrap(
        f'  <path d="{_ring(50, 50, 34, 22)}" fill="%%MAIN%%" fill-rule="evenodd"/>\n'
        '  <circle cx="50" cy="50" r="3.6" fill="%%ACCENT%%"/>'
    )


def _s5():
    """三层嵌套 —— 外环 + 中环 + 核"""
    return _wrap(
        '<g stroke-linejoin="round">\n'
        f'    <polygon points="{_pts(flat_top(50, 50, 34))}" stroke="%%MAIN%%" stroke-width="3"/>\n'
        f'    <polygon points="{_pts(flat_top(50, 50, 24.5))}" stroke="%%ACCENT%%" stroke-width="1.7"/>\n'
        "  </g>\n"
        '  <circle cx="50" cy="50" r="3.4" fill="%%ACCENT%%"/>'
    )


def _s6():
    """无核 —— 去掉中心圆，只留双层轮廓"""
    return _nest(3.4, 2.8, core_r=0, core_fill="none").replace(
        '  <circle cx="50" cy="50" r="0" fill="none"/>', ""
    )


def _s7():
    """六边形核 —— 中心核改用小六边形"""
    return _wrap(
        '<g stroke-linejoin="round">\n'
        f'    <polygon points="{_pts(flat_top(50, 50, 34))}" stroke="%%MAIN%%" stroke-width="3"/>\n'
        f'    <polygon points="{_pts(pointy_top(50, 50, 16))}" stroke="%%ACCENT%%" stroke-width="2.6"/>\n'
        "  </g>\n"
        f'  <polygon points="{_pts(pointy_top(50, 50, 6.5))}" fill="%%MAIN%%"/>'
    )


def _s8():
    """蜂窝簇 —— 七格等大共边，中心格用主色高亮"""
    return _wrap(
        '<g stroke-linejoin="round">\n'
        f'    <path d="{_cluster(50, 50, 13.2)}" stroke="%%ACCENT%%" stroke-width="1.9"/>\n'
        "  </g>\n"
        f'  <polygon points="{_pts(flat_top(50, 50, 13.2))}" fill="%%MAIN%%"/>'
    )


def _s9():
    """细线版 —— 同结构，线更轻，适合小尺寸与浅色底"""
    return _nest(2.1, 1.8, core_r=3)


def _s10():
    """粗线版 —— 同结构，线更重，适合大尺寸与深色底"""
    return _nest(4.2, 3.6, core_r=4.2)


STYLES = [
    {"id": "s1-nested", "name": "标准嵌套", "en": "Nested",
     "note": "与原选定稿一致，外轮廓与内轮廓错位 30°",
     "build": _s1},
    {"id": "s2-solid-outer", "name": "外实心中空", "en": "Solid Shell",
     "note": "实心外壳镂空内核，识别度最高", "build": _s2},
    {"id": "s3-solid-inner", "name": "内实心", "en": "Solid Core",
     "note": "外描边内实心，块面更稳", "build": _s3},
    {"id": "s4-ring", "name": "蜂房环", "en": "Hex Ring",
     "note": "粗环 + 强调核，几何感最强", "build": _s4},
    {"id": "s5-triple", "name": "三层嵌套", "en": "Triple",
     "note": "三个同心层级，纵深感更强", "build": _s5},
    {"id": "s6-no-core", "name": "去核轮廓", "en": "No Core",
     "note": "仅留双层轮廓，最克制", "build": _s6},
    {"id": "s7-hex-core", "name": "六边形核", "en": "Hex Core",
     "note": "中心核换成小六边形，与外轮廓同族", "build": _s7},
    {"id": "s8-cluster", "name": "蜂窝簇", "en": "Cluster",
     "note": "中心 + 六邻，直接画出蜂巢结构", "build": _s8},
    {"id": "s9-fine", "name": "细线版", "en": "Fine",
     "note": "线宽减三成，小尺寸与浅底更清爽", "build": _s9},
    {"id": "s10-bold", "name": "粗线版", "en": "Bold",
     "note": "线宽加四成，大尺寸与深底更厚重", "build": _s10},
]
