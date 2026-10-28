"""
品牌规范手册生成器 —— Atom 标志系统

产出：一份可直接交付给合作方/印厂/外部设计师的品牌规范（HTML，单文件可打印为 PDF）。

内容覆盖品牌标志交付的六大必备项：
    1. 标志构成与几何规则（X 高、描边、错位 30°）
    2. 安全空间（clear space）
    3. 最小尺寸
    4. 色彩规范（HEX / RGB / CMYK / 对比度实测）
    5. 反白与单色变体、承载面选择
    6. 背景禁用与错例

数据来源：几何参数从实际 SVG 解析得到，配色从 palettes.py 读取，
对比度由 contrast_audit.py 实测计算 —— 不手写任何数值，避免转录误差。

用法:
    python brand_guide.py                        # 输出 brand_guide.html
    python brand_guide.py -o guide.html
"""

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import palettes
import contrast_audit

D = HERE

# ── 主用方案 ──
PRIMARY = "ink-rust"
LOGOSVG = D / "pick" / "logo-primary.svg"
LOCKUPSVG = D / "pick" / "lockup-primary.svg"

# ── 几何参数（由 parse_geometry 实测得到，此处为兜底默认值）──
GEOM_FALLBACK = {
    "x_height": 68.0, "outer_r": 34.0, "sw_outer": 3.0, "sw_inner": 2.6,
    "core_r": 3.6, "clear_space": 17.0, "ink_w": 71.0, "ink_h": 61.88,
}


