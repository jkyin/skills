# Craft Agent — 组件规范（完整参考）

Craft Agent 应用 UI 组件的设计规范。每个组件给出 **用途 / Anatomy / Variants /
States / 关键 Props / Sizing·Layout / 用到的 token / Notes**，用于复刻或评审。

配合 `reference.md`（设计基元：颜色/字体/阴影/z-index/动效）一起使用——本文档的
所有 token 名都定义在那里。来源：Craft Agent 仓库 `packages/ui/src/components/`。

> 约定速记（贯穿全部组件，先看这条再看个体）：
> - **浮动按钮基样式**：`bg-background shadow-minimal rounded-[6px]`，图标多为 `w-3.5 h-3.5`。
> - **hover 才显现**：次要动作用 `opacity-0 group-hover:opacity-100`（父容器加 `group`）。
> - **复制反馈**：点击后 `text-success` + Check 图标，**2000ms** 后复原。
> - **菜单项**：`px-2 py-1.5 rounded-[4px] text-sm`，hover `bg-foreground/[0.03~0.05]`，destructive 用 `text-destructive`。
> - **徽章高度梯度**：内联 `h-[22px]` / 头部 `h-[26px]` / 操作 `h-[28px]`。
> - **弹层定位**：vibrancy 风格走 Radix（`StyledDropdown*` + `popover-styled` + `z-dropdown`）；
>   轻量自管定位走 `getBoundingClientRect` + fixed（`SimpleDropdown`/`FilterableSelectPopover`）。
> - **等宽数字**：计数/时长/百分比一律 `tabular-nums`。

---

## 0. 共享布局常量（`lib/layout.ts`）

聊天与 overlay 的跨端（Electron / web viewer）一致性常量。

**`CHAT_LAYOUT`**

| key | 值 |
|---|---|
| maxWidth | `max-w-[840px]` |
| containerPadding | `px-5 py-8` |
| messageSpacing | `space-y-2.5` |
| userMessagePadding | `pt-4 pb-2`（用户消息与 AI 响应的视觉分隔） |
| brandingPadding | `pt-16 pb-24` |

**`OVERLAY_LAYOUT`**

| key | 值 | 说明 |
|---|---|---|
| modalBreakpoint | `99999` | **实际恒为 fullscreen**（阈值设极大，modal 模式预留但不触发） |
| modalMaxWidth | `1100` | modal 卡片最大宽（保留） |
| modalMaxHeightPercent | `85` | modal 最大高 = 85vh（保留） |
| modalBackdropClass | `bg-black/50` | modal 遮罩 |
| fullscreenBackdropClass | `bg-background` | fullscreen 遮罩 |

`useOverlayMode()` 按视口宽返回 `'modal' | 'fullscreen'`；因阈值为 99999，**当前始终 fullscreen**。

---

## 1. 基础原语（`components/ui/`）

### Island
- **用途**：在多个 `IslandContentView` 子视图间做形变（morph）切换的动画外壳容器，支持 dialog 语义、滚动锁与外部交互拦截。
- **Anatomy**：外层 `motion.div`（layout spring + 可选 morph）→ `relative` 包裹 → `AnimatePresence mode="popLayout"` 内容 crossfade 层（opacity + blur）→ 对齐容器（justify/items 由 anchor 决定）；`blockOutsideInteraction` 时 portal 一个 `fixed inset-0` 全屏 blocker 到 body。
- **Variants**：`dialogBehavior` = `none | close | back-or-close`（默认 `back-or-close`）；`replayOnVisible` = `auto | always`；morph / 非 morph。
- **States**：`data-state` open/closed（由 `isVisible` 派生）；warmup 隐藏（morph 首帧两层 RAF 预热）；replay priming；transition settling（切视图后 `duration*1000+80` ms）；dialog 模式 `role="dialog"` + `aria-modal` + 自动 focus；scroll locked；outside dismiss（捕获阶段 pointerdown）。
- **Props（关键）**：

| Prop | 类型 | 默认 | 说明 |
|---|---|---|---|
| activeViewId | string | — | 当前激活子视图 id |
| radius | number | 12 | shell 圆角 |
| isVisible | boolean | true | 控制 presence/进出场 |
| transitionConfig | IslandTransitionConfig | DEFAULT_TRANSITION | 见 reference §8.2 |
| dialogBehavior | 'none'\|'close'\|'back-or-close' | 'back-or-close' | Escape 语义 |
| lockScrollWhileVisible | boolean | false | 可见即锁滚动 |
| dismissOnPointerDownOutside | boolean | false | 外部按下关闭 |
| replayOnVisible | 'auto'\|'always' | 'auto' | 入场重放策略 |
| overlayZIndex | zIndex | — | blocker 遮罩 z，应设为容器 z − 1 |

- **Sizing/Layout**：shell `mx-auto w-fit overflow-hidden border border-border/50 bg-background shadow-strong`，`borderRadius: radius`（默认 12），`transformOrigin: 50% 50%`；scale clamp `[0.06, 4]`；morph delta 上限 `innerWidth/Height * 0.75`，fallback scale `0.16`。
- **Tokens used**：`border-border/50`、`bg-background`、`shadow-strong`；动效 `DEFAULT_TRANSITION`（duration 0.4 / bounce 0.2 / blurPx 7 / entryStartScale 0.25）；内容缓动 `CONTENT_EASE = [0.2, 0.8, 0.2, 1]`。
- **Notes**：外壳 spring + 内容 crossfade 并行；dialog focus 管理；全局引用计数滚动锁（`body` overflow:hidden + touchAction:none，捕获阶段拦 wheel/touchmove/滚动键，可编辑元素豁免）；Escape 优先走 dismissible-layer bridge（priority 200）。导出工具函数 `handleIslandEscape`。

### IslandContentView
- **用途**：Island 子视图的 **marker** 组件，仅承载 id/anchor/morph/lockScroll 元数据，本身不渲染包装节点（返回 `<>{children}</>`）。
- **Props（关键）**：`id`、`anchorX`（`left|center|right`，默认 center）、`anchorY`（`top|center|bottom`，默认 top）、`morphFrom`、`lockScroll`、`blockOutsideInteraction`、`className`。
- **Notes**：父 Island 通过 `child.type === IslandContentView` 识别；也支持任何带 string `id` prop 的子组件（flexible path）。

