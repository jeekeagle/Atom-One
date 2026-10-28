"""
蜂巢六边 Logo —— 配色方案表（单一数据源）

两组占位符：
  %%MAIN%%   主色 —— 大面积结构色（外轮廓 / 外壳）
  %%ACCENT%% 强调色 —— 小面积点睛色（内核 / 内轮廓）

每套配色标注了建议底色与适用场景，方便直接落地。
所有颜色按 WCAG 对比度思路挑选，深底方案强调色提亮。
"""

PALETTES = [
    {
        "id": "ink-rust",
        "name": "墨黑锈红",
        "en": "Ink & Rust",
        "main": "#1A1A1A",
        "accent": "#8A4A3F",
        "on": "#FFFFFF",
        "note": "原选定稿配色。学术、克制、印刷友好",
        "usage": "纸质物料 / 正文排印 / 讲义",
    },
    {
        "id": "ink-gold",
        "name": "墨黑鎏金",
        "en": "Ink & Gold",
        "main": "#1C1B19",
        "accent": "#B08D4F",
        "on": "#FFFFFF",
        "note": "古典学院感，强调色降饱和后不刺眼",
        "usage": "对外汇报 / 荣誉性场合 / 徽章",
    },
    {
        "id": "ink-teal",
        "name": "墨黑靛青",
        "en": "Ink & Teal",
        "main": "#15202B",
        "accent": "#2E7D8A",
        "on": "#FFFFFF",
        "note": "冷静理性，科技与学术中性色",
        "usage": "研究报告 / 技术文档 / 白底场景",
    },
    {
        "id": "navy-cyan",
        "name": "藏青湖蓝",
        "en": "Navy & Cyan",
        "main": "#12233B",
        "accent": "#1B9AAA",
        "on": "#FFFFFF",
        "note": "清晰现代，强调色明度高、适合数字界面",
        "usage": "网站 / App 图标 / 产品界面",
    },
    {
        "id": "forest-lime",
        "name": "深林青柠",
        "en": "Forest & Lime",
        "main": "#1E3328",
        "accent": "#7FB800",
        "on": "#FFFFFF",
        "note": "高对比强调色，年轻有生长感",
        "usage": "创新产品 / 创投材料 / 展台",
    },
    {
        "id": "plum-coral",
        "name": "紫棠珊瑚",
        "en": "Plum & Coral",
        "main": "#2E1F3D",
        "accent": "#E8654F",
        "on": "#FFFFFF",
        "note": "暖冷对撞，视觉张力最大",
        "usage": "品牌发布 / 社交媒体头图 / 封面",
    },
    {
        "id": "cobalt-white",
        "name": "钴蓝纯白",
        "en": "Cobalt & White",
        "main": "#1B44C8",
        "accent": "#FFFFFF",
        "on": "#FFFFFF",
        "note": "单色系统，双色版即反白版",
        "usage": "反白版本 / 深底 / 烫印",
        "reverse": True,
    },
    {
        "id": "black-white",
        "name": "纯黑白",
        "en": "Pure Mono",
        "main": "#000000",
        "accent": "#FFFFFF",
        "on": "#FFFFFF",
        "note": "最极端的印刷/雕刻/丝网印方案",
        "usage": "单色印刷 / 激光雕刻 / 印章",
        "reverse": True,
    },
    {
        "id": "sand-umber",
        "name": "沙棕炭褐",
        "en": "Sand & Umber",
        "main": "#3A322B",
        "accent": "#C4A484",
        "on": "#F7F4EF",
        "note": "低饱和暖调，沉稳不张扬",
        "usage": "纸质封面 / 展陈 / 复古场景",
    },
    {
        "id": "slate-mint",
        "name": "石板薄荷",
        "en": "Slate & Mint",
        "main": "#26313B",
        "accent": "#4FC3A1",
        "on": "#FFFFFF",
        "note": "清透现代，强调色轻盈",
        "usage": "数字化产品 / 课程物料",
    },
]