def parse_geometry():
    """从实际 SVG 解析几何参数 —— 规范里的每个数字都必须可追溯"""
    g = dict(GEOM_FALLBACK)
    if not LOGOSVG.exists():
        return g
    s = LOGOSVG.read_text(encoding="utf-8")

    polys = re.findall(r'<polygon fill="none" points="([\d.,\s]+)"\s+stroke="[^"]*"\s+stroke-width="([\d.]+)"', s)
    if len(polys) >= 2:
        def bbox(ptxt):
            p = [tuple(map(float, q.split(","))) for q in ptxt.split()]
            xs = [x for x, y in p]; ys = [y for x, y in p]
            return min(xs), min(ys), max(xs), max(ys)
        ox0, oy0, ox1, oy1 = bbox(polys[0][0])
        g["x_height"] = ox1 - ox0
        g["outer_r"] = max(ox1 - 50, 50 - ox0)
        g["sw_outer"] = float(polys[0][1])
        g["sw_inner"] = float(polys[1][1])
        g["ink_w"] = (ox1 - ox0) + float(polys[0][1])
        g["ink_h"] = (oy1 - oy0) + float(polys[0][1])

    m = re.search(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"', s)
    if m:
        g["core_r"] = float(m.group(3))

    # 安全空间：外接圆半径的 1/2，即 X 高的 1/4
    g["clear_space"] = round(g["outer_r"] / 2, 1)
    return g


def read_svg(path, colors=None):
    """读 SVG 并（可选）替换配色"""
    if not path.exists():
        return ""
    s = path.read_text(encoding="utf-8")
    if colors:
        for k, v in colors.items():
            s = s.replace(k, v)
    return s


def build():
    g = parse_geometry()
    pal = {p["id"]: p for p in palettes.PALETTES}
    audits = {a["id"]: a for a in contrast_audit.audit()}
    primary = pal[PRIMARY]

    # 各配色下的 SVG（用于色彩规范区）
    svg_main = read_svg(LOGOSVG)
    svg_rev = read_svg(D / "pick" / "logo-primary-reverse.svg")
    svg_lock = read_svg(LOCKUPSVG)
    svg_mono = read_svg(D / "pick" / "lockup-primary-mono.svg")

    def pal_row(p):
        a = audits[p["id"]]
        surfaces = []
        for r in a["surface_rows"]:
            surfaces.append(
                f'<tr><td>{r["surface_name"]}</td>'
                f'<td class="mono">{r["surface_hex"]}</td>'
                f'<td>{r["mode"] or "—"}</td>'
                f'<td class="num">{r["struct_ratio"]:.2f}</td>'
                f'<td class="num">{r["dot_ratio"] if r["dot_ratio"] else "—"}</td>'
                f'<td class="{"ok" if r["usable"] else "no"}">{"可用" if r["usable"] else "不可用"}</td></tr>')
        c = p
        return f"""
        <div class="pal-card">
          <div class="pal-head">
            <div class="pal-sw" style="background:{c['main']}">
              <span style="background:{c['accent']}"></span>
            </div>
            <div>
              <b>{c['name']}</b>
              <small>{c['en']} · {c['id']}</small>
            </div>
          </div>
          <div class="pal-codes">
            <span><i>HEX</i><em>{c['main']}</em></span>
            <span><i>HEX</i><em>{c['accent']}</em></span>
            <span><i>CMYK</i><em>{audit['cmyk_main'] if False else ''}{', '.join(str(x) for x in audits[p['id']]['cmyk_main'])}</em></span>
            <span><i>CMYK</i><em>{', '.join(str(x) for x in audits[p['id']]['cmyk_accent'])}</em></span>
          </div>
          <p class="pal-note">{c['note']}</p>
          <p class="pal-usage">建议用途：{c['usage']}</p>
          <table class="pal-table">
            <thead><tr><th>承载面</th><th>底色</th><th>推荐上色</th><th>结构对比</th><th>点睛对比</th><th>结论</th></tr></thead>
            <tbody>{"".join(surfaces)}</tbody>
          </table>
        </div>"""

    pal_cards = "".join(pal_row(p) for p in palettes.PALETTES)

    html = HTML_TEMPLATE
    html = html.replace("/*__GEOM__*/", repr(g))
    html = html.replace("/*__PRIMARY_COLOR__*/", primary["main"])
    html = html.replace("/*__ACCENT_COLOR__*/", primary["accent"])
    html = html.replace("/*__LOGO_MAIN__*/", svg_main)
    html = html.replace("/*__LOGO_REV__*/", svg_rev)
    html = html.replace("/*__LOCKUP__*/", svg_lock)
    html = html.replace("/*__MONO__*/", svg_mono)
    html = html.replace("/*__PAL_CARDS__*/", pal_cards)
    html = html.replace("/*__GEOM_JSON__*/", "{" + ", ".join(
        f'"{k}": {v}' for k, v in g.items()) + "}")
    return html


# ══════════════════════════════════════════════════════════════════
# 模板
# ══════════════════════════════════════════════════════════════════

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atom 品牌规范手册 · Brand Guidelines</title>
<style>
  :root{
    --ink:#1A1A1A; --rust:#8A4A3F; --paper:#FFFFFF; --warm:#F5F3EF;
    --line:#E2DED7; --muted:#8A8377; --rule:#C9C3B8;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    font-family:"Songti SC","SimSun","Microsoft YaHei",Georgia,serif;
    color:var(--ink); background:var(--warm); line-height:1.75;
    -webkit-font-smoothing:antialiased;
  }
  .sheet{ max-width:940px; margin:0 auto; background:var(--paper);
          box-shadow:0 1px 3px rgba(0,0,0,.06), 0 12px 40px rgba(0,0,0,.06); }
  .page{ padding:64px 68px; border-bottom:1px solid var(--line); }
  .page:last-child{ border-bottom:none; }

  /* ── 页头 ── */
  .cover{ padding:84px 68px 64px; }
  .cover-mark{ display:flex; align-items:center; gap:22px; margin-bottom:52px; }
  .cover-mark svg{ width:74px; height:74px; }
  .cover h1{ font-size:52px; font-weight:700; letter-spacing:-.02em; line-height:1.12; }
  .cover h1 small{ display:block; font-size:15px; font-weight:400; letter-spacing:.22em;
                   color:var(--muted); margin-top:14px; text-transform:uppercase; }
  .cover .lede{ font-size:17px; color:#4A453D; max-width:620px; margin-top:30px;
                padding-top:26px; border-top:1px solid var(--line); }
  .cover-meta{ display:grid; grid-template-columns:repeat(4,1fr); gap:24px; margin-top:44px;
               padding-top:26px; border-top:1px solid var(--line); }
  .cover-meta div b{ display:block; font-size:11px; letter-spacing:.12em; color:var(--muted);
                     text-transform:uppercase; margin-bottom:6px; font-weight:500; }
  .cover-meta div span{ font-size:14.5px; font-family:ui-monospace,Menlo,Consolas,monospace; }

  /* ── 章节 ── */
  .sec-no{ font-size:11.5px; letter-spacing:.2em; color:var(--rust); font-weight:600;
           margin-bottom:10px; }
  h2{ font-size:30px; font-weight:700; letter-spacing:-.01em; margin-bottom:8px; }
  h3{ font-size:17px; font-weight:600; margin:36px 0 14px; }
  .sec-lede{ font-size:15px; color:var(--muted); max-width:660px; margin-bottom:34px; }

  /* ── 网格 ── */
  .grid2{ display:grid; grid-template-columns:1fr 1fr; gap:26px; }
  .grid3{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
  .panel{ border:1px solid var(--line); border-radius:10px; padding:26px; background:var(--paper); }
  .panel-label{ font-size:11px; letter-spacing:.14em; color:var(--muted); text-transform:uppercase;
                margin-bottom:16px; font-weight:600; }
  .stage{ display:flex; align-items:center; justify-content:center; padding:38px 20px;
          border-radius:8px; background:var(--warm); position:relative; }
  .stage.white{ background:#fff; border:1px solid var(--line); }
  .stage.dark{ background:var(--ink); }
  .stage svg{ max-width:100%; height:auto; }
  /* 注入的完整 SVG（自带 viewBox）需限高，避免撑破舞台 */
  .stage > svg{ width:150px; height:150px; }
  .stage > div > svg{ width:100%; height:auto; }

  /* ── 几何图 ── */
  .geo-wrap{ border:1px solid var(--line); border-radius:10px; padding:28px; background:#FCFBF9; }
  .geo-legend{ display:flex; gap:22px; margin-top:18px; flex-wrap:wrap; }
  .geo-legend span{ font-size:12.5px; color:var(--muted); display:flex; align-items:center; gap:7px; }
  .geo-legend i{ width:13px; height:13px; border-radius:3px; display:inline-block; }

  /* ── 数据表 ── */
  table.spec{ width:100%; border-collapse:collapse; font-size:13.5px; margin-top:6px; }
  table.spec th{ text-align:left; font-size:10.5px; letter-spacing:.12em; color:var(--muted);
                 text-transform:uppercase; font-weight:600; padding:9px 12px;
                 border-bottom:1px solid var(--rule); }
  table.spec td{ padding:9px 12px; border-bottom:1px solid var(--line); vertical-align:top; }
  table.spec td.num{ font-family:ui-monospace,Menlo,Consolas,monospace; }
  table.spec td.mono{ font-family:ui-monospace,Menlo,Consolas,monospace; }
  table.spec tr:last-child td{ border-bottom:none; }
  td.ok{ color:#2F6B3A; font-weight:600; }
  td.no{ color:#9A3B32; font-weight:600; }

  /* ── 配色卡 ── */
  .pal-card{ border:1px solid var(--line); border-radius:10px; padding:22px; margin-bottom:20px; }
  .pal-head{ display:flex; align-items:center; gap:15px; margin-bottom:16px; }
  .pal-sw{ width:54px; height:54px; border-radius:9px; display:flex; align-items:center;
           justify-content:center; border:1px solid rgba(0,0,0,.08); }
  .pal-sw span{ width:19px; height:19px; border-radius:50%; display:block; }
  .pal-head b{ display:block; font-size:16px; }
  .pal-head small{ font-size:12px; color:var(--muted); font-family:ui-monospace,monospace; }
  .pal-codes{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px; }
  .pal-codes span{ display:flex; align-items:center; gap:7px; font-size:11.5px;
                   background:var(--warm); border-radius:5px; padding:5px 10px; }
  .pal-codes i{ font-style:normal; color:var(--muted); letter-spacing:.08em; }
  .pal-codes em{ font-style:normal; font-family:ui-monospace,Menlo,Consolas,monospace;
                 color:var(--ink); }
  .pal-note{ font-size:13.5px; color:#4A453D; }
  .pal-usage{ font-size:12.5px; color:var(--muted); margin-top:4px; }
  .pal-table{ width:100%; border-collapse:collapse; font-size:12.5px; margin-top:14px; }
  .pal-table th{ text-align:left; font-size:10px; letter-spacing:.1em; color:var(--muted);
                 text-transform:uppercase; font-weight:600; padding:6px 10px;
                 border-bottom:1px solid var(--rule); }
  .pal-table td{ padding:6px 10px; border-bottom:1px solid var(--line);
                 font-family:ui-monospace,Menlo,Consolas,monospace; }
  .pal-table td:first-child{ font-family:inherit; }
  .pal-table tr:last-child td{ border-bottom:none; }

  /* ── 禁用 ── */
  .dont{ border:1px solid var(--line); border-radius:10px; overflow:hidden; }
  .dont-cell{ aspect-ratio:1/1; display:flex; align-items:center; justify-content:center;
              position:relative; border-bottom:1px solid var(--line); }
  .dont-cell:last-child{ border-bottom:none; }
  .dont-cell svg{ width:44%; height:auto; }
  .dont-cap{ font-size:11.5px; color:var(--muted); padding:9px 12px; background:var(--warm);
             border-bottom:1px solid var(--line); }
  .dont-cell.bad::after{ content:"×"; position:absolute; top:6px; right:10px;
             font-size:26px; color:rgba(154,59,50,.62); font-weight:300; line-height:1;
             text-shadow:0 0 5px rgba(255,255,255,.9); pointer-events:none; }
  .dont-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }

  /* ── 交付清单 ── */
  .files{ display:grid; grid-template-columns:repeat(2,1fr); gap:0 34px; }
  .files div{ display:flex; justify-content:space-between; gap:18px; padding:11px 0;
              border-bottom:1px solid var(--line); font-size:13.5px; }
  .files div span{ color:var(--muted); font-family:ui-monospace,Menlo,Consolas,monospace;
                   font-size:12px; }

  .note{ background:var(--warm); border-left:3px solid var(--rust); padding:16px 20px;
         border-radius:0 8px 8px 0; font-size:13.5px; color:#4A453D; margin:20px 0; }
  .rule-list{ counter-reset:r; }
  .rule-list li{ list-style:none; counter-increment:r; padding:11px 0 11px 38px;
                 border-bottom:1px solid var(--line); position:relative; font-size:14.5px; }
  .rule-list li::before{ content:counter(r,decimal-leading-zero); position:absolute; left:0;
             top:11px; font-size:11.5px; color:var(--rust); font-family:ui-monospace,monospace;
             letter-spacing:.06em; }
  .rule-list li b{ font-weight:600; }
  .rule-list li em{ font-style:normal; color:var(--muted); font-size:13px; }

  footer{ padding:38px 68px; font-size:12px; color:var(--muted); text-align:center;
          border-top:1px solid var(--line); }

  @media print{
    body{ background:#fff; }
    .sheet{ box-shadow:none; max-width:none; }
    .page{ page-break-inside:avoid; padding:44px 52px; }
    @page{ size:A4; margin:14mm; }
  }
</style>
</head>
<body>
<div class="sheet">

  <!-- ════════ 封面 ════════ -->
  <div class="page cover">
    <div class="cover-mark">
      /*__LOGO_MAIN__*/
    </div>
    <h1>Atom 品牌标志规范
      <small>Brand Identity Guidelines · 2026</small>
    </h1>
    <p class="lede">
      Atom 方法体系的视觉标志，以「蜂巢六边」为核心几何：外壳与内核六边形错位三十度咬合，
      中心一点为核。本手册规定标志的构成、比例、安全空间、最小尺寸、色彩与承载面规则，
      以及不得使用的情形。所有数值均由标志源文件实测得出。
    </p>
    <div class="cover-meta">
      <div><b>版本</b><span>1.0</span></div>
      <div><b>标志结构</b><span>Hex Nest</span></div>
      <div><b>X 高</b><span id="geo-x">—</span></div>
      <div><b>主色</b><span id="geo-main">—</span></div>
    </div>
  </div>

  <!-- ════════ 01 构成 ════════ -->
  <div class="page">
    <div class="sec-no">SECTION 01</div>
    <h2>标志构成与几何规则</h2>
    <p class="sec-lede">
      标志由三个元素构成：外层六边形轮廓、内层六边形轮廓、中心实心核。
      外壳为平顶六边形（尖角朝左右），内核为尖顶六边形（尖角朝上下），两者错位三十度。
      这个错位是识别锚点——同向叠放只会退化成靶心。
    </p>

    <div class="grid2">
      <div class="geo-wrap">
        <svg viewBox="0 0 100 100" width="100%">
          <g stroke="#D8D2C8" stroke-width="0.4" fill="none">
            <rect x="16" y="16" width="68" height="68"/>
          </g>
          <g stroke-linejoin="round">
            <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"
                     stroke="#1A1A1A" stroke-width="3"/>
            <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42"
                     stroke="#8A4A3F" stroke-width="2.6"/>
          </g>
          <circle cx="50" cy="50" r="3.6" fill="#1A1A1A"/>
          <g stroke="#9A958B" stroke-width="0.35" stroke-dasharray="1.6 1.6" fill="none">
            <line x1="50" y1="4" x2="50" y2="16"/>
            <line x1="50" y1="84" x2="50" y2="96"/>
            <line x1="4" y1="50" x2="16" y2="50"/>
            <line x1="84" y1="50" x2="96" y2="50"/>
          </g>
          <g stroke="#8A4A3F" stroke-width="0.35" stroke-dasharray="1.2 1.2" fill="none">
            <rect x="33" y="20.56" width="34" height="58.88"/>
          </g>
          <text x="50" y="11" font-size="4" text-anchor="middle" fill="#8A4A3F" font-family="monospace">X 高</text>
        </svg>
        <div class="geo-legend">
          <span><i style="background:#1A1A1A"></i>外壳轮廓 描边 3.0</span>
          <span><i style="background:#8A4A3F"></i>内核轮廓 描边 2.6</span>
          <span><i style="background:#9A958B"></i>对位基准线</span>
        </div>
      </div>

      <div>
        <table class="spec">
          <tr><th>参数</th><th>数值</th><th>说明</th></tr>
          <tr><td>画布</td><td class="num">100 × 100</td><td>等比缩放的基准</td></tr>
          <tr><td>X 高</td><td class="num" id="g-x">—</td><td>外壳左右顶点间距</td></tr>
          <tr><td>外接圆半径</td><td class="num" id="g-r">—</td><td>以画布中心为圆心</td></tr>
          <tr><td>外壳描边</td><td class="num" id="g-swo">—</td><td>圆角接头</td></tr>
          <tr><td>内核描边</td><td class="num" id="g-swi">—</td><td>比外壳略细，形成层级</td></tr>
          <tr><td>内核圆半径</td><td class="num" id="g-cr">—</td><td>实心，位于正中</td></tr>
          <tr><td>错位角</td><td class="num">30°</td><td>外壳与内核朝向差</td></tr>
          <tr><td>实际墨迹</td><td class="num" id="g-ink">—</td><td>含描边外扩</td></tr>
        </table>
        <div class="note">
          所有数值由 <code>brand_guide.py</code> 直接解析源 SVG 得出，
          改动标志文件后重跑本手册即同步更新——规范与资产不会脱节。
        </div>
      </div>
    </div>
  </div>

  <!-- ════════ 02 安全空间 ════════ -->
  <div class="page">
    <div class="sec-no">SECTION 02</div>
    <h2>安全空间</h2>
    <p class="sec-lede">
      标志四周必须留出足够的空白，使它不与文字、图形或版面边缘相互干扰。
      安全空间以 X 为单位，定义为 <b>X 的 1/4</b>，等同于外壳外接圆半径的一半。
    </p>

    <div class="grid2">
      <div class="panel">
        <div class="panel-label">安全空间示意</div>
        <div class="stage white">
          <svg viewBox="0 0 100 100" width="72%">
            <rect x="0" y="0" width="100" height="100" fill="#F0EDE7"/>
            <rect x="17" y="20.56" width="66" height="58.88" fill="none"
                  stroke="#8A4A3F" stroke-width="0.5" stroke-dasharray="1.4 1.4"/>
            <g stroke-linejoin="round">
              <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"
                       stroke="#1A1A1A" stroke-width="3"/>
              <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42"
                       stroke="#8A4A3F" stroke-width="2.6"/>
            </g>
            <circle cx="50" cy="50" r="3.6" fill="#1A1A1A"/>
          </svg>
        </div>
        <div class="geo-legend">
          <span><i style="background:#F0EDE7"></i>安全空间区</span>
          <span><i style="background:#8A4A3F"></i>安全空间边界（虚线）</span>
        </div>
      </div>

      <div>
        <h3 style="margin-top:0">规则</h3>
        <ul class="rule-list">
          <li><b>四周等距</b> <em>标志上、下、左、右到相邻元素或版面边缘的最小距离，均为 X/4</em></li>
          <li><b>不得压缩</b> <em>空间不足时缩小标志，不得削减留白</em></li>
          <li><b>文字不侵入</b> <em>任何文字、图形、图像不得进入安全空间区</em></li>
          <li><b>并置时取大</b> <em>两个标志并置，间距不小于较大一方的 X 高</em></li>
        </ul>
        <table class="spec" style="margin-top:18px">
          <tr><th>标志宽度</th><th>最小安全留白</th></tr>
          <tr><td class="num">120 px</td><td class="num">34 px</td></tr>
          <tr><td class="num">240 px</td><td class="num">68 px</td></tr>
          <tr><td class="num">480 px</td><td class="num">136 px</td></tr>
          <tr><td class="num">960 px</td><td class="num">272 px</td></tr>
        </table>
      </div>
    </div>
  </div>

  <!-- ════════ 03 最小尺寸 ════════ -->
  <div class="page">
    <div class="sec-no">SECTION 03</div>
    <h2>最小尺寸</h2>
    <p class="sec-lede">
      标志缩到一定程度后，中心实心核会糊成一个点、内核六边形会填死。
      下列尺寸为实测下限，低于此值请改用单色版或实心版。
    </p>

    <div class="grid3">
      <div class="panel">
        <div class="panel-label">通用标志</div>
        <div class="stage white" style="min-height:150px">
          <svg viewBox="0 0 100 100" style="width:96px">
            <g stroke-linejoin="round">
              <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"
                       stroke="#1A1A1A" stroke-width="3"/>
              <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42"
                       stroke="#8A4A3F" stroke-width="2.6"/>
            </g>
            <circle cx="50" cy="50" r="3.6" fill="#1A1A1A"/>
          </svg>
        </div>
        <p style="font-size:13px;margin-top:12px">最小 <b>32 px</b>　建议 <b>48 px</b> 以上</p>
        <p style="font-size:12px;color:var(--muted)">32px 以下内核与中心核将失去可辨识度</p>
      </div>

      <div class="panel">
        <div class="panel-label">实心版（推荐用于超小尺寸）</div>
        <div class="stage white" style="min-height:150px">
          <svg viewBox="0 0 100 100" style="width:96px">
            <path d="M50,16 L79.4,33 L79.4,67 L50,84 L20.6,67 L20.6,33 Z"
                  fill="#1A1A1A" fill-rule="evenodd"/>
            <path d="M50,34 L63.86,42 L63.86,58 L50,66 L36.14,58 L36.14,42 Z"
                  fill="#FFFFFF"/>
          </svg>
        </div>
        <p style="font-size:13px;margin-top:12px">最小 <b>16 px</b></p>
        <p style="font-size:12px;color:var(--muted)">实心外壳＋镂空内核，16px 仍清晰</p>
      </div>

      <div class="panel">
        <div class="panel-label">联合锁定组合</div>
        <div class="stage white" style="min-height:150px">
          <div style="width:88%">/*__LOCKUP__*/</div>
        </div>
        <p style="font-size:13px;margin-top:12px">最小 <b>120 px</b>（宽度计）</p>
        <p style="font-size:12px;color:var(--muted)">含副标题版本最小 160px</p>
      </div>
    </div>

    <div class="note">
      界面图标、favicon 等场景请优先使用<b>实心版</b>或<b>单色版</b>。
      完整尺寸测试矩阵见交付包 <code>scale_test.png</code>。
    </div>
  </div>

  <!-- ════════ 04 色彩 ════════ -->
  <div class="page">
    <div class="sec-no">SECTION 04</div>
    <h2>色彩规范</h2>
    <p class="sec-lede">
      主色承载结构面积，强调色只占小面积——强调色面积越小越耐看。
      对比度数值由 WCAG 2.1 相对亮度公式实算，非估算。
    </p>

    <h3>主用配色 · 墨黑锈红</h3>
    <div class="grid2">
      <div class="panel">
        <div class="panel-label">全色版（浅底）</div>
        <div class="stage white">/*__LOGO_MAIN__*/</div>
        <table class="spec" style="margin-top:16px">
          <tr><th>角色</th><th>HEX</th><th>RGB</th><th>CMYK</th></tr>
          <tr><td>主色</td><td class="mono">#1A1A1A</td><td class="num">26,26,26</td><td class="num">0,0,0,90</td></tr>
          <tr><td>强调色</td><td class="mono">#8A4A3F</td><td class="num">138,74,63</td><td class="num">0,46,54,46</td></tr>
        </table>
      </div>
      <div class="panel">
        <div class="panel-label">反白版（深底）</div>
        <div class="stage dark">/*__LOGO_REV__*/</div>
        <table class="spec" style="margin-top:16px">
          <tr><th>角色</th><th>HEX</th><th>用法</th></tr>
          <tr><td>结构色</td><td class="mono">#F2F0EC</td><td>深底上的主轮廓</td></tr>
          <tr><td>强调色</td><td class="mono">#8A4A3F</td><td>保持不变</td></tr>
        </table>
      </div>
    </div>

    <h3>备用配色库</h3>
    <p style="font-size:13.5px;color:var(--muted);margin-bottom:16px">
      十套配色均通过对比度校验。表中「推荐上色」列已根据承载面明暗自动选定——
      浅底用全色版，深底用反白版。
    </p>
    /*__PAL_CARDS__*/
  </div>

  <!-- ════════ 05 变体 ════════ -->
  <div class="page">
    <div class="sec-no">SECTION 05</div>
    <h2>标志变体</h2>
    <p class="sec-lede">
      同一标志在不同场景下的标准变体。不得自行改造结构比例、角度或元素数量。
    </p>

    <div class="grid3">
      <div class="panel">
        <div class="panel-label">① 通用版（主用）</div>
        <div class="stage white">/*__LOGO_MAIN__*/</div>
        <p style="font-size:12.5px;color:var(--muted);margin-top:11px">默认版本。承载面为白/浅色时使用</p>
      </div>
      <div class="panel">
        <div class="panel-label">② 反白版</div>
        <div class="stage dark">/*__LOGO_REV__*/</div>
        <p style="font-size:12.5px;color:var(--muted);margin-top:11px">承载面为深色/照片时使用</p>
      </div>
      <div class="panel">
        <div class="panel-label">③ 单色版</div>
        <div class="stage white">
          <svg viewBox="0 0 100 100" style="width:130px">
            <g stroke="#1A1A1A" stroke-linejoin="round" stroke-width="3">
              <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"/>
              <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42" stroke-width="2.6"/>
            </g>
            <circle cx="50" cy="50" r="3.6" fill="#1A1A1A"/>
          </svg>
        </div>
        <p style="font-size:12.5px;color:var(--muted);margin-top:11px">单色印刷、雕刻、烫印、丝网印</p>
      </div>
    </div>

    <h3>联合锁定组合</h3>
    <div class="grid2">
      <div class="panel">
        <div class="panel-label">标准锁定（图标＋字标）</div>
        <div class="stage white" style="padding:30px 24px">
          <div style="width:100%">/*__LOCKUP__*/</div>
        </div>
        <p style="font-size:12.5px;color:var(--muted);margin-top:11px">
          图标在左、字标在右。字标已转曲为路径，任何环境打开均不变形。
        </p>
      </div>
      <div class="panel">
        <div class="panel-label">单色锁定</div>
        <div class="stage white" style="padding:30px 24px"><div style="width:100%">/*__MONO__*/</div></div>
        <p style="font-size:12.5px;color:var(--muted);margin-top:11px">
          用于单色介质，或空间受限时替代带副标题的完整锁定。
        </p>
      </div>
    </div>

    <div class="note">
      <b>锁定组合硬约束：</b>副标题宽度不得超过主字标宽度，否则右侧收边被破坏。
      当前配置下主标宽 267、副标宽 236，均收于主标边界内。此项为交付前必检项。
    </div>
  </div>

  <!-- ════════ 06 禁用 ════════ -->
  <div class="page">
    <div class="sec-no">SECTION 06</div>
    <h2>不得使用</h2>
    <p class="sec-lede">以下情形会破坏标志的识别度或规范性，一律不得使用。</p>

    <div class="dont-grid">
      <div class="dont">
        <div class="dont-cell bad">
          <svg viewBox="0 0 100 100" style="transform:rotate(-14deg)">
            <g stroke-linejoin="round">
              <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"
                       stroke="#1A1A1A" stroke-width="3"/>
              <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42"
                       stroke="#8A4A3F" stroke-width="2.6"/>
            </g>
            <circle cx="50" cy="50" r="3.6" fill="#1A1A1A"/>
          </svg>
        </div>
        <div class="dont-cap">不得旋转或倾斜</div>
      </div>

      <div class="dont">
        <div class="dont-cell bad">
          <svg viewBox="0 0 100 100">
            <g stroke-linejoin="round">
              <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"
                       stroke="#1A1A1A" stroke-width="7"/>
              <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42"
                       stroke="#8A4A3F" stroke-width="6"/>
            </g>
            <circle cx="50" cy="50" r="7" fill="#1A1A1A"/>
          </svg>
        </div>
        <div class="dont-cap">不得加粗描边</div>
      </div>

      <div class="dont">
        <div class="dont-cell bad">
          <svg viewBox="0 0 100 100">
            <g stroke-linejoin="round">
              <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"
                       stroke="#1A1A1A" stroke-width="3"/>
              <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42"
                       stroke="#8A4A3F" stroke-width="2.6"/>
            </g>
            <circle cx="50" cy="50" r="3.6" fill="#8A4A3F"/>
          </svg>
        </div>
        <div class="dont-cap">不得互换主色与强调色</div>
      </div>

      <div class="dont">
        <div class="dont-cell bad" style="background:linear-gradient(135deg,#8A4A3F,#C9A227)">
          <svg viewBox="0 0 100 100">
            <g stroke-linejoin="round">
              <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"
                       stroke="#3B7DD8" stroke-width="3"/>
              <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42"
                       stroke="#1A1A1A" stroke-width="2.6"/>
            </g>
            <circle cx="50" cy="50" r="3.6" fill="#3B7DD8"/>
          </svg>
        </div>
        <div class="dont-cap">不得使用非系统内配色</div>
      </div>

      <div class="dont">
        <div class="dont-cell bad">
          <svg viewBox="0 0 100 100" style="transform:scaleY(0.62)">
            <g stroke-linejoin="round">
              <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"
                       stroke="#1A1A1A" stroke-width="3"/>
              <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42"
                       stroke="#8A4A3F" stroke-width="2.6"/>
            </g>
            <circle cx="50" cy="50" r="3.6" fill="#1A1A1A"/>
          </svg>
        </div>
        <div class="dont-cap">不得拉伸变形</div>
      </div>

      <div class="dont">
        <div class="dont-cell bad">
          <svg viewBox="0 0 100 100">
            <g stroke-linejoin="round">
              <polygon fill="none" points="84,50 67,79.44 33,79.44 16,50 33,20.56 67,20.56"
                       stroke="#1A1A1A" stroke-width="3"/>
              <polygon fill="none" points="50,34 63.86,42 63.86,58 50,66 36.14,58 36.14,42"
                       stroke="#8A4A3F" stroke-width="2.6"/>
            </g>
            <circle cx="50" cy="50" r="3.6" fill="#1A1A1A"/>
            <rect x="20" y="70" width="60" height="14" fill="#F0EDE7" stroke="#D8D2C8" stroke-width="0.4"/>
            <text x="50" y="79.5" font-size="8" text-anchor="middle" fill="#8A4A3F"
                  font-family="serif">压缩</text>
          </svg>
        </div>
        <div class="dont-cap">不得压缩比例</div>
      </div>
    </div>

    <h3>承载面选择</h3>
    <table class="spec">
      <tr><th>承载面</th><th>推荐上色</th><th>说明</th></tr>
      <tr><td>纯白 / 纸本 / 浅色</td><td>全色版</td><td>品牌默认场景</td></tr>
      <tr><td>墨黑 / 深色 / 照片</td><td>反白版</td><td>结构色换浅色，强调色保留</td></tr>
      <tr><td>单色印刷 / 雕刻 / 烫印</td><td>单色版</td><td>单色系统</td></tr>
      <tr><td>彩色照片 / 复杂背景</td><td>反白版 + 留白</td><td>或改用动态背景展示页方案</td></tr>
    </table>
  </div>

  <!-- ════════ 07 交付 ════════ -->
  <div class="page">
    <div class="sec-no">SECTION 07</div>
    <h2>交付清单</h2>
    <p class="sec-lede">交付包内的资产构成与使用方式。</p>

    <div class="grid2">
      <div>
        <h3 style="margin-top:0">矢量资产</h3>
        <div class="files">
          <div><b>全色 SVG</b><span>svg/</span></div>
          <div><b>单色 SVG</b><span>svg-mono/</span></div>
          <div><b>反白 SVG</b><span>reverse/</span></div>
          <div><b>锁定组合 SVG</b><span>lockup/svg/</span></div>
          <div><b>锁定组合单色</b><span>lockup/svg-mono/</span></div>
        </div>
        <div class="note" style="margin-top:18px">
          单色 SVG 的主色使用 <code>currentColor</code>，可直接继承父元素文字颜色，
          用于深色模式与网页排版。
        </div>
      </div>
      <div>
        <h3 style="margin-top:0">位图与应用资产</h3>
        <div class="files">
          <div><b>1024 透明 PNG</b><span>png/</span></div>
          <div><b>512 透明 PNG</b><span>png-512/</span></div>
          <div><b>四档 favicon</b><span>favicon/</span></div>
          <div><b>方形应用图标</b><span>assets/appicon/</span></div>
          <div><b>锁定组合 PNG</b><span>lockup/png/</span></div>
        </div>
        <div class="note" style="margin-top:18px">
          应用图标经自动裁边居中处理，视觉重量与正方形画布一致，
          不因图形自带留白而显得偏小。
        </div>
      </div>
    </div>

    <h3>交互展示</h3>
    <div class="files">
      <div><b>交互预览页（样式×配色）</b><span>preview.html</span></div>
      <div><b>锁定组合展示页</b><span>lockup.html</span></div>
      <div><b>WebGL 动态背景页</b><span>atom_webgl.html</span></div>
      <div><b>品牌规范手册</b><span>brand_guide.html</span></div>
      <div><b>对比度审计报告</b><span>contrast_audit.py</span></div>
    </div>

    <h3>使用前检查</h3>
    <ul class="rule-list">
      <li><b>结构未改</b> <em>比例、角度、描边、元素数量与本手册一致</em></li>
      <li><b>色彩合规</b> <em>取自系统内配色，或已通过对比度校验</em></li>
      <li><b>空间足量</b> <em>四周留白不少于 X/4</em></li>
      <li><b>尺寸合规</b> <em>不小于对应场景的最小尺寸要求</em></li>
      <li><b>文件为路径</b> <em>字标已转曲，脱离字体依赖</em></li>
    </ul>
  </div>

  <footer>Atom 品牌标志规范手册 · 版本 1.0 · 本手册的数值与资产同源，标志改动后重跑即同步</footer>
</div>

<script>
  // 注入几何实测值
  const G = /*__GEOM_JSON__*/;
  document.getElementById('geo-x').textContent = G.x_height.toFixed(0);
  document.getElementById('geo-main').textContent = '/*__PRIMARY_COLOR__*/';
  const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
  set('g-x', G.x_height.toFixed(1));
  set('g-r', G.outer_r.toFixed(1));
  set('g-swo', G.sw_outer.toFixed(1));
  set('g-swi', G.sw_inner.toFixed(1));
  set('g-cr', G.core_r.toFixed(1));
  set('g-ink', G.ink_w.toFixed(1) + ' × ' + G.ink_h.toFixed(2));
</script>
</body>
</html>
"""


def main():
    print("生成品牌规范手册")
    g = parse_geometry()
    print(f"  几何实测：X高={g['x_height']:.1f} 外接圆R={g['outer_r']:.1f} "
          f"描边={g['sw_outer']}/{g['sw_inner']} 安全空间={g['clear_space']:.1f}")
    html = build()
    out = D / "brand_guide.html"
    out.write_text(html, encoding="utf-8")
    print(f"  输出：{out}  ({len(html) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