### IslandFollowUpContentView
- **用途**：Island 内可复用的「追问 / Follow-up」确认视图：多行输入 + 提交 / 提交并发送 / 取消 / 删除，含 view·edit 两态。
- **Anatomy**：`IslandContentView`（center/top）→ 根 `w-[330px] px-3 pt-3 pb-3 space-y-2.5 select-none` → 标题行 + 输入区（隐藏 measure textarea 自动测高 + 可见 textarea）+ 底部操作行（左 Delete，右 Cancel + 主操作 / split button）。
- **Variants**：`mode` = `edit`（默认）/ `view`（只读，主按钮显示 Edit）；`sendMessageKey` = `enter`（默认）/ `cmd-enter`；单按钮 / split button（有 `onSubmitAndSend` 时）。
- **States**：empty→主按钮 `disabled:opacity-40`；hover `hover:bg-foreground/2`；submit menu open；view 模式 `readOnly tabIndex=-1`；overflow（超 maxInputHeight → `overflowY:auto`）。
- **Sizing/Layout**：固定宽 `w-[330px]`，内边距 12px，子项 `space-y-2.5`；输入区 `rounded-[8px] py-1`，textarea `leading-5`；`minInputHeight` view=20 / edit=44，`maxInputHeight` 默认 400；按钮 `h-8 px-3 rounded-[8px]`；split 下拉触发 `h-8 w-6 border-l border-border/40`，Chevron `h-3 w-3`；Send 图标 `h-3.5 w-3.5`；下拉 `sideOffset={6}` side=bottom align=end。
- **Tokens used**：`bg-background`、`shadow-minimal`、`text-foreground/75·70`、`text-red-500`、`border-border/40`、`hover:bg-foreground/2·5`；下拉 z-index `var(--z-island-popover, 410)`。
- **Notes**：Escape→cancel；`enter` 模式 Enter（无修饰键）或 Cmd/Ctrl+Enter 提交，`cmd-enter` 模式仅 Cmd/Ctrl+Enter；挂载后 RAF 自动聚焦置光标末尾；Save&Send 下拉 `onInteractOutside` 阻止冒泡到父 Island。

### useIslandNavigation（hook）
- **用途**：Island 多视图流程的 backstack 导航。返回 `current / canPop / stack / push / replace / pop / reset / handleEscapeBackOrClose`。
- **Notes**：配合 `dialogBehavior='back-or-close'` 与 `onRequestBack` 使用；`canPop = stack.length > 1`。

### InlineMenuSurface（命令式 class）
- **用途**：caret 锚定的无头内联菜单浮层（slash / mention / label），自管 DOM、选中态、点击委托、键盘选择、滚动跟随。非 React。
- **States**：`selectedIndex`（clamp）；选中行带 `.is-selected`，`ensureSelectedVisible` 自动滚动入视。
- **关键选项**：`className`、`zIndex`（默认 `'var(--z-panel, 50)'`）、`onSelect(item, index)`、`render(container, items, selectedIndex)`。
- **Notes**：`position: fixed`，`setPosition(top,left)` 写入 px；`mousedown` 委托（preventDefault 防抢焦点，`closest('[data-index]')` 取行）；`moveSelection` 循环；`mount(parent=body)` / `destroy()`。

### SimpleDropdown / SimpleDropdownItem
- **用途**：无外部依赖的轻量下拉，自管开关 / 定位 / 键盘导航（非 Radix）。
- **Anatomy**：trigger（`inline-flex`）+ portal 到 body 的菜单 `div`；context 提供 `close / highlightedId / setHighlightedId`。
- **States**：open（`isOpen && position`）；disabled（`opacity-50 pointer-events-none`）；highlighted（键盘/hover/focus → `bg-foreground/[0.05]`）；进场 `animate-in fade-in-0 zoom-in-95 duration-100`。
- **Sizing/Layout**：菜单 `fixed min-w-[140px] p-1 rounded-[8px]`，`top = rect.bottom + 4`，menuWidth≈160，视口边距 8px；item `w-full px-2.5 py-1.5 gap-2 text-[13px] rounded-[4px]`，icon `w-3.5 h-3.5`。
- **Tokens used**：`z-50`、`bg-background`、`shadow-strong`、`border-border/50`、`bg-foreground/[0.05]`、`text-destructive`、`transition-colors`。
- **Props**：`SimpleDropdown`：`trigger`、`align`（`start|end`，默认 end）、`disabled`、`keyboardNavigation`（默认 true）；`SimpleDropdownItem`：`onClick`、`icon`、`variant`（`default|destructive`）。
- **Notes**：mousedown 检测外部关闭；capture 阶段 keydown 处理 Escape / Arrow 循环 / Enter `.click()`；高亮项 `scrollIntoView({block:'nearest'})`。

### StyledDropdown 家族（Radix 包装，vibrancy 风格）
- **用途**：基于 Radix 的样式化下拉，统一玻璃质感 + 进出场动画 + portal。
- **成员**：`DropdownMenu`/`Sub`（透传 Root）、`DropdownMenuTrigger`（默认 `autoMirrorHoverToOpen` 把 `hover:*` 镜像为 `data-[state=open]:*`）、`StyledDropdownMenuContent`、`StyledDropdownMenuItem`、`StyledDropdownMenuSeparator`、`StyledDropdownMenuSubTrigger`、`StyledDropdownMenuSubContent`、`DropdownMenuShortcut`。
- **Content**：`p-1 w-fit flex flex-col gap-0.5 text-xs`，默认 `min-w-40`，`sideOffset=4`；`max-h`/`origin` 取 Radix CSS 变量；token `popover-styled`、`z-dropdown`、`font-sans`，动画 `animate-in/out fade/zoom + slide-in-from-{side}-2`。`light` prop 强制亮色。
- **Item**：`px-2 py-1.5 pr-4 gap-2 text-sm rounded-[4px]`，hover/focus `bg-foreground/[0.03]`，`data-[disabled]` → `opacity-50 pointer-events-none`，`variant=destructive` → `!text-destructive`；svg `h-3.5 w-3.5`。
- **Separator**：`h-px -mx-1 my-1 bg-foreground/10`。**SubContent**：默认 `min-w-36`、`sideOffset=-4`。**Shortcut**：`text-xs tracking-widest text-muted-foreground`。
- **辅助**：`mirrorHoverToOpenStateClasses(className)` 镜像前缀 `bg-/text-/border-/ring-/opacity-`。

### FilterableSelectPopover
- **用途**：带文本过滤 + 键盘导航 + 点击外部关闭 + 锚点 portal 定位的扁平列表选择器（泛型）。
- **Anatomy**：portal → 全屏 backdrop（`fixed inset-0`）+ 浮层（fixed，`translateY(-100%)` 向上展开）+ 顶部 filter input（带下边框）+ 可滚动列表 + 空态/无结果态。
- **States**：highlighted（`bg-foreground/5` + `data-highlighted` 滚动）；selected（`bg-foreground/3`）；empty / noResults。
- **Sizing/Layout**：浮层 `rounded-[8px]`，`minWidth=200 / maxWidth=320`（视口 padding 8）；`top = rect.top - 8` 后上展开；filter `px-3 py-2`；列表 `max-h-[240px] overflow-y-auto p-1`；默认项 `gap-3 px-3 py-2 text-[13px] rounded-[6px]`。
- **Tokens used**：`z-floating-backdrop`、`z-floating-menu`、`bg-background`、`shadow-modal-small`、`border-border/50`、`bg-foreground/5`、`bg-foreground/3`。
- **Props（关键）**：`open`、`anchorRef`、`renderItem`、`closeOnSelect`（默认 false）、`minWidth/maxWidth`。
- **Notes**：自管定位（监听 resize + 捕获阶段 scroll）；打开 RAF+setTimeout 双保险聚焦 input；Arrow 循环 / Enter 选 / Escape 关。

