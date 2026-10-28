# 蜂巢六边 · Atom 标志样式与配色系统

在用户已选定的 **v3-hex 蜂巢六边** 基础上，扩展出的完整标志系统：
**10 种结构样式 × 10 套配色 = 100 个组合**，全部为矢量母版。

---

## 一、设计基因

所有变体共享同一枚六边形的几何构造，这是整个系统的辨识锚点：

| 层 | 形状 | 朝向 | 作用 |
|---|---|---|---|
| 外壳 | 六边形 | **平边朝上下**（flat-top，尖角朝左右） | 蜂巢单元的物理边界 |
| 内核 | 六边形 | **尖角朝上下**（pointy-top） | 与外壳错位 30°，形成咬合 |
| 中心 | 圆点 / 小六边形 | — | 智能体单元的"核" |

> **错位 30° 是关键**。两个同向的六边形只会像靶心一样重叠；错位后才形成蜂窝的咬合关系，
> 也才同时承载「原子」与「蜂巢」两个隐喻。

**为什么是蜂巢**：蜂巢是自然界最经济的空间分割——六边形能无缝隙铺满平面。
这与 Atom 方法体系的「原子式单元」主张精确对应：**可组合、可复制、可拼装、彼此协作**。

---

## 二、十种结构样式

| id | 名称 | 结构 | 特征 | 适用 |
|---|---|---|---|---|
| `s1-nested` | 标准嵌套 | 双层描边 + 圆核 | 与原选定稿一致 | 主用 |
| `s2-solid-outer` | 外实心中空 | 实心外壳镂空内核 | 识别度最高、远距离可辨 | 标识牌、大屏 |
| `s3-solid-inner` | 内实心 | 外描边 + 实心内核 | 块面稳定 | 应用图标 |
| `s4-ring` | 蜂房环 | 六边形粗环 + 核 | 几何感最强 | 印刷、烫印 |
| `s5-triple` | 三层嵌套 | 三级同心 | 纵深层次 | 机构标识、证书 |
| `s6-no-core` | 去核轮廓 | 仅双层轮廓 | 最克制 | 底纹、水印 |
| `s7-hex-core` | 六边形核 | 核改小六边形 | 与外壳同族 | 系列化延展 |
| `s8-cluster` | 蜂窝簇 | 七格等大共边 | 直接画出蜂巢 | 生态/协作叙事 |
| `s9-fine` | 细线版 | 线宽 2.1 / 1.8 | 轻、小尺寸清晰 | 小图标、浅底 |
| `s10-bold` | 粗线版 | 线宽 4.2 / 3.6 | 重、大尺寸有分量 | 招牌、印刷主图 |

---

## 三、十套配色

| id | 名称 | 主色 | 强调色 | 气质与用途 |
|---|---|---|---|---|
| `ink-rust` | 墨黑锈红 | `#1A1A1A` | `#8A4A3F` | 学术克制。**主用**，纸面与正文 |
| `ink-gold` | 墨黑鎏金 | `#1C1B19` | `#B08D4F` | 古典学院感，荣誉场合 |
| `ink-teal` | 墨黑靛青 | `#15202B` | `#2E7D8A` | 冷静理性，技术文档 |
| `navy-cyan` | 藏青湖蓝 | `#12233B` | `#1B9AAA` | 清晰现代，**数字界面** |
| `forest-lime` | 深林青柠 | `#1E3328` | `#7FB800` | 高对比，年轻有生长感 |
| `plum-coral` | 紫棠珊瑚 | `#2E1F3D` | `#E8654F` | 冷暖对撞，张力最大，发布场合 |
| `cobalt-white` | 钴蓝纯白 | `#1B44C8` | `#FFFFFF` | 单色系统，反白版 |
| `black-white` | 纯黑白 | `#000000` | `#FFFFFF` | 印刷 / 雕刻 / 印章 |
| `sand-umber` | 沙棕炭褐 | `#3A322B` | `#C4A484` | 低饱和暖调，纸质封面 |
| `slate-mint` | 石板薄荷 | `#26313B` | `#4FC3A1` | 清透现代，课程物料 |

> **配色用法**：主色承担结构面积，强调色只出现在小面积（内核、内轮廓）。
> 强调色面积越小、彩度越可控，整套系统越耐看。

---

## 四、文件结构

