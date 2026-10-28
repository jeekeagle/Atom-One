"""
Atom 字标 —— 字形转曲生成器

为什么不用 <text>：<text> 依赖系统字体，换一台机器就掉字变形。
品牌资产必须转曲 —— 把字形轮廓烘成路径，任何环境渲染一致。

字标设计决策：
  · 字体 Arial Bold（几何无衬线，笔画粗壮，与六边形 3 单位线宽呼应）
  · 光学调整：字标需与图标做视觉平衡，而非机械居中
  · 字距（tracking）单独可调，用于匹配图标的呼吸感
"""
import pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"

_cache = {}


def _load():
    if "f" not in _cache:
        f = TTFont(FONT_PATH, fontNumber=0)
        _cache["f"] = f
        _cache["cmap"] = f.getBestCmap()
        _cache["gs"] = f.getGlyphSet()
        _cache["upem"] = f["head"].unitsPerEm
    return _cache["f"], _cache["cmap"], _cache["gs"], _cache["upem"]


def glyph_path(ch):
    """单个字符 → SVG path 数据（字体坐标系，y 向上）"""
    _, cmap, gs, _ = _load()
    name = cmap.get(ord(ch))
    if name is None:
        raise KeyError(f"字体缺字形：{ch}")
    pen = SVGPathPen(gs)
    gs[name].draw(pen)
    return pen.getCommands()


def glyph_advance(ch):
    _, cmap, gs, _ = _load()
    return gs[cmap.get(ord(ch))].width


def _glyph_path_transformed(ch, tx, ty, scale, flip_y):
    """把一个字符画成已缩放平移（并可选 y 翻转）的 path

    用 fontTools 的 TransformPen 处理坐标，避免手写 path 解析出错。
    字体坐标 y 向上、基线 y=0；SVG 需 y 向下，故翻转用 y' = -y。
    """
    _, cmap, gs, _ = _load()
    name = cmap.get(ord(ch))
    if name is None:
        raise KeyError(f"字体缺字形：{ch}")
    if flip_y:
        m = Transform(scale, 0, 0, -scale, tx, ty)
    else:
        m = Transform(scale, 0, 0, scale, tx, ty)
    pen = SVGPathPen(gs)
    tpen = TransformPen(pen, m)
    gs[name].draw(tpen)
    return pen.getCommands()


def text_paths(text, size=100.0, tracking=0.0, anchor="left", flip_y=True):
    """整串文字 → (path_d, advance_width, size)

    path 已缩放到 size 并（默认）翻转为 SVG 坐标：基线 y=0，字形向上为负。
    tracking 单位为 em 的千分比。
    """
    _, _, _, upem = _load()
    scale = size / upem
    track_px = tracking / 1000.0 * size

    parts = []
    x_cursor = 0.0
    for ch in text:
        if ch == " ":
            x_cursor += glyph_advance(" ") * scale + track_px
            continue
        adv = glyph_advance(ch) * scale
        d = _glyph_path_transformed(ch, x_cursor, 0.0, scale, flip_y)
        if d:
            parts.append(d)
        x_cursor += adv + track_px

    total_w = x_cursor - (track_px if text and text[-1] != " " else 0)

    if anchor in ("middle", "end"):
        dx = -total_w / 2 if anchor == "middle" else -total_w
        if dx != 0:
            parts = [_shift_path(p, dx) for p in parts]

    return " ".join(parts), total_w, size


def _shift_path(d, dx):
    """给已生成的 path 整体加一个 x 偏移（用 TransformPen 重绘更稳）"""
    import re
    toks = re.findall(r"[MLCQHVZmlcqhvz]|-?\d+\.?\d*", d)
    out = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t in "ML":
            out.append(f"{t}{float(toks[i+1])+dx:.2f} {float(toks[i+2]):.2f}")
            i += 3
        elif t == "H":
            out.append(f"H{float(toks[i+1])+dx:.2f}"); i += 2
        elif t == "V":
            out.append(f"V{float(toks[i+1]):.2f}"); i += 2
        elif t == "C":
            v = [float(x) for x in toks[i+1:i+7]]
            v[0] += dx; v[2] += dx; v[4] += dx
            out.append("C" + " ".join(f"{v[j]:.2f}" for j in range(6))); i += 7
        elif t == "Q":
            v = [float(x) for x in toks[i+1:i+5]]
            v[0] += dx; v[2] += dx
            out.append("Q" + " ".join(f"{v[j]:.2f}" for j in range(4))); i += 5
        else:
            i += 1
    return "".join(out)


def cap_height(size=100.0, font_path=None):
    """大写字母的实际墨迹高度（用于字标与图标的光学对齐）

    返回 (cap_height, ascent_from_baseline)
    """
    global FONT_PATH
    old = FONT_PATH
    if font_path:
        FONT_PATH = font_path
    try:
        _cache.clear()
        f, cmap, gs, upem = _load()
        from fontTools.pens.boundsPen import BoundsPen
        bp = BoundsPen(gs)
        gs[cmap[ord("H")]].draw(bp)
        top, bot = bp.bounds[3], bp.bounds[1]
        return (top - bot) * size / upem, top * size / upem
    finally:
        FONT_PATH = old
        _cache.clear()


def ink_bounds(text, size=100.0, tracking=0.0, flip_y=True):
    """文字的实际墨迹包围盒 —— 排版对齐必须用这个，而不是 advance 宽度

    返回 (x0, y0, x1, y1)，坐标基于基线 y=0、y 向上为正（未翻转）或向下（已翻转）
    """
    _, _, _, upem = _load()
    scale = size / upem
    track_px = tracking / 1000.0 * size

    from fontTools.pens.boundsPen import BoundsPen

    xs, ys = [], []
    x_cursor = 0.0
    for ch in text:
        if ch == " ":
            x_cursor += glyph_advance(" ") * scale + track_px
            continue
        bp = BoundsPen(_cache["gs"])
        _cache["gs"][_cache["cmap"][ord(ch)]].draw(bp)
        if bp.bounds:
            bx0, by0, bx1, by1 = bp.bounds
            xs += [bx0 * scale + x_cursor, bx1 * scale + x_cursor]
            ys += [by0 * scale, by1 * scale]
        x_cursor += glyph_advance(ch) * scale + track_px

    if not xs:
        return 0, 0, 0, 0
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    if flip_y:
        y0, y1 = -y1, -y0
    return x0, y0, x1, y1