### Drawer 家族（vaul 包装）
- **用途**：基于 `vaul` 的方向性抽屉，拖拽手势由 vaul 接管。
- **成员**：`Drawer`/`Trigger`/`Portal`/`Close`（透传 + `data-slot`）、`DrawerOverlay`、`DrawerContent`、`DrawerHeader/Footer/Title/Description`。
- **DrawerOverlay**：`fixed inset-0`，`z-modal`，`bg-black/50`，fade 动画。
- **DrawerContent**：按 `data-[vaul-drawer-direction]` 贴边——top/bottom `inset-x-0 max-h-[80vh]`（圆角 `rounded-b-lg`/`rounded-t-lg`），left/right `inset-y-0 w-3/4 sm:max-w-sm`；`bg-background z-modal`；仅 bottom 显示拖拽手柄 `h-2 w-[100px] rounded-full bg-muted mx-auto mt-4`。
- **Header/Footer**：`p-4`，Header `flex flex-col gap-0.5`，Footer `mt-auto flex flex-col gap-2`；Title `font-semibold text-foreground`，Description `text-sm text-muted-foreground`。

### PreviewHeader / PreviewHeaderBadge
- **用途**：预览窗口/覆盖层的统一头部工具条（三段式：左占位 / 中徽章 / 右动作+关闭），兼容 macOS 交通灯与拖拽区。
- **PreviewHeader**：`shrink-0 flex items-center justify-between px-3`，高度 `height` prop（默认 50，overlay 常用 44）；左右 `flex-1 min-w-[70px]`；中/右设 `WebkitAppRegion:'no-drag'`；关闭按钮 `p-1.5 rounded-[6px] bg-background shadow-minimal opacity-70 hover:opacity-100 ring-ring`，X 图标 `w-4 h-4`。
- **PreviewHeaderBadge**：`h-[26px] px-2.5 gap-1.5 rounded-[6px] text-[13px] font-medium bg-background shadow-minimal text-foreground/70`，icon `w-3.5 h-3.5`，文本 `truncate`；`onClick` 时为可点击 button（label `group-hover:underline`）；`variant` 多枚举但当前都映射 `text-foreground/70`。

### Spinner / LoadingIndicator
- **Spinner**：`span.spinner[role=status]` 内 9 个 `.spinner-cube`，3×3 网格 CSS 动画，`currentColor` + em 尺寸（CSS 见 reference §8.4）；`aria-label="Loading"`。
- **LoadingIndicator**：Spinner（或非动画态静态 `●`）+ 可选 label + 可选 elapsed；容器 `inline-flex items-center gap-2`；label `text-muted-foreground`，elapsed `text-muted-foreground/60 tabular-nums`（仅 `elapsed >= 1000ms` 显示）；`formatDuration`：<60s → `${s}s`，否则 `m:ss`。Props：`label`、`animated`（默认 true）、`showElapsed`（boolean | 起始时间戳）、`spinnerClassName`。

### Tooltip 家族（Radix）
- **TooltipProvider**：`delayDuration` 默认 300ms，固定 `disableHoverableContent`。
- **TooltipContent**：暗色玻璃气泡——`dark bg-background/80 backdrop-blur-xl backdrop-saturate-150 border-border/50 text-foreground shadow-modal-small`，`px-2.5 py-1.5 rounded-[8px] text-xs`，`z-tooltip`，`sideOffset=4`；进场 `animate-in fade-in-0 duration-100`，出场 `fade-out-0 duration-75`。

---

## 2. 聊天（`components/chat/`）

### TurnCard（含内部 ResponseCard）
- **用途**：渲染一个 assistant turn——可折叠的活动（工具步骤）列表 + 最终响应/计划卡片 + 可选 Todos。聊天核心卡片。
- **Anatomy**：最外层 `space-y-1`。
  - **活动区**（`group select-none`）：折叠 header（旋转 Chevron + step 数 badge + crossfade 预览文本 + `TurnCardActionsMenu`）→ 展开区（`AnimatePresence` height auto，左竖线缩进，逐条 `ActivityRow`/`ActivityGroupRow` + 末尾流式 spinner 行）。
  - **ResponseCard**（response / plan）：卡片 `bg-background shadow-minimal rounded-[8px]`，可选 plan header（`bg-success/5` + ListTodo + "Plan"）、Fullscreen 按钮（hover 显现）、滚动内容区（Markdown，`maxHeight=540`，暗色 16px 渐变 mask）、footer（`border-t border-border/30 bg-muted/20`：左 Copy/Markdown，右 Accept Plan + Branch；streaming 显示 spinner + "Streaming...")。
- **Variants**：ResponseCard `variant` = `response`/`plan`；`displayMode` = `informative`/`detailed`（默认 detailed）；`compactMode`（仅 Accept Plan footer）。
- **States**：collapsed/expanded（Chevron 0→90°，`duration 0.15`；height auto `duration 0.25 ease [0.4,0,0.2,1]`）；streaming；buffering（ResponseCard 返回 null，显示占位 spinner）；活动状态 pending/running(Spinner)/completed(CheckCircle2 success)/error(XCircle destructive)/backgrounded；hover header `hover:bg-muted/50`；copied；Accept Plan 行仅 `isLastResponse` 时 `opacity-100 translate-x-0`，否则 `opacity-0 translate-x-2 pointer-events-none`。
- **Props（关键）**：

| Prop | 类型 | 默认 | 说明 |
|---|---|---|---|
| isStreaming | boolean | — | 流式态 |
| isComplete | boolean | — | 完成态（驱动 turnPhase） |
| isExpanded / defaultExpanded | boolean | false | 活动区展开 |
| response | ResponseContent | — | 含 isPlan/text/isStreaming |
| todos | TodoItem[] | — | 底部 Todo 区 |
| compactMode | boolean | false | 精简 footer |
| displayMode | 'informative'\|'detailed' | 'detailed' | 隐藏 MCP/参数 |
| isLastResponse | boolean | — | 控制 Accept Plan 行显隐 |
| annotationInteractionMode | 'interactive'\|'tooltip-only' | 'interactive' | 注释交互 |

