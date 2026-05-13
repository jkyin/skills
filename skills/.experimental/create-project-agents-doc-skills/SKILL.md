---
name: create-project-agents-doc-skills
description: 在当前项目创建或更新项目级 agents 文档维护 skills。用于生成 .codex/skills 与 .claude/skills 下的 maintain-agents-docs 和 prune-agents-docs，并在规则涉及外部事实、官方资料、第三方 API/SDK、平台政策、协议规范、依赖升级或安全要求时要求 web 搜索核对来源；同时按 AGENTS.md 面向所有 coding agents、CLAUDE.md 仅面向 Claude Code 的分工写入使用提示，不把完整 skill 内容塞进根级文档。
---

# 创建项目 Agents 文档 Skills

使用本 skill 在当前项目中创建项目级 `maintain-agents-docs` 和 `prune-agents-docs`。生成结果必须适配目标项目，而不是复用 AgenticBoard 或其他项目的具体规则。

## 目标产物

默认创建 Codex 侧项目级 skill：

- `.codex/skills/maintain-agents-docs/SKILL.md`
- `.codex/skills/maintain-agents-docs/agents/openai.yaml`
- `.codex/skills/prune-agents-docs/SKILL.md`
- `.codex/skills/prune-agents-docs/agents/openai.yaml`

如果项目存在 `.claude/skills`、`CLAUDE.md`，或用户明确要求 Claude 也可用，创建 Claude 侧项目级 skill：

- `.claude/skills/maintain-agents-docs/SKILL.md`
- `.claude/skills/maintain-agents-docs/agents/openai.yaml`
- `.claude/skills/prune-agents-docs/SKILL.md`
- `.claude/skills/prune-agents-docs/agents/openai.yaml`

`name` 必须保持英文标识符：`maintain-agents-docs` 和 `prune-agents-docs`。正文优先使用目标项目的主要语言；若不确定，使用中文并保留命令、文件名、API 名和类型名原文。不要把 skill 放在 `.agents/`。

## 项目勘察

创建前先收集目标项目上下文：

- 查找指令文件：`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md`、`.cursorrules`、现有 `.codex/skills`、`.claude/skills`。
- 检查项目结构：`rg --files` 或等价方式，定位 docs、src、tests、scripts。
- 检查 git 状态：`git status --short`，避免覆盖用户已有改动。
- 读取现有根级指令文件全文。
- 读取与项目核心约定相关的 docs 或代码入口；不要只看文件名猜规则。
- 如果项目规则依赖外部事实、官方文档、平台行为、框架/API 语义或近期变化，使用 web 搜索核对最新官方资料；优先官方文档、规范、发布说明和仓库文档，记录来源 URL。

遵守根级文档分工：

- `AGENTS.md` 放项目根目录，给所有 coding agents 使用。
- `CLAUDE.md` 放项目根目录，只给 Claude Code 使用。
- `CLAUDE.md` 不要变成第二份 `AGENTS.md`。
- `AGENTS.md` / `CLAUDE.md` 不承载完整 skill 内容，只写“什么时候使用哪个 skill”。

如果目标项目没有 `AGENTS.md` 或 `CLAUDE.md`，生成 skill 时仍要把文件名写成可配置目标：优先维护已存在的 agents instruction 文件，并在 workflow 中说明需要先发现目标文件。

## 提炼项目专属语义

必须从目标项目提炼 protected semantics。不要复制 AgenticBoard 的 Codex thread、Process Rollup、rich VM 等规则，除非目标项目本身确实有这些约定。

可作为 protected semantics 的内容包括：

- 代码或文档明确要求长期保留的架构 invariant。
- 安全、权限、命令执行、数据迁移、destructive 操作相关规则。
- 项目特有的测试、验证、发布或生成物规则。
- provider、平台、框架或协议层的不可丢失语义。
- 团队明确写在 `AGENTS.md` / `CLAUDE.md` / docs 中的工作方式。
- 经 web 搜索核实的外部官方约束，例如平台政策、SDK/API 行为、协议规范或安全要求；必须保留来源 URL。

不能作为 protected semantics 的内容包括：

- 一次性实现细节。
- commit summary 或 changelog。
- 没有证据的未来设计猜测。
- 只属于另一个项目的专有约定。
- 未经官方资料或项目代码佐证的搜索结果、博客观点或论坛经验。

## Web 搜索支持

生成的 `maintain-agents-docs` 和 `prune-agents-docs` 必须支持 web 搜索，并明确这些规则：

