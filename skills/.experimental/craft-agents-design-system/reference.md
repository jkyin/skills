# Craft Agent — 视觉设计规范（完整参考）

Craft Agent 应用视觉设计系统的自包含参考，记录全部设计 token、标度与动效约定，
**无需源码即可理解、评审或复刻**。

来源（Craft Agent 仓库）：`packages/ui/src/styles/index.css`（主题、标度、阴影、
z-index、工具类）+ §8/§9 标注的 token 文件。

系统面向 Tailwind CSS v4（`@theme inline`），但 token 本身是纯 CSS 自定义属性，
可直接复制到任意项目。

---

## 1. 设计哲学

- **6 色系统**：UI 所有颜色都从六个基色派生。没有庞杂调色板；语义由这六色加系统化变体承载。
- **两条变体轴**：
  - **`/NN` = alpha 透明** —— 如 `foreground/50`。用于边框、hover、遮罩，任何需要透出背景的场景。
  - **`-NN` = 实色混合** —— 向 `background` 不透明插值，如 `--foreground-50`。用于需要实色填充（其上有文字、不透底）的场景。
- **OKLCH 优先**：基色以 OKLCH 编写，保证明暗下感知均匀。主题覆盖接受任意 CSS 颜色格式，但推荐 OKLCH。
- **明暗一等公民**：暗色模式（`.dark` 类）重新声明六个基色与阴影透明度；其余全部派生、自动更新。

---

## 2. 颜色 token

### 2.1 六个基色

| Token | 用途 | Light | Dark |
|---|---|---|---|
| `--background` | 表面 / 页面 | `oklch(0.98 0.003 265)` | `oklch(0.2 0.005 270)` |
| `--foreground` | 文字与图标 | `oklch(0.185 0.01 270)` | `oklch(0.92 0.005 270)` |
| `--accent` | 品牌紫、Auto/Execute、激活态 | `oklch(0.58 0.22 293)` | `oklch(0.65 0.20 293)` |
| `--info` | 琥珀 —— 警告、Ask 模式、提示 | `oklch(0.75 0.16 70)` | `oklch(0.70 0.16 70)` |
| `--success` | 绿 —— 已连接、勾选 | `oklch(0.55 0.17 145)` | `oklch(0.60 0.17 145)` |
| `--destructive` | 红 —— 错误、失败、删除 | `oklch(0.58 0.24 28)` | `oklch(0.70 0.19 22)` |

### 2.2 RGB 阴影伴生色

供需要 `rgba()` 的染色/边框阴影使用。刻意比基色更暗（约 70%），使染色阴影读起来像阴影而非光晕。

| Token | Light | Dark |
|---|---|---|
| `--foreground-rgb` | `38, 36, 42` | `227, 226, 229` |
| `--accent-rgb` | `104, 78, 133` | `118, 92, 147` |
| `--destructive-rgb` | `180, 60, 50` | `200, 80, 70` |
| `--info-rgb` | `180, 120, 40` | `200, 140, 60` |
| `--success-rgb` | `34, 120, 60` | `50, 140, 80` |

### 2.3 文字变体（提升对比）

状态色向 `--foreground` 混合 50%，使状态*文字*在表面上仍清晰。明暗同公式。

```css
--success-text:     color-mix(in oklab, var(--success) 50%, var(--foreground));
--destructive-text: color-mix(in oklab, var(--destructive) 50%, var(--foreground));
--info-text:        color-mix(in oklab, var(--info) 50%, var(--foreground));
```

### 2.4 foreground 实色混合阶梯

将 `--foreground` 向 `--background` 用 `color-mix(in oklch, …)` 插值的不透明阶梯。
明暗定义相同，故每一阶跨主题保持其感知角色。各阶：

`--foreground-2, -3, -5, -10, -20, -30, -40, -50, -60, -70, -80, -90, -95`

```css
--foreground-5:  color-mix(in oklch, var(--foreground) 5%,  var(--background));
--foreground-50: color-mix(in oklch, var(--foreground) 50%, var(--background));
/* …每一阶同模式 */
```