- **Sizing/Layout**：折叠 header `pl-2.5 pr-1.5 py-1.5 rounded-[8px] gap-2`，预览区 `h-5`；step badge `px-1.5 py-0.5 rounded-[4px] text-[10px] font-medium tabular-nums`；展开列表 `pl-4 pr-2 space-y-0.5 border-l-2 border-muted ml-[13px]`，超 `maxVisibleActivities=15` 滚动（行高 24）；ResponseCard 内容 plan/completed `pl-[22px] pr-[16px] py-3 text-sm`，`MAX_HEIGHT=540`；plan header `px-4 py-2 border-b border-border/30`；desktop footer `pl-4 pr-2.5 py-2`，compact `pl-3 pr-2 py-1.5`；Fullscreen 按钮 `top-2 right-2 p-1 rounded-[6px]`，图标 `w-3.5 h-3.5`。
- **SIZE_CONFIG**（导出，复用于 InlineExecution）：fontSize `text-[13px]`，iconSize `w-3 h-3`，spinner `text-[10px]`。
- **Tokens used**：`bg-background`、`shadow-minimal`、`bg-muted/20·50`、`border-border/30`、`border-muted`、`bg-success/5`、`text-success`、`text-destructive`、`text-accent`、`scrollbar-hover`、暗色 16px mask；动效 `duration 0.15/0.2/0.25`，ease `[0.4,0,0.2,1]`/`easeOut`，错峰 delay `index*0.03`（上限 `staggeredAnimationLimit=10`）。
- **Notes**：turnPhase 由 `deriveTurnPhase` 状态机推导；展开后延迟 260ms 滚到底；buffering 由 `BUFFER_CONFIG`（MIN 500ms / MAX 2500ms / throttle 300ms）控制；活动区 `data-search-exclude`，响应内容 `data-search-root="response"`；导出 `ActivityStatusIcon`、`mapToolEventToActivity`。

### UserMessageBubble
- **用途**：右对齐用户消息气泡，支持 markdown、附件缩略图、@mention badges、排队态。
- **Anatomy**：外层 `flex flex-col items-end gap-3 w-full` → 附件预览行（`max-w-[80%]`）+ EditRequest badges 行 + 气泡（`bg-user-message-bubble rounded-[16px]`，可选 Queued chip + 内容）。子部件：`EditRequestBadge`、`InlineBadge`、`CommandBadge`、`ContextBadge`、`InlineFileBadge`。
- **Variants**：附件 image（`h-14 w-14` 方块）/ document（气泡 + 缩略图 + 两行文字）；`compactMode`。
- **States**：queued（顶部 Clock+"Queued" 斜体 chip，Clock `animate-pulse`，最短可见 `QUEUED_MIN_VISIBLE_MS=2500`）；附件 hover `hover:opacity-80`；可点击文件 badge `hover:bg-foreground/5 cursor-pointer`；isPending 视觉不变。
- **Sizing/Layout**：气泡 `max-w-[80%] rounded-[16px]`，padding 普通 `px-5 py-3.5` / compact `px-4 py-2`；图片缩略图 `h-14 w-14 rounded-[8px]`，文档缩略图 `h-11 w-8 rounded-[6px]`、文档气泡 `rounded-[8px] pl-1.5 pr-3 py-1.5 gap-2.5`（文字 `max-w-[120px]`）；EditRequestBadge `h-[28px] px-2.5 rounded-[8px] text-[13px]`；Inline/Command/Context badge `h-[22px] px-1.5 rounded-[5px] text-[12px]`，icon `12×12 rounded-[2px]`，label `truncate max-w-[200px]`，`translateY(-1px)`。
- **Tokens used**：`bg-user-message-bubble`、`bg-background`、`shadow-minimal`、`text-muted-foreground`、`bg-foreground/5·10`、`text-foreground/50·55`、`animate-pulse`。
- **Notes**：badge 按 `start`/`end` 位置切片插入文本；edit_request badge 从文本剥离后在气泡上方独立渲染；Queued chip `role="status" aria-live="polite"`；InlineFileBadge 用 Tooltip(top) 显示全路径。

### SystemMessage
- **用途**：展示 error/warning/info/system 系统消息（markdown）。
- **Anatomy**：外层 `px-4 py-2` → 内块 `text-sm px-3 py-2 rounded-md` → Markdown(minimal)。
- **Variants**：
  - error：`text-[var(--destructive-text)] shadow-tinted`，bg `oklch(from var(--destructive) l c h / 0.03)`，`--shadow-color: var(--destructive-rgb)`
  - warning：同上换 `--info-*`
  - info / system：`text-muted-foreground border border-muted bg-muted/30`
- **Notes**：error/warning 用 tinted 阴影 + 极淡 oklch 背景；`--shadow-color` 由内联 style 注入。

### InlineExecution
- **用途**：EditPopover 内紧凑展示 mini agent 执行进度，状态机 executing → success / error。
- **Anatomy**：`space-y-3` → header（状态图标 + 文案）+ activity 列表（仅 executing，取最后 3 条）+ 结果区（Markdown）+ actions 行（`border-t border-border/30 pt-1`）。
- **States**：executing（`LoadingIndicator animated showElapsed` + "editing"，Cancel 左对齐）；success（CheckCircle2 `text-success` + "done"，Done 按钮 `bg-success/10 text-success hover:bg-success/20`）；error（XCircle `text-destructive`，Dismiss + 可选 Retry `bg-accent/10 text-accent hover:bg-accent/20`）。
- **Sizing/Layout**：行 `space-y-3`，activity 列表 `space-y-0.5 pl-1`（行 `py-0.5 gap-2`），按钮 `px-2 py-1 rounded-md`，header 图标 `w-4 h-4`，按钮图标 `w-3 h-3`。
- **Tokens used**：复用 `SIZE_CONFIG.fontSize`(text-[13px])、`ActivityStatusIcon`；`text-success/accent/destructive`、`bg-success/10`、`bg-accent/10`、`border-border/30`、`prose-compact`。

### TurnCardActionsMenu
- **用途**：TurnCard header 右侧 "..." 下拉（查看文件变更 / 查看 turn 详情）。
- **Anatomy**：`SimpleDropdown`(align end) + trigger（`MoreHorizontal`）+ 两个 `SimpleDropdownItem`（FileDiff / ArrowUpRight）。
- **States**：默认 `opacity-0 group-hover:opacity-100`；open `opacity-100 text-foreground`；hover `hover:text-foreground`；focus-visible ring；无回调时整体不渲染。
- **Sizing/Layout**：trigger `p-1 rounded-[6px]`，图标 `w-3 h-3`。
- **Notes**：trigger 用 `role="button" tabIndex=0` div，拦截 Enter/Space；"查看文件变更" 仅当 `onOpenMultiFileDiff && hasEditOrWriteActivities`。