- 当候选规则涉及最新外部事实、官方资料、第三方 API/SDK、平台政策、协议规范、依赖升级或安全要求时，必须先 web 搜索核对。
- 优先使用官方文档、规范、发布说明、API reference、项目仓库和可信安全公告；避免把博客、论坛或二手摘要作为唯一依据。
- web 搜索只补充外部证据；项目本地事实仍以仓库代码、docs、现有 agents 指令和 git 历史为准。
- 写入 agents docs 的外部规则必须带来源 URL 或可追溯来源说明；无法核实时只作为保留候选，不提升为 durable rule。
- 如果当前环境不能联网或不能使用 web 搜索，最终回复必须说明缺口，并列出哪些外部事实没有完成核对。

## 生成 maintain-agents-docs

生成的 `maintain-agents-docs` 必须表达这些机制：

- 目的：刷新项目 agents 指令，让规则保持最新，而不是一味追加补丁。
- 生命周期顺序：`update -> merge -> move -> add`。
- 证据来源：用户请求、现有指令、当前 diff、staged diff、未 push commits、最近 6 个 commits、相关源码/docs、web 搜索核对过的官方资料。
- 提升门槛：只有 durable rule 才能进入 agents docs。
- 放置门槛：`AGENTS.md` 放所有 coding agents 公共规则和 skill 使用时机；`CLAUDE.md` 只放 Claude Code 专属约束和 Claude 侧 skill 使用提示；完整 skill 内容放 `.codex/skills` 或 `.claude/skills`。
- 边界：不大规模删除、不重写整个文件、不添加 commit log、不单次新增超过 5 条规则。
- 审查摘要：最终回复必须说明证据来源、web 搜索来源 URL 或未联网缺口、动作数量、保留候选项和是否触碰 protected semantics。
- protected semantics：使用从目标项目提炼出的内容。

## 生成 prune-agents-docs

生成的 `prune-agents-docs` 必须表达这些机制：

- 目的：精简和收敛现有 agents 指令，不从最新 commit 添加新规则。
- 生命周期顺序：`merge -> shorten -> move -> delete`。
- 证据来源：目标文件全文、`rg` 引用检查、git 状态、证明 stale/重复/错放/低价值的相关代码或文档；涉及外部事实 stale 判定时，使用 web 搜索核对官方资料。
- 边界：可删除低价值规则、合并重复规则、缩短啰嗦规则、移动错放规则。
- 禁止：从最新 commit 添加新规则、改变文件风格、删除命令/安全规则除非明确 stale。
- 删除门槛：只有 redundant/stale/misplaced/non-operational 且不破坏 live reference 时才能删除。
- web 搜索边界：只能用于核实外部事实是否过期或官方约束是否变化，不能借搜索结果新增最新 commit 规则。
- protected semantics：使用从目标项目提炼出的内容，并默认保护命令、安全和项目核心语义。

## 写入规则

- 若目标 skill 已存在，先读取现有内容并更新，不要盲目覆盖。
- Codex skill 放 `.codex/skills/`；Claude skill 放 `.claude/skills/`；不要使用 `.agents/`。
- `.codex` 和 `.claude` 的 skill 可以共享生命周期机制，但描述中要尊重各工具入口差异。
- `agents/openai.yaml` 使用目标项目语言；`default_prompt` 必须包含 `$maintain-agents-docs` 或 `$prune-agents-docs`。
- 不创建 README、安装说明、changelog 或额外辅助文档。
- 不把完整 skill 内容写入 `AGENTS.md` 或 `CLAUDE.md`；根级文档只写什么时候使用哪个 skill。
- `CLAUDE.md` 只写 Claude Code 专属约束，不重复 `AGENTS.md` 的公共规则。
- 如果项目 `.gitignore` 忽略 `.codex/` 或 `.claude/`，最终回复必须提醒用户。

## 验证

完成后执行这些检查：

- 校验每个 `SKILL.md` frontmatter 只有合法字段，`name` 为 hyphen-case，`description` 不超过 1024 字符。
- 检查没有模板 `TODO` 残留。
- 对比 `.codex` 和 `.claude` 对应 skill，确认应该一致的内容确实一致。
- 检查 `agents/openai.yaml` 的 `display_name`、`short_description` 和 `default_prompt` 存在且与 skill 职责一致。
- 检查生成的 maintain/prune skills 明确包含 web 搜索规则，并要求最终回复报告搜索来源 URL 或未联网缺口。
- 最终回复说明创建了哪些文件、项目专属 protected semantics 来自哪里、是否更新了根级 skill 使用提示、哪些目录被 git ignore、web 搜索是否完成及来源。