用于不透明分隔线、弱化文字、不能透底的色调填充。

---

## 3. 语义 / shadcn 兼容 token

由六基色派生，任何 shadcn 风格组件可直接接入。明暗相同（引用会翻转的基色）。

| Token | 值 | 说明 |
|---|---|---|
| `--secondary` / `--muted` | `oklch(from var(--foreground) l c h / 0.05)` | 5% foreground 着色 |
| `--secondary-foreground` | `var(--foreground)` | |
| `--muted-foreground` | `var(--foreground-50)` | |
| `--card` / `--popover` | `var(--background)` | |
| `--card-foreground` / `--popover-foreground` | `var(--foreground)` | |
| `--border` | `oklch(from var(--foreground) l c h / 0.05)` | 5% alpha |
| `--input` | `oklch(from var(--foreground) l c h / 0.1)` | 10% alpha |
| `--ring` | `oklch(from var(--foreground) l c h / 0.25)` | 焦点环颜色 |
| `--ring-width` | `1px` | |
| `--ring-offset` | `0px` | |
| `--destructive-foreground` | `var(--background)` | destructive 填充上的文字 |

**组件 token**（另见 §9）：

| Token | 值 |
|---|---|
| `--user-message-bubble` | `oklch(from var(--foreground) l c h / 0.05)` |
| `--md-bullets` / `--md-counters` | `var(--foreground-50)` |

---

## 4. 字体

| Token | 值 |
|---|---|
| `--font-sans` | `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` |
| `--font-mono` / `--font-serif` | `"JetBrains Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace` |
| `--font-default` | `var(--font-sans)` |
| `--font-size-base` | `15px`（设于 `html`；rem 标度由此派生） |
| `--tracking-normal` | `0em` |

Body 使用 `--font-default` 并抗锯齿（`-webkit-font-smoothing: antialiased`、
`-moz-osx-font-smoothing: grayscale`）。

**可选 Inter 字体**：设置 `html[data-font="inter"]` 将 `--font-sans` 切到 Inter，
并启用光学尺寸 + 风格集：

```css
font-optical-sizing: auto;
font-feature-settings: "cv01", "cv02", "cv03", "cv04", "case";
```

（需加载 Inter，最好带光学尺寸 `opsz,wght@14..32`。）

---

## 5. 间距与形状

| Token | 值 | 说明 |
|---|---|---|
| `--spacing` | `0.25rem` | 基础间距单位 |
| `--radius` | `0rem` | **默认直角** —— 系统是方正风格 |

**圆角**：当某元素*确实*应圆角时，用 `.smooth-corners` 工具类得到 iOS 风超椭圆
（`corner-shape: superellipse`，带 `-webkit-` 前缀）。半径值设在元素本身上。

---

## 6. 阴影

### 6.1 透明度驱动变量

亮色阴影克制；暗色加强边框环并去掉模糊光晕。

| Token | Light | Dark |
|---|---|---|
| `--shadow-border-opacity` | `0.08` | `0.15` |
| `--shadow-blur-opacity` | `0.06` | `0.12` |

### 6.2 阴影梯度

阴影为分层堆叠：一个 `foreground-rgb` 的 1px 边框环，加上逐渐变大变柔的黑色模糊层。
由最平到最浮：

| 工具类 / 变量 | 层次 | 用途 |
|---|---|---|
| `--shadow-minimal-flat` | 仅边框环 | 发丝描边、无抬升 |
| `.shadow-minimal` / `--shadow-minimal` | 环 + 2 小模糊 | 静置卡片、chip |
| `.shadow-middle` | 环 + 3 模糊（至 `-3px`） | hover 卡片 |
| `.shadow-medium` | 环 + 4 模糊（至 `-6px`） | 菜单、抬升面板 |
| `.shadow-strong` | 环 + 5 模糊（至 `-12px`） | 对话框 |
| `.shadow-hero` | 环 + 7 模糊（至 `-24px`，柔 `64px`） | 悬浮 hero / 营销 |
| `--shadow-modal-small` / `.shadow-modal-small` | 环 + 5 接地模糊（无负扩散） | 平贴的模态 |
| `.popover-styled` | 背景 + 8px 圆角 + 柔和 6 层阴影 | 统一 popover 容器 |