### AcceptPlanDropdown
- **用途**：桌面端 plan 接受按钮，两选项（Accept / Accept & Compact），Radix DropdownMenu 定位。
- **Anatomy**：`DropdownMenu` → trigger button（送出图标 + label + ChevronDown）→ `StyledDropdownMenuContent`(align end) 两个 item（标题 + 描述两行）。
- **States**：hover `hover:bg-success/10`；open ChevronDown `data-[state=open]:rotate-180 duration-150`；focus-visible ring。
- **Sizing/Layout**：trigger `h-[28px] pl-2.5 pr-2 rounded-[6px] gap-1.5 text-xs font-medium`，送出图标 `h-3.5 w-3.5`，Chevron `h-3 w-3`；菜单 `min-w-64 sideOffset={6}`，item `py-2 items-start`（描述 `max-w-[220px] text-xs`，标题 `text-[13px] leading-tight`）。
- **Tokens used**：`bg-success/5`、`text-success`、`hover:bg-success/10`、`shadow-tinted`(`--shadow-color: 34,136,82`)、`text-muted-foreground`、`transition-all duration-150`。
- **Notes**：用 Radix 解决 `@container`/transform/滚动容器下的定位问题。

### CompactAcceptPlanDrawer
- **用途**：紧凑场景的 plan 接受选择器，trigger 打开底部 sheet（vaul Drawer）。与 AcceptPlanDropdown 同 trigger 样式。
- **Anatomy**：`Drawer` → `DrawerTrigger`(同款 button) → `DrawerContent`（`DrawerHeader/Title` + 两个 `DrawerClose` 全宽选项按钮）。
- **Sizing/Layout**：内容区 `px-4 pb-6 flex flex-col gap-1`，选项按钮 `w-full px-3 py-3 rounded-lg gap-0.5`（标题 `text-sm font-medium`，描述 `text-xs text-muted-foreground`）；选项 hover `hover:bg-foreground/5`。
- **Notes**：与 `CompactPermissionModeSelector`/`CompactModelSelector` 同 UX；`DrawerClose asChild` 选中后自动关闭。

### SessionViewer
- **用途**：只读会话转录查看器（web viewer），将 messages 分组为 turns 并渲染 user/system/assistant 卡片，顶/底渐变淡出。
- **Anatomy**：`PlatformProvider` → `flex flex-col h-full` → 可选 header（`shrink-0 border-b`）→ 带 mask 渐变的消息区（`flex-1 min-h-0`）→ 居中内容（`CHAT_CLASSES.messageContainer`）逐 turn 渲染（user→`UserMessageBubble`、system→`SystemMessage`、assistant→`TurnCard`）→ 底部品牌 `CraftAgentLogo` → 可选 footer（`border-t`）。
- **Variants**：`mode` = `readonly`（→ TurnCard `tooltip-only`）/ `interactive`（→ `interactive`）。
- **States**：`expandedTurns`（受控 Set，`defaultExpanded` 决定初始）、`expandedActivityGroups`（受控 Set）。
- **Sizing/Layout**：来自 `CHAT_LAYOUT`（maxWidth `840px`、`px-5 py-8`、`space-y-2.5`、userMessage `pt-4 pb-2`）；mask `linear-gradient(to bottom, transparent 0%, black 32px, black calc(100% - 32px), transparent 100%)`（顶/底 32px 淡出）；Logo `w-8 h-8`，色 `text-[#9570BE]/40`。
- **Notes**：turns 由 `groupMessagesByTurn`；assistant turn 展开键 `getAssistantTurnUiKey`。

---

## 3. Overlay 系统（`components/overlay/`）

### FullscreenOverlayBase
- **用途**：所有全屏 overlay 的基底，基于 Radix Dialog 提供焦点管理/ESC/可访问性 + 全视口遮罩滚动容器 + 浮动 header。
- **Anatomy**：`Dialog.Root` → `Portal` → `Content`（`fixed inset-0`）→ `sr-only` Dialog.Title + 遮罩区（`absolute inset-0` + CSS mask 渐变）→ 滚动容器（`h-full overflow-y-auto`，paddingTop = header+fade）→ 居中包裹（`min-h-full flex flex-col justify-center`）→ 可选 `OverlayErrorBanner` + children；浮动 header（`absolute top-0 left-0 right-0 z-10`）。
- **States**：open/close（`isOpen`）；hasHeader（任一 header prop 存在）→ `contentPaddingTop = 72`，否则 `24`；error 横幅；打开隐藏 macOS 红绿灯，关闭恢复。
- **Sizing/Layout**：`HEADER_HEIGHT=48`，`FADE_SIZE=24`，`paddingBottom=24`；mask `linear-gradient(to bottom, transparent 0px, black 24px, black calc(100% - 24px), transparent 100%)`。
- **Tokens used**：背景 `bg-foreground-3` + `fullscreen-overlay-background`（模糊）；z-index `var(--z-fullscreen, 350)`，浮动 header `z-10`。
- **Notes**：`onOpenAutoFocus` preventDefault；ESC 经 `handleFullscreenEscapeWithStack()` → dismissible-layer bridge（`type:'radix-dialog'`, `priority:100`）；header DOM 顺序后渲染以视觉置顶。

### FullscreenOverlayBaseHeader
- **用途**：由结构化 props 构建 overlay header 徽章行，含文件路径双触发菜单 + 内置复制按钮。
- **Anatomy**：`PreviewHeader`(height 48, onClose, rightActions) → typeBadge(`PreviewHeaderBadge`) + filePath(`FilePathBadge` 双触发) 或 title(`PreviewHeaderBadge` onClick shrinkable) + subtitle；rightActions = 内置复制按钮 + headerActions。`FilePathBadge` = `ContextMenu`(右键) 包 `DropdownMenu`(左键) 包 badge button，菜单项 Open(ExternalLink) / Reveal in {fileManager}(FolderOpen)。
- **States**：copied（2000ms 复原，Copy↔Check）；filePath hover `group-hover:underline`；菜单项 hover `bg-foreground/[0.03]`。
- **Sizing/Layout**：filePath badge `gap-1.5 h-[26px] px-2.5 rounded-[6px] text-[13px] font-medium text-foreground/70`；复制按钮 `p-1.5 rounded-[6px]`（图标 `w-4 h-4`）；context menu `min-w-40 p-1 text-xs gap-0.5`，item `gap-2 px-2 py-1.5 pr-4 rounded-[4px]`；dropdown `sideOffset={6} align=center`。
- **Tokens used**：`bg-background shadow-minimal`、`popover-styled`、`z-dropdown`、菜单 z `var(--z-floating-menu, 400)`、复制按钮 `opacity-70 hover:opacity-100 ring-ring`、`animate-in fade-in-0 zoom-in-95`。
- **Notes**：`displayPath()` 截断为「父目录/文件名」；左键 dropdown + 右键 context menu 共享菜单项；回调来自 PlatformContext。

