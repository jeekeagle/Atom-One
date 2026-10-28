#!/usr/bin/env python3
"""Atom Logo 展示页生成器 —— 从 variants.py 单一数据源自动产出 showcase.html"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import variants

D = pathlib.Path(__file__).parent
OUT = D / "showcase.html"

ROUND_NAME = {1: "第一轮", 2: "第二轮"}


def build_data():
    """构造页面用的数据（内联 SVG 从 variants 直接取，杜绝转录误差）"""
    items = []
    for v in variants.VARIANTS:
        svg = v["build"]().strip()
        svg = svg.replace("\n", "").replace("  ", "")
        items.append({
            "id": v["id"],
            "title": v["title"],
            "sub": v["sub"],
            "tag": v["tag"],
            "philosophy": v["philosophy"],
            "round": v["round"],
            "svg": svg,
        })
    return items


def build_html(items):
    data_json = json.dumps(items, ensure_ascii=False, indent=2)
    n1 = sum(1 for i in items if i["round"] == 1)
    n2 = sum(1 for i in items if i["round"] == 2)

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Atom 方法体系 — Logo 设计提案</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  :root {
    --ink:#1A1A1A; --sub:#6E6A63; --line:#E4E2DD; --paper:#FAFAF8;
    --accent:#8A4A3F;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: var(--paper); color: var(--ink);
    -webkit-font-smoothing: antialiased; line-height:1.7;
  }
  .mono { font-family: "SF Mono", "JetBrains Mono", Consolas, monospace; }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 0 32px; }

  header { padding: 96px 0 72px; border-bottom: 1px solid var(--line); }
  .eyebrow { font-size:11px; letter-spacing:.22em; text-transform:uppercase;
             color:var(--sub); margin-bottom:28px; }
  h1 { font-size: clamp(44px,7vw,84px); font-weight:200; letter-spacing:.06em;
        line-height:1.1; margin-bottom:8px; }
  h1 .zh { font-weight:300; margin-left:18px; letter-spacing:.12em; }
  .lead { max-width:640px; margin-top:28px; font-size:16px; color:var(--sub);
           font-weight:300; line-height:1.9; }
  .meta { display:flex; gap:40px; flex-wrap:wrap; margin-top:40px;
           padding-top:24px; border-top:1px solid var(--line); }
  .meta div { font-size:12px; }
  .meta .k { color:var(--sub); letter-spacing:.12em; text-transform:uppercase; margin-bottom:4px; }
  .swatch { display:inline-block; width:13px; height:13px; border-radius:2px;
             margin-right:8px; vertical-align:-2px; }

  .round-head { display:flex; align-items:baseline; gap:16px;
                 margin:0 0 8px; padding-top:72px; }
  .round-head h2 { font-size:26px; font-weight:300; letter-spacing:.08em; }
  .round-head .n { font-size:11px; color:var(--sub); letter-spacing:.2em; }
  .round-note { font-size:13.5px; color:var(--sub); max-width:700px;
                 font-weight:300; line-height:1.9; margin-bottom:34px; }

  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr));
           gap:56px 40px; padding:0 0 40px; }
  .card { display:flex; flex-direction:column; align-items:center; text-align:center; }
  .stage { width:100%; aspect-ratio:1/1; display:flex; align-items:center;
            justify-content:center; background:#fff; border:1px solid var(--line);
            position:relative; overflow:hidden;
            transition:transform .6s cubic-bezier(.16,1,.3,1), box-shadow .6s cubic-bezier(.16,1,.3,1); }
  .card:hover .stage { transform:translateY(-5px); box-shadow:0 18px 50px rgba(0,0,0,.07); }
  .stage svg { width:58%; height:58%; color:var(--ink); display:block; }
  .stage .glow { position:absolute; inset:0; pointer-events:none; opacity:0;
                  transition:opacity .8s ease;
                  background:radial-gradient(circle at 50% 50%, rgba(138,74,63,.07), transparent 62%); }
  .card:hover .stage .glow { opacity:1; }
  .no { position:absolute; top:14px; left:16px; font-size:11px; color:#B8B4AD; letter-spacing:.1em; }
  .title { font-size:19px; font-weight:500; letter-spacing:.1em; margin-top:26px; }
  .sub { font-size:10.5px; color:var(--sub); letter-spacing:.2em; text-transform:uppercase; margin-top:9px; }
  .tag { display:inline-block; font-size:10.5px; color:var(--accent); letter-spacing:.1em;
          border:1px solid rgba(138,74,63,.28); border-radius:2px; padding:3px 9px; margin-top:14px; }
  .why { font-size:13.5px; color:var(--sub); font-weight:300; line-height:1.95;
          margin-top:18px; text-align:justify; }

  .scale { padding:0 0 100px; }
  .sec-h { display:flex; align-items:baseline; gap:18px; margin-bottom:12px; }
  .sec-h h2 { font-size:26px; font-weight:300; letter-spacing:.08em; }
  .sec-h .n { font-size:11px; color:var(--sub); letter-spacing:.2em; }
  .note { font-size:13px; color:var(--sub); margin-bottom:32px; max-width:720px; font-weight:300; line-height:1.9; }
  .st { overflow-x:auto; background:#fff; border:1px solid var(--line); }
  table { border-collapse:collapse; width:100%; min-width:620px; }
  th, td { padding:13px 16px; text-align:center; border-bottom:1px solid #F0EEEA; }
  th { font-size:10.5px; color:var(--sub); letter-spacing:.16em; text-transform:uppercase; font-weight:500; }
  td:first-child, th:first-child { text-align:left; padding-left:24px; white-space:nowrap; }
  td.sz { width:88px; }
  td.sz img { display:block; margin:0 auto; }
  .rn { color:#B8B4AD; font-size:10.5px; }

  .usage { padding:0 0 110px; }
  .usage-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
                 gap:20px; margin-top:30px; }
  .u { background:#fff; border:1px solid var(--line); padding:26px 22px; }
  .u h4 { font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--sub);
           font-weight:500; margin-bottom:16px; }
  .u .demo { height:88px; display:flex; align-items:center; justify-content:center; margin-bottom:14px; }
  .u .demo svg { width:56px; height:56px; }
  .u p { font-size:12px; color:var(--sub); font-weight:300; line-height:1.8; }
  .u.dark { background:var(--ink); border-color:var(--ink); }
  .u.dark h4, .u.dark p { color:#9A968F; }
  .u.dark .demo svg { color:#F2F0EC; }

  footer { border-top:1px solid var(--line); padding:44px 0 72px; text-align:center;
            font-size:11px; color:var(--sub); letter-spacing:.16em; text-transform:uppercase; }
  .bar { width:34px; height:1px; background:var(--ink); opacity:.28; margin:0 auto 24px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="eyebrow mono">Logo Design Proposal / 2026</div>
    <h1>Atom<span class="zh">原子式智能体单元</span></h1>
    <p class="lead">
      为一套「原子式智能体单元」方法体系设计的品牌标记。设计立意取自原子物理学的三件套——
      不可再分的核、可组合的单元、可无限递归的内部结构。视觉语言走学术出版物的克制路线：
      纯黑、无渐变、无阴影，靠几何关系而非装饰建立辨识度。
    </p>
    <div class="meta">
      <div><div class="k mono">Concept</div><div>原子式智能体单元</div></div>
      <div><div class="k mono">Style</div><div>学术专业 · 克制几何</div></div>
      <div><div class="k mono">Variants</div><div>/*__N_TOTAL__*/ 个方案（/*__N1__*/ + /*__N2__*/）</div></div>
      <div><div class="k mono">Color</div><div>
        <span class="swatch" style="background:#1A1A1A"></span>
        <span class="swatch" style="background:#8A4A3F"></span>currentColor 可控</div></div>
    </div>
  </header>

  <div class="round-head"><h2>第一轮</h2><span class="n mono">ROUND 01 · /*__N1__*/ VARIANTS</span></div>
  <p class="round-note">
    从原子物理学的三大母题出发——轨道与核、辐射与点阵、容器与单元——
    逐一试探这套视觉语言能承载多少语义。覆盖线、点、几何、模块、网络、字母六个母题方向。
  </p>
  <div class="grid" id="grid1"></div>

  <div class="round-head"><h2>第二轮</h2><span class="n mono">ROUND 02 · /*__N2__*/ VARIANTS</span></div>
  <p class="round-note">
    换七个此前未尝试的母题：层积、干涉、负空间通道、递归分形、棱镜解析、切分、对握。
    重点不在几何本身的新奇，而在能不能把方法论的某个动作讲清楚——
    分解、组合、留白、收敛，都是这套体系里真实发生的操作。
  </p>
  <div class="grid" id="grid2"></div>

  <div class="scale">
    <div class="sec-h"><h2>尺寸适应性</h2><span class="n mono">SCALE TEST</span></div>
    <p class="note">
      实际下采样至 16 / 32 / 64 / 128 px 后再放大显示，以保留真实像素特征。
      经验规律：<strong>闭合几何与实心块</strong>（03 蜂巢、05 模块、11 开窗、14 切分、15 对握）
      全尺寸可用；<strong>细线与开放结构</strong>（01 轨道、04 弧线、06 网络、10 摩尔、12 分形）
      在 16px 下会并线或灰飞，建议限定 64px 以上使用。
    </p>
    <div class="st">
      <table>
        <thead><tr><th>方案</th><th>16px</th><th>32px</th><th>64px</th><th>128px</th></tr></thead>
        <tbody id="scaleBody"></tbody>
      </table>
    </div>
  </div>

  <div class="usage">
    <div class="sec-h"><h2>应用建议</h2><span class="n mono">USAGE</span></div>
    <p class="note">
      所有方案使用 <span class="mono">currentColor</span> 着色，置于任意父容器即可整体换色——
      随链接变蓝、随主题变深，是可直接落地的工程约定。
    </p>
    <div class="usage-grid" id="usageGrid"></div>
  </div>
</div>
<footer><div class="bar"></div>Atom Method System · Logo Exploration</footer>

<script>
const DATA = /*__DATA__*/;

const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;');

const render = (arr, startNo) => arr.map((v,i) => `
  <div class="card">
    <div class="stage">
      <div class="glow"></div>
      <span class="no mono">${String(startNo+i).padStart(2,'0')}</span>
      ${v.svg}
    </div>
    <div class="title">${esc(v.title)}</div>
    <div class="sub mono">${esc(v.sub)}</div>
    <div class="tag">${esc(v.tag)}</div>
    <p class="why">${esc(v.philosophy)}</p>
  </div>`).join('');

const r1 = DATA.filter(x=>x.round===1), r2 = DATA.filter(x=>x.round===2);
document.getElementById('grid1').innerHTML = render(r1, 1);
document.getElementById('grid2').innerHTML = render(r2, r1.length+1);

document.getElementById('scaleBody').innerHTML = DATA.map(v=>`
  <tr>
    <td>${esc(v.title)} <span class="mono rn">${esc(v.sub)}</span></td>
    ${[16,32,64,128].map(s=>`<td class="sz"><img src="png/${v.id}.png" width="${s}" height="${s}" alt=""></td>`).join('')}
  </tr>`).join('');

// 应用示例：挑 5 个代表性 + 深色反白
const PICK = ['v3-hex','v7-letter-a','v8-recursive','v10-moire','v15-bracket'];
const byId = Object.fromEntries(DATA.map(x=>[x.id,x]));
document.getElementById('usageGrid').innerHTML = PICK.map(id=>`
  <div class="u">
    <h4 class="mono">${esc(byId[id].title)}</h4>
    <div class="demo">${byId[id].svg}</div>
    <p>${esc(byId[id].tag)}<br>${esc(byId[id].sub)}</p>
  </div>`).join('') + `
  <div class="u dark">
    <h4 class="mono">反白模式</h4>
    <div class="demo">${byId['v8-recursive'].svg}</div>
    <p>深色底反白<br>RECURSIVE NEST</p>
  </div>`;
</script>
</body>
</html>
"""
    html = (html
            .replace("/*__DATA__*/", data_json)
            .replace("/*__N_TOTAL__*/", str(len(items)))
            .replace("/*__N1__*/", str(n1))
            .replace("/*__N2__*/", str(n2)))
    return html


def main():
    items = build_data()
    html = build_html(items)
    OUT.write_text(html, encoding="utf-8")
    print(f"已生成 {OUT.name}（{len(items)} 个方案，{len(html)} 字符）")
    # 自检
    for v in variants.VARIANTS:
        assert v["id"] in html, f"{v['id']} 未进入页面"
    print("自检通过：全部方案 id 均已写入页面")


if __name__ == "__main__":
    main()
