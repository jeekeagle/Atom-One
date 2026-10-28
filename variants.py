#!/usr/bin/env python3
"""
Atom 方法体系 Logo — 全部方案定义（单一数据源）
generate.py / build_showcase.py / export_assets.py 均从此处读取，
避免任何手抄转录造成的坐标误差。

设计原则：1-2 核心元素 / ≥40% 负空间 / 线宽 1.5-3 / 单一焦点 / 克制无装饰
所有图形使用 currentColor，便于换色。
"""
import math

# ─────────────────────────────────────────────────────────────
# 几何工具
# ─────────────────────────────────────────────────────────────
def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return round(cx + r * math.cos(a), 2), round(cy + r * math.sin(a), 2)


def arc_path(cx, cy, r, start, end):
    """圆弧路径。角度以正方向递增（SVG y 向下即顺时针）"""
    x1, y1 = polar(cx, cy, r, start)
    x2, y2 = polar(cx, cy, r, end)
    delta = (end - start) % 360
    large = 1 if delta > 180 else 0
    return f"M {x1} {y1} A {r} {r} 0 {large} 1 {x2} {y2}"


def grid_cells(cells, x0, y0, cell, gap, size=14, rx=2.8):
    """生成圆角方阵，cells 为需要保留的 (col,row) 集合"""
    out = []
    for col, row in cells:
        x = x0 + col * (size + gap)
        y = y0 + row * (size + gap)
        out.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{rx}"/>')
    return "".join(out)


# ─────────────────────────────────────────────────────────────
# 第一轮 · 8 个方案
# ─────────────────────────────────────────────────────────────
def v1_orbital():
    return """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
  <g stroke="currentColor" stroke-width="2.4">
    <ellipse cx="50" cy="50" rx="35" ry="13" transform="rotate(-28 50 50)"/>
    <ellipse cx="50" cy="50" rx="35" ry="13" transform="rotate(32 50 50)"/>
  </g>
  <circle cx="50" cy="50" r="7" fill="currentColor"/>
</svg>"""


def v2_concentric():
    inner, outer = [], []
    for d in range(90, 450, 60):
        x, y = polar(50, 50, 17, d)
        inner.append(f'<circle cx="{x}" cy="{y}" r="2.8"/>')
    for d in range(15, 375, 30):
        x, y = polar(50, 50, 30, d)
        outer.append(f'<circle cx="{x}" cy="{y}" r="1.9"/>')
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g fill="currentColor">
    <circle cx="50" cy="50" r="4.5"/>
    {''.join(inner)}
    {''.join(outer)}
  </g>
</svg>"""


def v3_hex():
    return """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
  <g stroke="currentColor" stroke-linejoin="round">
    <polygon points="84,50 67,79.4 33,79.4 16,50 33,20.6 67,20.6" stroke-width="3"/>
    <polygon points="50,34 63.9,42 63.9,58 50,66 36.1,58 36.1,42" stroke-width="2.6"/>
  </g>
  <circle cx="50" cy="50" r="3.6" fill="currentColor"/>
</svg>"""


def v4_arcs():
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
  <g stroke="currentColor" stroke-linecap="round">
    <path d="{arc_path(50, 50, 35, 160, 305)}" stroke-width="2.8"/>
    <path d="{arc_path(50, 50, 25, 250, 405)}" stroke-width="2.4"/>
    <path d="{arc_path(50, 50, 16, 330, 455)}" stroke-width="2.2"/>
  </g>
  <circle cx="50" cy="50" r="5" fill="currentColor"/>
</svg>"""


def v5_modules():
    cells = []
    for d in range(0, 360, 60):
        x, y = polar(50, 50, 26, d)
        cells.append(f'<rect x="{round(x-5,2)}" y="{round(y-5,2)}" width="10" height="10" rx="2.6"/>')
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g fill="currentColor">
    {''.join(cells)}
    <circle cx="50" cy="50" r="6.5"/>
  </g>
