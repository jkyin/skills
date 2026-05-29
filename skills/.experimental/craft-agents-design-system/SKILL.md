---
name: craft-agents-design-system
description: Craft Agent app 的视觉设计规范参考。在实现、修改或评审 UI 时提供权威的设计 token、配色、字体、间距、阴影、层级、动效约定与组件规格。当用户说「用 Craft Agent 风格」「参考 Craft Agent 视觉规范」「实现 Craft Agent 同款 X（按钮/下拉/卡片/overlay/Island）」，或需要正确的颜色/阴影/z-index/动效数值、组件 anatomy·variants·states·props 时使用本 skill。覆盖 6 色系统、foreground 混合阶梯、阴影梯度、z-index 标度、Island 动效、组件级 tokens，以及聊天/overlay/菜单/内容渲染等组件的完整规格。
---

# Craft Agent 视觉设计规范

本 skill 提供 Craft Agent 应用的完整视觉设计系统，自包含、不依赖任何源码即可使用。
用于在新项目或现有界面中复刻 Craft Agent 风格，或在评审 UI 时核对 token 是否合规。

## 何时使用

- 用户要求「Craft Agent 风格 / 同款」的界面、组件或主题。
- 实现 UI 时需要权威的颜色、字体、间距、圆角、阴影、z-index、动效数值。
- 评审/重构 UI，检查是否硬编码了颜色或 z-index、阴影是否走标准梯度。
- 搭建主题系统，需要知道哪些是「基色」、哪些是「派生」。

## 如何使用

1. 需要**设计基元**（颜色/字体/间距/阴影/z-index/动效）→ 读 [reference.md](reference.md)（11 节，含全部 token 表）。
2. 需要**组件规格**（某个按钮/下拉/卡片/overlay/Island 怎么做）→ 读 [components.md](components.md)（含 anatomy / variants / states / props / 尺寸 / 用到的 token，及跨组件「通用约定」）。
3. 按需取值：实现时引用 CSS 变量名（如 `var(--foreground-50)`）与组件实测类名/数值，不要硬编码原始色值。
4. 遵守铁律：
   - **只重定义 6 基色**即可重主题，其余全部派生，勿手改派生 token。
   - **绝不硬编码 z-index 与颜色**，一律引用标度 token。
   - 新建组件先看 components.md 的 **§5 组件通用约定**，复用既有模式（浮动控件三件套、复制交互、菜单项规范、focus 环等）。

## 核心速查

**6 基色**（其余颜色全部由它们派生）：`--background` `--foreground` `--accent`（紫，品牌/Auto/Execute）`--info`（琥珀，警告/Ask）`--success`（绿）`--destructive`（红）。

**两条变体轴**：
- `/NN` = **alpha 透明**（边框、hover、遮罩）——如 `foreground/50`
- `-NN` = **向 background 实色混合**（不透明填充）——如 `--foreground-50`

**默认值要点**：`--radius: 0`（默认直角，需要圆角用 `.smooth-corners` 超椭圆）；`--font-size-base: 15px`；`--spacing: 0.25rem`；UI 用 system sans，代码用 `JetBrains Mono`。

**阴影梯度**（由轻到重）：`shadow-minimal → middle → medium → strong → hero`；模态用 `shadow-modal-small`；染色阴影用 `.shadow-tinted` + `--shadow-color`。

**z-index 标度**：`base 0 / local 10 / sticky 20 / titlebar 40 / panel 50 / dropdown 100 / tooltip 150 / modal 200 / overlay 300 / fullscreen 350 / island 400 / splash 600`。

**动效**：默认过渡 `200ms`；Island 默认 `duration 0.4s, bounce 0.2, blurPx 7`；内容缓动 `cubic-bezier(0.2, 0.8, 0.2, 1)`。

完整数值、明暗双套配色、组件级 tokens 见 [reference.md](reference.md)。