### PreviewOverlay
- **用途**：所有预览 overlay 的统一呈现基底，三模式（fullscreen / modal / embedded）共享同一 header + mask + 居中流式布局。
- **Anatomy**：共享 header（`FullscreenOverlayBaseHeader`）+ 共享 contentArea（遮罩 `flex-1 min-h-0 relative` + mask → `absolute inset-0 overflow-y-auto` → 居中包裹 → errorBanner + children）。embedded：`flex flex-col {bg} h-full w-full overflow-hidden rounded-lg border border-foreground/5`；fullscreen 委托 `FullscreenOverlayBase`；modal 自有 portal（`fixed inset-0 z-50 flex items-center justify-center`）。
- **Variants**：`modal` / `fullscreen`（`useOverlayMode()`，**当前恒 fullscreen**）/ `embedded`。
- **States**：modal Escape→close、背景点击→close；error 居中横幅；`!isOpen && !embedded` → null。
- **Sizing/Layout**：modal 卡片 `width:90vw`，`maxWidth: OVERLAY_LAYOUT.modalMaxWidth(1100)`，`height: 85vh`，`borderRadius:16`；`FADE_SIZE=24`；embedded `rounded-lg border border-foreground/5`。
- **Tokens used**：默认 `bg-background`（可被 `className` 覆盖）；modal 卡片 `shadow-3xl smooth-corners z-50`；mask 同 FullscreenOverlayBase（24px）。

### ContentFrame
- **用途**：预览 overlay 的共享「终端式卡片」框架——圆角卡片 + 居中标题栏，可选左右侧栏悬挂于卡片外。
- **Anatomy**：外层 `flex px-6` → `relative mx-auto` 包裹 →（可选 leftSidebar `absolute right-full mr-4`）+ 主卡片（`flex flex-col rounded-2xl overflow-hidden backdrop-blur-sm shadow-strong bg-background min-h-[320px]`：标题栏 `flex justify-center items-center px-4 py-3 border-b` + 内容区）+（可选 rightSidebar `absolute left-full ml-4`）。
- **Variants**：默认填满至 `maxWidth`（默认 850）/ `fitContent`（`width:max-content`，cap 100%，floor `minWidth`）。
- **Tokens used**：`bg-background shadow-strong backdrop-blur-sm`；标题栏下边框 `border-foreground/7`；标题 `text-xs font-semibold tracking-wider text-foreground/30`；外背景（父级）`bg-foreground-3`。
- **Notes**：卡片无内滚，超高由父滚动容器整卡滚动；`margin:auto` 处理溢出优于 items-center。

### GenericOverlay
- **用途**：未知工具内容的回退 overlay，用 PreviewOverlay + CodeBlock 高亮，自动检测语言，支持 diff 双栏。
- **Anatomy**：`PreviewOverlay`(typeBadge=FileCode, `gray`, `bg-foreground-3`) → `ContentFrame` → 滚动区，diff 模式两列 `flex gap-4 h-full p-4`（Original/Modified + `CodeBlock mode=minimal`），单内容 `p-4` + CodeBlock。
- **Notes**：`detectLanguage` / `detectLanguageFromPath`（扩展名映射），error 透传为 `{label:'Tool Failed', message}`。

### CopyButton
- **用途**：可复用复制按钮，复制后短暂显示对勾。
- **Sizing/Layout**：`w-7 h-7 rounded-[6px] flex items-center justify-center shrink-0`，图标 `w-3.5 h-3.5`。
- **States**：copied（2000ms 内 Check + `text-success`）；默认 `text-muted-foreground`，hover `text-foreground hover:bg-foreground/5`，focus-visible ring。
- **Notes**：与 header 内置复制按钮逻辑相同、样式不同（此为 `w-7 h-7` 着色款，header 为 `p-1.5 bg-background shadow-minimal opacity` 款）。

### ItemNavigator
- **用途**：overlay 项目导航——左右箭头 + 中间可点击标签（点击打开下拉直选）。
- **Anatomy**：`flex items-center gap-1 select-none` → ChevronLeft + `DropdownMenu`(标签触发 + `StyledDropdownMenuContent` 列表，活动项 Check) + ChevronRight。
- **Variants**：`size` = `sm`（内联）/ `md`（全屏）。
- **States**：首项 prev disabled / 末项 next disabled（`disabled:opacity-30 cursor-not-allowed`）；活动项 `Check text-accent`；`items.length <= 1` → null。
- **Sizing/Layout**：sm 箭头 `p-1 rounded-[6px]`(图标 `w-3.5 h-3.5`)、标签 `text-[12px] px-2.5 h-[22px] w-[112px] rounded-[6px]`；md 箭头 `p-1.5 rounded-[8px]`(图标 `w-4 h-4`)、标签 `text-[13px] px-3 h-[28px] w-[144px] rounded-[8px]`；下拉 `max-h-64 overflow-y-auto`。
- **Tokens used**：`bg-background shadow-minimal`、箭头 `text-foreground/50 hover:text-foreground`、标签 `text-muted-foreground font-medium`、活动 Check `text-accent`、下拉 z `var(--z-floating-menu, 400)`。

### OverlayErrorBanner
- **用途**：预览 overlay 的共享错误横幅，TurnCard 染色阴影风格。
- **Anatomy**：`w-full max-w-[850px] mx-auto` → 卡片（label + message）。
- **Sizing/Layout**：卡片 `px-4 py-3 rounded-[8px] max-w-[850px]`；label `text-xs font-semibold mb-0.5`；message `text-sm`。
- **Tokens used**：背景 `color-mix(in oklab, var(--destructive) 5%, var(--background))`、`shadow-tinted`(`--shadow-color: var(--destructive-rgb)`)、label `text-destructive/70`、message `text-destructive whitespace-pre-wrap break-words font-mono`。

### ZoomControls
- **用途**：缩放控制条——减/百分比下拉/加 三联组 + 重置。
- **Anatomy**：`flex items-center gap-1.5` → 分段组（`flex gap-px bg-background shadow-minimal rounded-[6px]`：Minus `rounded-l-[6px]` + ZoomDropdown + Plus `rounded-r-[6px]`）+ 重置(RotateCcw)。ZoomDropdown：百分比触发 + 弹层（Zoom to fit + 分隔线 + 预设列表，活动预设 Check）。
- **States**：`scale<=minScale` 缩小禁用 / `>=maxScale` 放大禁用 / `resetDisabled`（`disabled:opacity-30 cursor-not-allowed`）；活动预设 `Check + font-medium`；下拉点击外部/Escape 关。
- **Sizing/Layout**：按钮 `p-1.5`(图标 `w-3.5 h-3.5`)；百分比触发 `px-1 py-1 min-w-[4rem] text-[13px] tabular-nums`；弹层 `mt-1 min-w-[140px] p-1 rounded-[8px]`（项 `px-2.5 py-1.5 rounded-[4px] text-[13px]`，分隔线 `h-px bg-foreground/5 my-1`）。
- **Tokens used**：`bg-background shadow-minimal`（条/重置）、`shadow-strong border-border/50`（下拉）、hover `bg-foreground/5`、`opacity-70 hover:opacity-100`、focus-visible ring、`animate-in fade-in-0 zoom-in-95 duration-100`。
- **Notes**：ZoomDropdown 自管 open（非 Radix）；`zoomPercent = Math.round(scale*100)`。