</svg>"""


def v6_network():
    return """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
  <g stroke="currentColor" stroke-width="2" stroke-linecap="round">
    <path d="M 50 50 Q 38 60, 26 70"/>
    <path d="M 50 50 Q 61 41, 72 32"/>
    <path d="M 50 50 Q 62 59, 74 68"/>
  </g>
  <g fill="currentColor">
    <circle cx="50" cy="50" r="6.5"/>
    <circle cx="26" cy="70" r="4.5"/>
    <circle cx="72" cy="32" r="4.5"/>
    <circle cx="74" cy="68" r="3.4"/>
  </g>
</svg>"""


def v7_letter_a():
    return """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
  <g stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 28 76 L 50 24 L 72 76"/>
    <path d="M 36.5 58 L 63.5 58"/>
  </g>
  <circle cx="50" cy="58" r="4.8" fill="currentColor"/>
</svg>"""


def v8_recursive():
    return """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
  <g stroke="currentColor">
    <circle cx="36" cy="64" r="26" stroke-width="2.6"/>
    <circle cx="36" cy="64" r="11" stroke-width="2.4"/>
    <circle cx="66" cy="36" r="16" stroke-width="2.4"/>
  </g>
  <circle cx="36" cy="64" r="3.2" fill="currentColor"/>
</svg>"""


# ─────────────────────────────────────────────────────────────
# 第二轮 · 7 个新方案
# ─────────────────────────────────────────────────────────────
def v9_strata():
    """层积：四条宽度递增的横条，最底一条实心作基座"""
    bars = []
    widths = [30, 42, 54, 66]
    for i, w in enumerate(widths):
        y = 22 + i * 15
        x = round(50 - w / 2, 1)
        if i == 3:  # 最底层实心
            bars.append(f'<rect x="{x}" y="{y}" width="{w}" height="9" rx="2.5"/>')
        else:
            bars.append(f'<rect x="{x}" y="{y}" width="{w}" height="9" rx="2.5" fill="none" '
                        f'stroke="currentColor" stroke-width="2.2"/>')
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g>
    {''.join(bars)}
  </g>
</svg>"""


def v10_moire():
    """摩尔：两族等距线，其中一族整体旋转，产生疏密干涉纹
    要点：线距要够疏（8→11），旋转角要够大（28°），否则看不出干涉"""
    h = "".join(f'<line x1="18" y1="{y}" x2="82" y2="{y}"/>' for y in range(24, 66, 11))
    v = "".join(f'<line x1="{x}" y1="18" x2="{x}" y2="82"/>' for x in range(24, 66, 11))
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
    {h}
    <g transform="rotate(28 50 50)">
      {v}
    </g>
  </g>
</svg>"""


def v11_aperture():
    """开窗：4×4 方阵中挖出一条连贯的 S 形通道
    通道走 (0,3)→(1,3)→(1,2)→(2,2)→(2,1)→(3,1)，
    每步相邻，读起来是一条贯通的路径而非随机缺口"""
    hole = {(0, 3), (1, 3), (1, 2), (2, 2), (2, 1), (3, 1)}
    cells = [(c, r) for r in range(4) for c in range(4) if (c, r) not in hole]
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g fill="currentColor">
    {grid_cells(cells, 14, 14, 15, 3, size=15, rx=3.2)}
  </g>
</svg>"""