### 6.3 染色阴影

`.shadow-tinted` 从每元素的 `--shadow-color`（`r, g, b` 三元组，通常取某个 `*-rgb`
token）染色阴影。它响应 `--shadow-border-opacity` / `--shadow-blur-opacity`，故可逐实例调强度。

```jsx
<div
  className="shadow-tinted"
  style={{ ['--shadow-color']: 'var(--info-rgb)',
           ['--shadow-border-opacity']: '0.14',
           ['--shadow-blur-opacity']: '0.10' }} />
```

**暗色模式**下 `.shadow-tinted` 变为仅描边（3× 边框环，模糊层归零）——
彩色光晕被丢弃，改用清晰染色边缘。

---

## 7. z-index 标度

单一有序标度；绝不硬编码 z-index，一律引用 token（在 Craft Agent 仓库由
`no-hardcoded-z-index` / `no-floating-z-tokens-in-island` ESLint 规则强制）。

| Token | 值 | 层 |
|---|---|---|
| `--z-base` | `0` | 正常流 |
| `--z-local` | `10` | 局部堆叠 |
| `--z-sticky` | `20` | sticky 头/行 |
| `--z-titlebar` | `40` | 窗口标题栏 |
| `--z-panel` | `50` | 侧栏面板 |
| `--z-dropdown` | `100` | 下拉 |
| `--z-tooltip` | `150` | tooltip |
| `--z-modal` | `200` | 模态 |
| `--z-overlay` | `300` | 全遮罩 / backdrop |
| `--z-fullscreen` | `350` | 全屏表面 |
| `--z-floating-backdrop` / `--z-island-overlay` | `390` | island backdrop |
| `--z-floating-menu` / `--z-island` | `400` | 浮动菜单 / island 外壳 |
| `--z-island-popover` | `410` | island 之上的 popover |
| `--z-splash` | `600` | splash（最顶） |

> 约定：Island 的 `overlayZIndex` 是其容器 z-index **减 1**（如 island `400` → overlay `390`）。

---

## 8. 动效

### 8.1 时长与缓动

Tailwind `duration-*` 用量（高频优先）：**200ms**（多数过渡默认）、**150ms**、
**100ms**、**75ms**（干脆）、**300ms**（大面积表面）。

在用的缓动曲线：

| 曲线 | 值 | 使用方 |
|---|---|---|
| 内容缓动 | `[0.2, 0.8, 0.2, 1]`（cubic-bezier） | Island 内容交叉淡入 |
| 强调 ease-out | `cubic-bezier(0.22, 1, 0.36, 1)` | 减速感入场 |
| `easeOut` / `easeInOut` | framer-motion 预设 | 透明度 / 循环 shimmer |

### 8.2 Island 过渡（`IslandTransitionConfig`）

「island」是会形变的浮动容器。默认值（`Island.tsx`）：

| 字段 | 默认 | 含义 |
|---|---|---|
| `duration` | `0.4`（秒） | 外壳 + 内容主时长 |
| `bounce` | `0.2` | 外壳布局弹簧 bounce |
| `blurPx` | `7` | 内容交叉淡入的进/出模糊半径 |
| `entryAngleDeg` | `0` | 方向偏移角（`0`=自右，`90`=自下） |
| `entryDistancePx` | `0` | 方向位移距离 |
| `entryStartScale` | `0.25` | 无形变目标缩放时的起始缩放 |

外壳以 `spring`（时长+bounce）动画；内容以 `tween`（内容缓动曲线）动画。

### 8.3 速度感知入场（`island-motion.ts`）

选区 island 入场从指针速度推导角度/距离：