```
hex/
├── styles.py              ★ 样式定义（几何 + 结构）—— 单一数据源
├── palettes.py            ★ 配色定义 —— 单一数据源
├── wordmark.py            ★ 字标转曲（fontTools → SVG path）
├── lockup.py              ★ 联合锁定组合排版引擎
├── contrast_audit.py      ★ WCAG 对比度审计（全色/反白/单色三模式）
├── brand_guide.py         ★ 品牌规范手册生成器（几何实测 → PDF）
├── build_variants.py      生成 100 组合 SVG + PNG
├── export_assets.py       导出交付资产（PNG/favicon/反白）
├── export_lockup.py       导出 100 套锁定组合
├── contact_sheet.py       生成图标比色大图
├── lockup_sheet.py        生成锁定组合比色大图
├── build_preview.py       注入数据 → preview.html（图标预览页）
├── build_lockup_page.py   注入数据 → lockup.html（锁定组合展示页）
├── preview.tpl.html       图标预览页模板
├── preview.html           图标预览页产物（单文件，可直接双击打开）
├── lockup.tpl.html        锁定组合页模板
├── lockup.html            锁定组合页产物（单文件，零外链）
├── atom_webgl.html        WebGL 动态背景页（6 着色器 + 真实 logo）
├── brand_guide.html       品牌规范手册（单文件，可打印）
├── brand_guide.pdf        品牌规范手册 PDF（16 页 A4）
├── svg/         100 个全色 SVG（主色+强调色写死）
├── svg-mono/    100 个单色 SVG（主色=currentColor）
├── png/         100 个 1024 透明底 PNG
├── png-512/     100 个 512 透明底 PNG
├── favicon/     400 个（16/32/48/512）
├── reverse/     100 个反白版
├── lockup/      锁定组合四套资产
├── pick/        精选资产（网站与文档直接用）
├── sheet-styles.png       样式 × 配色 比色图
├── sheet-palettes.png     配色 × 样式 比色图
├── sheet-grid.png         100 格速览网格
├── sheet-lockup-styles.png    锁定组合 比色图
└── sheet-lockup-palettes.png  锁定组合 比色图
```

---

## 五、联合锁定组合（Lockup）

图标在左、字标在右的横向组合，共 100 套（10 样式 × 10 配色）。

**字形已转曲。** `wordmark.py` 用 fontTools 把 Arial Bold 的字形轮廓烘成 SVG path，
任何环境打开都一致 —— 品牌资产不能用 `<text>`，换台机器就掉字变形。

**排版参数**（`lockup.py`，全部可调）

| 参数 | 值 | 说明 |
|---|---|---|
| `CAP_RATIO` | 0.40 | 字标 cap height ÷ 图标高度。0.40 时两者视觉重量平级 |
| `GAP_RATIO` | 0.30 | 图标与字标间距 ÷ 图标高度 |
| `TAG_SIZE_RATIO` | 0.22 | 副标字号 ÷ 主标字号 |
| `TRACKING` | 60 | 主标字距（em 千分比） |
| `TAG_TRACKING` | 180 | 副标字距，小字需更松 |
| `TAG_GAP` | 0.30 | 主标基线到副标顶部 ÷ 图标高度 |

**关键约束：副标宽度不得超过主标宽度。**
主标「Atom」墨迹宽 267，副标「METHOD SYSTEM」在 ratio 0.22 / tracking 180 下为 236 ——
收在主标右边界内。反之（0.26/200 时为 285）会破坏锁定组合的右侧收边，是规范硬伤。

**垂直对齐**：字标以大写 A 的 cap 中线（视觉中心）对齐图标视觉中心，不是包围盒机械居中。
副标与主标左对齐，基线单独计算。

### 锁定组合文件

```
lockup/
├── svg/       100 个全色 SVG
├── svg-mono/  100 个单色 SVG（主标 currentColor）
├── png/       100 个透明底 PNG（1200px 宽）
└── png-rev/   100 个反白 PNG
```

`pick/` 中另有 4 套精选：`lockup-primary` / `lockup-digital` / `lockup-print` / `lockup-launch`。

**展示页**：`lockup.html` —— 可切换样式、配色、底色、副标题显隐，内含 10×10 矩阵与应用示例。

---

## 六、重新生成

```bash
cd hex
python build_variants.py      # 生成 100 组合 SVG/PNG
python export_assets.py       # 导出交付资产
python export_lockup.py       # 导出 100 套锁定组合
python build_preview.py       # 重建图标预览页
python build_lockup_page.py   # 重建锁定组合展示页
python contact_sheet.py styles   # 图标比色图
python contact_sheet.py palettes
python contact_sheet.py grid
python lockup_sheet.py styles    # 锁定组合比色图
python lockup_sheet.py palettes
```

**单一数据源原则**：样式与配色只写在 `styles.py` / `palettes.py` 里，
生成器、预览页、比色图全部从这两个文件读取——改动定义即全链路生效，不会出现手抄转录误差。

---

## 六、使用规范

**最小尺寸**

| 样式 | 16px | 32px |
|---|---|---|
| s1 / s2 / s3 / s4 / s5 / s7 | 可用 | 可用 |
| s6 / s9 | 谨慎 | 可用 |
| s8 蜂窝簇 | 不可用 | 可用 |
| s10 粗线版 | 不可用 | 可用 |

16px 场景请用 `s2-solid-outer`（实心块面在极小尺寸下依然成立）。

**色彩**
- 纸面印刷：主用 `ink-rust`，强调色可再降一档饱和
- 深色底：使用 `reverse/` 目录下的反白版，不要直接改主色
- 一次性印刷、雕刻、丝网印：`black-white`
- 屏幕：`navy-cyan`，深色界面另出反白版

**留白**
- 图形四周留白 ≥ 图形高度的 25%（favicon 已按 80% 安全框自动居中）
- 主色与背景对比度 ≥ 4.5:1