def v12_fractal():
    """分形：二叉递归分解树，末端实心点即最小单元"""
    edges = [
        (50, 22, 32, 48), (50, 22, 68, 48),
        (32, 48, 22, 74), (32, 48, 42, 74),
        (68, 48, 58, 74), (68, 48, 74, 74),
    ]
    lines = "".join(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>' for x1, y1, x2, y2 in edges)
    tips = "".join(f'<circle cx="{x}" cy="{y}" r="2.6"/>' for x, y in
                   [(22, 74), (42, 74), (58, 74), (74, 74)])
    mids = "".join(f'<circle cx="{x}" cy="{y}" r="3.1"/>' for x, y in [(32, 48), (68, 48)])
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g stroke="currentColor" stroke-width="1.5" stroke-linecap="round" fill="none">
    {lines}
  </g>
  <g fill="currentColor">
    {mids}
    {tips}
    <circle cx="50" cy="22" r="3.8"/>
  </g>
</svg>"""


def v13_prism():
    """棱镜：一束输入被分解为多束输出
    修正要点：
    1. 棱镜用「尖端朝右」的等腰三角形，左边为入射面
    2. 出射光束起点设在棱镜右顶点右侧 4 单位处，与轮廓完全分离
    3. 出射光束向下/上散开，避开上下斜边延长线"""
    tip_x = 60
    rays = "".join(
        f'<line x1="{tip_x + 4}" y1="50" x2="92" y2="{y}"/>'
        for y in (30, 42, 58, 70)
    )
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
  <g stroke="currentColor" stroke-linecap="round">
    <line x1="6" y1="50" x2="32" y2="50" stroke-width="2.8"/>
    {rays.replace('<line ', '<line stroke-width="1.7" ')}
  </g>
  <polygon points="32,26 32,74 {tip_x},50" stroke="currentColor" stroke-width="2.8" stroke-linejoin="round"/>
</svg>"""


def v14_split():
    """切分：一个方块沿对角拆成两半并错开，一实一空"""
    return """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="20.5,20.5 72.5,20.5 20.5,72.5" fill="currentColor"/>
  <polygon points="27.5,79.5 79.5,27.5 79.5,79.5" fill="none" stroke="currentColor"
           stroke-width="2.6" stroke-linejoin="round"/>
</svg>"""


def v15_bracket():
    """对握：一对括号夹住核心，作用域与被包裹者"""
    return """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
  <g stroke="currentColor" stroke-width="3" stroke-linecap="round">
    <path d="M 38 24 Q 20 50, 38 76"/>
    <path d="M 62 24 Q 80 50, 62 76"/>
  </g>
  <circle cx="50" cy="50" r="5.5" fill="currentColor"/>
</svg>"""


# ─────────────────────────────────────────────────────────────
# 方案清单
# ─────────────────────────────────────────────────────────────
VARIANTS = [
    # ── 第一轮 ──
    {
        "id": "v1-orbital", "round": 1, "title": "轨道原子", "sub": "ORBITAL ATOM",
        "tag": "纯几何 · 线系统",
        "philosophy": "两条不同倾角的椭圆轨道交叠于一颗实心核。轨道代表智能体在环境中反复试错的运行轨迹，核是被抽象出来的那一个不可再分的单元。刻意让两条轨道不对称，避免落入完全对称的呆板。",
        "build": v1_orbital,
    },
    {
        "id": "v2-concentric", "round": 1, "title": "同心点阵", "sub": "CONCENTRIC FIELD",
        "tag": "点阵 · 涌现",
        "philosophy": "中心一颗核，外围两圈微粒由内而外递减尺寸、递增间距。表达单元从核心向外辐射、层层展开的关系——原子式方法体系里，单点不构成系统，粒子的分布才构成结构。",
        "build": v2_concentric,
    },
    {
        "id": "v3-hex", "round": 1, "title": "蜂巢六边", "sub": "HEX LATTICE",
        "tag": "纯几何 · 嵌套",
        "philosophy": "外层六边形是智能体的边界容器，内层六边形是可被拆解与重组的单元，中心一点是贯穿始终的判断核心。六边形选择而非圆形，是在秩序感与柔性之间取平衡。",
        "build": v3_hex,
    },
    {
        "id": "v4-arcs", "round": 1, "title": "错位弧线", "sub": "OFFSET ARCS",
        "tag": "线系统 · 循环",
        "philosophy": "三段半径不同、起止错开的圆弧共同指向中心核。方法论不是一条直线流程，而是多个尺度上的循环往复、最终收敛到同一个判断。弧线留白处即思考发生的间隙。",
        "build": v4_arcs,
    },
    {
        "id": "v5-modules", "round": 1, "title": "模块聚合", "sub": "MODULAR ASSEMBLY",
        "tag": "重复几何 · 组合",
        "philosophy": "六个圆角方块等距环绕一颗核。这是「原子式」最直白的翻译：每个单元形状相同、功能可替，靠聚合而非层级形成系统。圆角处理让模块感不流于生硬。",
        "build": v5_modules,
    },
    {
        "id": "v6-network", "round": 1, "title": "编排网络", "sub": "ORCHESTRATION",
        "tag": "节点网络 · 协作",
        "philosophy": "中心节点体量最大，三个卫星节点按主次递减并以曲线相连。表达智能体不是孤岛，方法体系的价值在于单元之间的编排关系。远处的节点刻意做小做淡，形成深度。",
        "build": v6_network,
    },
    {
        "id": "v7-letter-a", "round": 1, "title": "字母骨架", "sub": "LETTER FRAME",
        "tag": "字母抽象 · 识别",
        "philosophy": "取字母 A 的结构基因而非字形本身：两笔斜线构成骨架，横杠中央嵌一颗实心原子。既有品牌识别度，又保留学术出版物的克制气质。适合作为课程与论文体系的署名标记。",
        "build": v7_letter_a,
    },
    {
        "id": "v8-recursive", "round": 1, "title": "递归嵌套", "sub": "RECURSIVE NEST",
        "tag": "同形递减 · 纵深",
        "philosophy": "左下一个大环，内部再套一个小环，右上一个独立的中环。这是方法体系最本质的一层：单元内部仍由更小的单元构成，分析可以无限向下递归。三个环同为正圆，不因大小而变形，保持体系的一致性。",
        "build": v8_recursive,
    },
    # ── 第二轮 ──
    {
        "id": "v9-strata", "round": 2, "title": "层积", "sub": "STRATA",
        "tag": "层叠 · 阶跃",
        "philosophy": "四条宽度递增的横条自上而下排布，最底层一条实心作基座。对应方法体系里的阶跃结构：越往下越是已经打下的判断基座，越往上越是待验证的推演。宽度递进即难度递进。",
        "build": v9_strata,
    },
    {
        "id": "v10-moire", "round": 2, "title": "摩尔干涉", "sub": "MOIRÉ",
        "tag": "线系统 · 涌现",
        "philosophy": "两族各自规整的等距线，一族整体旋转后交叠，在疏密变化中凭空生出第三种秩序。这是「单元相互作用生成结构」最物理的注脚：没有任何一个单元知道全局，全局却自己长了出来。",
        "build": v10_moire,
    },
    {
        "id": "v11-aperture", "round": 2, "title": "开窗通道", "sub": "APERTURE",
        "tag": "模块 · 负空间",
        "philosophy": "方阵单元中挖出一条 S 形通道，其余保留。方法体系在满地的单元里开辟一条可通行的路径——通道本身不承载内容，它标出的是「从哪里穿过」。大面积留白与密集方块形成硬对比。",
        "build": v11_aperture,
    },
    {
        "id": "v12-fractal", "round": 2, "title": "分形分解", "sub": "FRACTAL BRANCH",
        "tag": "递归 · 分支",
        "philosophy": "一个问题分两支，每支再分两支，直到末端那几个实心点。末端即「不可再分的最小单元」——方法论走到这里才真正落地。枝干越分越细，单元越分越小。",
        "build": v12_fractal,
    },
    {
        "id": "v13-prism", "round": 2, "title": "棱镜分解", "sub": "PRISM",
        "tag": "几何 · 分析",
        "philosophy": "一束输入光射入棱镜，出来时已散成多束。智能体接收到的同一个问题，经方法体系处理后会拆成几个不同性质的子问题。棱镜本身不产生颜色，它只负责改变方向。",
        "build": v13_prism,
    },
    {
        "id": "v14-split", "round": 2, "title": "切分", "sub": "SPLIT BLOCK",
        "tag": "实心 · 分离",
        "philosophy": "一个方块沿对角线切成两半，错开一道缝，一半实心一半描边。实心是已被确认的部分，描边是尚待验证的部分。切分动作本身就是方法论的第一件事。",
        "build": v14_split,
    },
    {
        "id": "v15-bracket", "round": 2, "title": "对握", "sub": "BRACKET",
        "tag": "几何 · 作用域",
        "philosophy": "一对括号夹住一颗实心核。括号是边界与上下文，核是被界定的那件事。这个方案几乎只剩两个元素，是全套里留白最多、最像符号而非图形的一个。",
        "build": v15_bracket,
    },
]

BY_ID = {v["id"]: v for v in VARIANTS}


def all_svg():
    """返回 {id: svg字符串}"""
    return {v["id"]: v["build"]().strip() for v in VARIANTS}