### Preview Overlay 家族
按内容类型分派的功能变体：`CodePreviewOverlay`、`TerminalPreviewOverlay`、`JSONPreviewOverlay`、`ImagePreviewOverlay`、`PDFPreviewOverlay`、`MermaidPreviewOverlay`、`HTMLPreviewOverlay`、`MultiDiffPreviewOverlay`、`DataTableOverlay`、`ActivityCardsOverlay`、`DocumentFormattedMarkdownOverlay`，回退用 `GenericOverlay`。它们都不直接管全屏壳，而是复用同一套原语——多数包 `PreviewOverlay`（→ 三模式，全屏委托 `FullscreenOverlayBase`）并内置 `ContentFrame`，header 走结构化 props，错误走 `OverlayErrorBanner`，缩放/导航/复制复用 `ZoomControls`/`ItemNavigator`/`CopyButton`；每个变体只负责自身内容渲染与 `typeBadge`。调用方据被预览内容类型选择变体，类型未知时落 `GenericOverlay`。

---

## 4. 内容渲染（markdown / code-viewer / terminal）

### Markdown
- **用途**：多模式（terminal/minimal/full）Markdown 渲染器，支持 GFM、数学、代码高亮、可点击链接、可折叠标题。
- **Variants**：`mode` = `terminal | minimal | full`（默认 `minimal`）。另有 `MemoizedMarkdown`（流式 memo）。
- **代码 fence 分流**：`diff`/`json`/`datatable`/`spreadsheet`/`html-preview`/`pdf-preview`/`image-preview`/`markdown-preview`/`latex`/`mermaid` → 专用块，其余 → `CodeBlock`；每块由 `wrapBlock` 包 `data-ca-block-type/path/id`。
- **元素样式（节选，按 mode）**：
  - minimal：`p my-2 leading-relaxed`；`ul my-2 space-y-1 ps-[16px] list-disc`；`ol my-2 pl-6 list-decimal`；表格 `my-3 overflow-x-auto`(`th/td py-2 px-3`)；`h1` `text-[16px] font-bold mt-5 mb-3`，`h2` `text-[16px] font-semibold`，`h3` `text-[15px]`；`blockquote border-l-2 pl-3`；`hr my-4`。
  - full：间距更大（`p my-3`、`ul my-3 space-y-1.5`、表格 `my-4 rounded-md border`、`tr hover:bg-muted/30`、`blockquote border-l-4 bg-muted/30 rounded-r-md`、`hr my-6`）。
  - terminal：紧凑（`p my-1`、`pre whitespace-pre-wrap my-2`、`table text-sm`）。
- **Tokens used**：链接 `text-accent hover:underline`；列表 marker `marker:text-[var(--md-bullets)]`；`text-muted-foreground`、`border-border/50`、`bg-muted/30·50`、`divide-border`；标题 `font-sans`，代码 `font-mono`。
- **Notes**：remark `remarkGfm`+`remarkMath`(`MARKDOWN_MATH_OPTIONS` 禁单 `$` 内联以保留货币) + 折叠时 `remarkCollapsibleSections`；rehype `rehypeKatex`+`rehypeRaw`；链接 `href` 经 `defaultUrlTransform` 过滤危险 scheme，点击经 `resolveMarkdownLinkTarget` 分流 `onFileClick`/`onUrlClick`；`stableHash`(FNV-1a) 生成 block id。

### CodeBlock / InlineCode
- **CodeBlock**：Shiki 语法高亮代码块，full 模式带语言标签头 + 复制按钮。
  - **Variants**：`mode` = `terminal | minimal | full`（默认 `full`）。
  - **States**：loading（降级纯文本 `<pre>`）；copied（2000ms Check `text-success`）；hover（复制按钮 `opacity-0 group-hover:opacity-100`）。
  - **Sizing/Layout**：full 外层 `relative group rounded-[8px] overflow-hidden border bg-muted/30`，头部 `px-3 py-1.5 text-xs`（语言 `uppercase tracking-wide font-medium`），代码区 `p-3 font-mono text-sm`，复制 SVG `w-4 h-4`；注入 HTML 强制 `[&_pre]:!bg-transparent [&_pre]:!p-0 [&_pre]:whitespace-pre-wrap [&_code]:!bg-transparent`。
  - **Notes**：主题优先级 context(`useShikiTheme`) > `forcedTheme` > DOM `.dark`；语言别名表，非法降级 `text`；LRU 缓存 `CACHE_MAX_SIZE=200`（key `theme:lang:code`）；复制 `aria-label="Copy code"`。
- **InlineCode**：`<code>`，`pl-1 pr-1 rounded text-[13px] font-mono`，背景 `bg-foreground/[0.04]`，无边框。

### CollapsibleSection
- **用途**：把 Markdown 标题段渲染为可折叠区块（标题作触发器）。仅 H1–H4 可折叠（>4 直接渲染）。
- **States**：collapsed/expanded（chevron `rotate` 0↔90）；chevron 可见性——无内容 `opacity-0`、折叠 `opacity-100`、展开 `opacity-0 group-hover:opacity-100`。
- **Sizing/Layout**：chevron 绝对 `-left-4 top-[5px]`，图标 `h-3 w-3`，`text-muted-foreground`。
- **Notes**：内容 `motion` `height 0↔auto + opacity`，`duration 0.2 ease easeInOut`，`overflow-hidden`；chevron 旋转 spring（`stiffness 300, damping 25`）。

### RichBlockShell
- **用途**：给富文本块包一层 hover 才显现的编辑动作（铅笔），用于 Tiptap 编辑入口。
- **Anatomy**：`TiptapHoverActionsHost`(group) → 可选 `TiptapHoverActions`(Pencil `w-3.5 h-3.5`) → children；仅传 `onEdit` 才显示按钮。
- **Notes**：`onMouseDown` preventDefault/stopPropagation 以保持 ProseMirror 焦点/选区；`aria-label={editTitle}`。