| 常量 | 值 | 角色 |
|---|---|---|
| 视口边距 | `12px` | 钳制锚点 X 时距边缘最小间隙 |
| 默认宽度估计 | `192px` | 预测量 island 宽度 |
| 默认起始缩放 | `0.25` | 入场缩放 |
| 入场距离范围 | `20px`–`132px` | 推导位移的钳制 |
| 回退入场距离 | `44px` | 无指针历史时 |
| 速度→距离系数 | `0.065` | px/s × 系数 → 位移距离 |

角度 = `atan2(dy, dx)` 归一化到 `[0,360)`。批注 **chip** 入场固定：
`entryAngleDeg 90`、`entryDistancePx 64`、`entryStartScale 0.25`。

### 8.4 内置动画（在 `index.css`）

- **Spinner** —— `.spinner` 是 3×3 SpinKit 网格的 `.spinner-cube`；尺寸继承
  `font-size`（`1em` 盒、`0.08em` gap），颜色继承 `currentColor`。
  `spinner-grid` 关键帧，`1.3s infinite ease-in-out`，错峰延迟 `0s`–`0.4s`。
- **Shimmer** —— `.animate-shimmer` 叠加移动的 `linear-gradient`（`foreground` 6% alpha），
  用于乐观/加载态；`1.5s ease-in-out infinite`，继承 `border-radius`。

---

## 9. 组件 token

### 9.1 批注高亮色（`annotation-style-tokens.ts`）

高亮填充（均约 10% alpha）：

| 颜色 | 值 |
|---|---|
| `yellow`（默认） | `color-mix(in srgb, var(--info) 10%, transparent)` |
| `green` | `rgba(74, 222, 128, 0.10)` |
| `blue` | `rgba(96, 165, 250, 0.10)` |
| `pink` | `rgba(244, 114, 182, 0.10)` |
| `purple` | `rgba(168, 85, 247, 0.10)` |

**批注 chip 背景**（info 向 background 混合）：

| 状态 | 背景 | 边框 / 模糊透明度 |
|---|---|---|
| Pending follow-up | `info 34% + background` | `0.14` / `0.10` |
| Sent follow-up | `info 14% + background`，opacity `0.58`，fg `--foreground` | `0.05` / `0.03` |
| Idle | `info 30% + background` | `0.05` / `0.03` |

Pending chip/rect 用 `.shadow-tinted` + `--shadow-color: var(--info-rgb)`。

### 9.2 任务勾选动画（`animated-task-item.tokens.ts`）

SVG 描边勾选：

```js
{ svgViewBox: '0 0 20 20',
  pathD: 'M 0 4.5 L 3.182 8 L 10 0',
  pathLength: '1',
  strokeWidth: '1.7',
  pathTransform: 'translate(5.15 6.05)' }
```

### 9.3 用户消息气泡

`--user-message-bubble: oklch(from var(--foreground) l c h / 0.05)` —— 5% foreground 着色。

---

## 10. 基础工具类

- **滚动条** —— 全局 `::-webkit-scrollbar` 为 `8px`，透明 track，`--border` thumb
  （hover → `--muted-foreground`）。
  - `.scrollbar-hide` —— 完全隐藏但保留滚动。
  - `.scrollbar-hover` —— 细 `4px` 条，thumb 仅在父级 `.group` hover 时出现。
- **焦点** —— `*:focus-visible` 移除 outline 并应用环 token（`--ring`、`--ring-width`、`--ring-offset`）。
- **盒模型** —— `* { box-sizing: border-box; border-color: var(--border) }`。

---

## 11. 主题与覆盖

只需提供六个基色即可重主题，其余全部派生。

- **应用默认**：Settings → Appearance → Default Theme。
- **按 workspace 覆盖**：存于 `~/.craft-agent/workspaces/{id}/config.json` 的
  `defaults.colorTheme`；省略则继承应用默认。
- **预设主题包**：`~/.craft-agent/themes/{name}.json`。
- **颜色覆盖**：`~/.craft-agent/theme.json`，可带 `dark` 块：

```json
{
  "accent": "oklch(0.58 0.22 293)",
  "dark": { "accent": "oklch(0.65 0.22 293)" }
}
```

所有字段可选 —— 只写要覆盖的。
