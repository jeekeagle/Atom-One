"""
Atom 联合锁定组合（Lockup）—— 图标在左 · 字标在右

排版原则（品牌锁定组合的标准做法）：
  1. 光学对齐，不是机械居中。字标（含小写 t/o/m 的 x-height 视觉重量）
     应与图标的**视觉中心**对齐，而不是把两者的包围盒机械居中。
  2. 图标与字标的间距由图标的"空腔"决定 —— 六边形外壳内的空白宽度，
     约为图标宽度的 0.22~0.28 倍。
  3. 字标字号由图标高度反推：图标高 H，字标 cap height ≈ 0.52H，
     这样两者在视觉重量上平级。
  4. 可选副标题（METHOD SYSTEM）置于字标下方，与主标左对齐。
  5. 所有字形已转曲 —— 不依赖系统字体，跨机器渲染一致。
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import wordmark
from styles import STYLES, flat_top, pointy_top, _pts, _subpath, _evenodd, _ring, _cluster

# ── 排版参数 ────────────────────────────────────────────────────────────

LOGO = "Atom"                 # 主字标
TAGLINE = "METHOD SYSTEM"     # 副标题
TRACKING = 60                 # 主标字距（em 千分比）
TAG_TRACKING = 180            # 副标字距（拉开，小字需要更松）
TAG_SIZE_RATIO = 0.22         # 副标字号 / 主标字号
                                # —— 0.22 是在「副标仍舒展」前提下能让副标宽度
                                #    不超过主标（267） 的最大值（236）。
#    副标宽于主标会破坏锁定组合的右侧收边，是品牌规范硬伤。
GAP_RATIO = 0.30              # 图标与字标间距 / 图标高度
CAP_RATIO = 0.40              # 字标 cap height / 图标高度
TAG_GAP = 0.30                # 主标基线到副标顶部 / 图标高度


def _logo_group(style_id, main, accent):
    """取出指定样式的主体图形（不含 viewBox 外壳），返回 path 片段"""
    st = next(s for s in STYLES if s["id"] == style_id)
    svg = st["build"]()
    # 剥掉外层 <svg> 标签与 fill="none"
    body = svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    body = body.replace('fill="none"', "")
    body = body.replace("%%MAIN%%", main).replace("%%ACCENT%%", accent)
    return body.strip()


def build_lockup(style_id="s1-nested", main="#1A1A1A", accent="#8A4A3F",
                 logo=LOGO, tagline=TAGLINE, show_tagline=True,
                 size=100.0, tracking=TRACKING, gap_ratio=GAP_RATIO,
                 cap_ratio=CAP_RATIO, padding_ratio=0.12):
    """生成联合锁定组合 SVG

    size = 图标高度（逻辑单位）。所有元素按此等比缩放。
    返回 (svg_string, viewbox_width, viewbox_height)
    """
    H = size                       # 图标高
    ICON_W = H * 0.86              # 六边形在 100 视框内宽 68 → 比例 0.68，这里用方形盒更稳
    # 六边形实际宽 68/100 = 0.68，视觉上比高度窄，锁定时按视觉重量补偿
    ICON_VIS_W = H * 0.68
    gap = H * gap_ratio

    # 字标：按 cap height 反推字号
    cap, ascent = wordmark.cap_height(100.0)
    font_size = (H * cap_ratio) / cap * 100.0
    logo_d, logo_adv, _ = wordmark.text_paths(logo, size=font_size, tracking=tracking)
    lx0, ly0, lx1, ly1 = wordmark.ink_bounds(logo, size=font_size, tracking=tracking)
    logo_w = lx1 - lx0
    logo_cap = ly1 - ly0          # 已翻转，负值区间；实际高度取 abs

    # 副标题
    if show_tagline and tagline:
        tag_size = font_size * TAG_SIZE_RATIO
        tag_d, tag_adv, _ = wordmark.text_paths(tagline, size=tag_size, tracking=TAG_TRACKING)
        tx0, ty0, tx1, ty1 = wordmark.ink_bounds(tagline, size=tag_size, tracking=TAG_TRACKING)
        tag_w = tx1 - tx0
        tag_h = ty1 - ty0
    else:
        tag_d, tx0, tag_w, tag_h = "", 0, 0, 0

    # ── 垂直排布 ──
    # 图标占 [0, H]
    # 字标：以大写 A 的 cap 中线（视觉中心）对齐图标的视觉中心
    logo_visual_center = (ly0 + ly1) / 2
    icon_vcenter = H * 0.52
    logo_baseline = icon_vcenter - logo_visual_center

    text_x = ICON_VIS_W + gap

    if show_tagline and tagline:
        # 副标紧跟主标下方：主标墨迹底部（基线附近）往下留 TAG_GAP
        tag_cap = abs(tag_h)
        tag_top = logo_baseline + TAG_GAP * H
        tag_baseline = tag_top + tag_cap
        total_h = max(H, tag_baseline)
    else:
        tag_baseline = 0
        total_h = H

    # 水平总宽：主标与副标取较宽者，保持右边界一致
    content_w = text_x + logo_w
    if show_tagline and tagline:
        content_w = max(content_w, text_x + tag_w)

    pad = H * padding_ratio
    vb_w = content_w + pad * 2
    vb_h = total_h + pad * 2

    # ── 拼装 ──
    parts = []
    # 图标：等比放大 100 视框到 H，并水平居中到 ICON_VIS_W
    icon_scale = H / 100.0
    icon_x = (ICON_VIS_W - 100 * icon_scale * 0.68) / 2
    parts.append(f'<g transform="translate({icon_x:.2f},{pad:.2f}) scale({icon_scale:.4f})">')
    parts.append(_logo_group(style_id, main, accent))
    parts.append("</g>")

    # 主字标
    parts.append(f'<path d="{logo_d}" fill="{main}" transform="translate({text_x - lx0:.2f},{logo_baseline + pad:.2f})"/>')

    # 副标题
    if show_tagline and tagline:
        parts.append(f'<path d="{tag_d}" fill="{main}" fill-opacity="0.62" '
                     f'transform="translate({text_x - tx0:.2f},{tag_baseline + pad:.2f})"/>')

    body = "\n  ".join(parts)
    svg = (f'<svg viewBox="0 0 {vb_w:.2f} {vb_h:.2f}" xmlns="http://www.w3.org/2000/svg" '
           f'fill="none">\n  {body}\n</svg>')
    return svg, vb_w, vb_h


def build_lockup_mono(style_id="s1-nested", accent="#8A4A3F", **kw):
    """单色版：主标用 currentColor，便于继承文字颜色"""
    svg, w, h = build_lockup(style_id=style_id, main="currentColor", accent=accent, **kw)
    return svg, w, h