### ShikiCodeViewer
- **用途**：只读代码查看器，行号槽 + Shiki 高亮 + 自定义滚动。
- **Anatomy**：外层 `h-full w-full overflow-auto`(bg `var(--background)`) → `min-h-full flex`（左 sticky 行号槽 + 右代码区）。
- **Variants**：`theme` = `light`(默认) / `dark`。
- **Sizing/Layout**：行号槽 `sticky left-0 minWidth:60px pr-4 px-2 select-none`，每行 `font-mono text-[13px] leading-[1.6]`；代码区 `flex-1 p-4 overflow-x-auto`，注入 HTML 强制 `whitespace-pre`（横向滚动不换行）。
- **Tokens used**：背景 `var(--background)`；行号 `rgba(255,255,255,0.3)`(dark)/`rgba(0,0,0,0.3)`(light)；右边框 `rgba(*,0.1)`/`(*,0.06)`；字体 `"JetBrains Mono"`。

### ShikiDiffViewer
- **用途**：基于 `@pierre/diffs` 的文件 diff 查看器，支持 unified/split、词级 diff、可点击文件头。
- **Variants**：`diffStyle` = `unified`(默认) / `split`；`theme` = `light`(默认) / `dark`。
- **States**：diffStyle 切换布局；`disableBackground` 切换变更行底色；file header 可点击（传 `onFileHeaderClick`）；ready（首渲 100ms 后 `transition-opacity duration-200` 淡入）。
- **Sizing/Layout**：外层 `fontFamily:"JetBrains Mono"`，`fontSize:13`，`lineHeight:1.6`。
- **Tokens used**：背景 `var(--background)`；diff 配色由 Shiki 主题（默认透明背景的 `craft-dark`/`craft-light` 走 CSS 变量）。
- **Notes**：pierre options `diffIndicators:'bars'`、`lineDiffType:'word'`、`overflow:'scroll'`；自定义元素 shadow DOM 渲染；导出 `getDiffStats(fileDiff)` 累加 add/del 计数。

### DiffViewerControls
- **用途**：diff 查看器的紧凑控制条——变更统计 + unified/split 切换 + 背景高亮开关。
- **Anatomy**：`flex items-center gap-1.5` → 统计区(`text-[13px] font-medium font-mono`：`-del` destructive / `+add` success) + diff 样式切换按钮(显示要切到的对侧图标) + 背景开关按钮。
- **States**：hover `opacity-70 hover:opacity-100`；背景已禁用 `opacity-40 hover:opacity-70`。
- **Sizing/Layout**：按钮 `p-1.5 rounded-[6px] bg-background shadow-minimal`，统计 `gap-2 mr-0.5`。
- **Notes**：按钮 `WebkitAppRegion:'no-drag'`；每按钮含 `title` + `aria-label`；切换图标语义为"目标模式"。

### TerminalOutput
- **用途**：终端命令 + 输出展示，支持 ANSI 颜色、grep 行号高亮、退出码徽章、复制。
- **Anatomy**：外层 `h-full w-full overflow-auto px-5 py-4 font-mono text-sm` → Command 区（标题行 + `<code>`）+ Output 区（标题行 + 退出码徽章 + `<pre>`）。
- **Variants**：`theme` = `light`(默认)/`dark`；`toolType` = `bash`(默认)/`grep`/`glob`。
- **States**：copied（对应按钮绿 Check，2000ms 复原）；exitCode 徽章（0 绿底绿字 `rgba(34,197,94,0.2)`/`rgb(34,197,94)`，非 0 红底红字 `rgba(239,68,68,0.2)`/`rgb(239,68,68)`）；grep 匹配行底色 `rgba(34,197,94,0.08)`。
- **Sizing/Layout**：Command `mb-4`，标题行 `mb-2 text-xs`（图标 `w-3 h-3`），复制 `p-1`(图标 `h-3.5 w-3.5`)；退出码徽章 `px-1.5 py-0.5 rounded text-[10px]`；grep 行号 `pr-3 text-right minWidth:3rem`；字体 `"JetBrains Mono"`。
- **Tokens used**：⚠️ **大量硬编码内联颜色而非设计 token**——text `#e4e4e4`/`#1a1a1a`，muted `#888`/`#666`，match `#22c55e`，cmd `#60a5fa`/`#2563eb`，codeBg/outputBg 用 rgba alpha；命令 `<code>` 用 `text-foreground`。
- **Notes**：`parseAnsi` 解析、`stripAnsi` 清复制内容；`isGrepContentOutput`+`parseGrepOutput`；带背景 ANSI span 加 `padding:0 2px; borderRadius:2px`；`whitespace-pre-wrap break-words`。

---

## 5. 组件通用约定（跨组件提炼）

这些是从上述组件反复出现的模式中提炼的「隐性规范」，新建组件时应遵循：

1. **浮动控件三件套**：`bg-background` + `shadow-minimal` + `rounded-[6px]`（PreviewHeader 关闭按钮、ZoomControls、DiffViewerControls、ItemNavigator、PreviewHeaderBadge 全部一致）。
2. **图标尺寸梯度**：超小 `w-3 h-3`（密集行内/header 内） < `w-3.5 h-3.5`（最常用，按钮内默认） < `w-4 h-4`（独立动作按钮）。
3. **复制交互**：统一 `navigator.clipboard.writeText`，成功 → `text-success` + Check，**2000ms** 复原，失败仅 `console.error`。
4. **菜单项规范**：`rounded-[4px]`，hover/focus `bg-foreground/[0.03~0.05]`，destructive 项用 `text-destructive`，图标插槽 `h-3.5 w-3.5 shrink-0`。
5. **次要动作 hover 才现**：`opacity-0 group-hover:opacity-100`，并保证 `focus-visible:opacity-100` 不丢可访问性。
6. **focus 环**：可聚焦控件统一 `focus-visible:ring-1 focus-visible:ring-ring`。
7. **Electron 拖拽区豁免**：标题栏内可点击控件加 `style={{ WebkitAppRegion: 'no-drag' }}`，左右各留 `min-w-[70px]` 给 macOS 交通灯。
8. **滚动边缘淡出**：长内容区用 `mask-image` 线性渐变（聊天 32px、overlay 24px、TurnCard 暗色 16px）而非硬边界。
9. **等宽数字**：step 计数、缩放百分比、时长、diff 统计一律 `tabular-nums`。
10. **弹层两条路线**：vibrancy 一致样式 → `StyledDropdown*`（Radix + `popover-styled` + `z-dropdown`）；需精确锚点/轻量自管 → `getBoundingClientRect` + `fixed` + `z-floating-menu/z-floating-backdrop`，配 `animate-in fade-in-0 zoom-in-95 duration-100`。
11. **代码/终端字体**：所有等宽场景固定 `"JetBrains Mono"` + `text-[13px]` + `leading-[1.6]`。
12. **染色阴影用于语义卡片**：error/warning 类卡片用 `.shadow-tinted` + 对应 `--shadow-color`（`destructive-rgb`/`info-rgb`）+ 极淡 oklch 背景（见 SystemMessage / OverlayErrorBanner）。
