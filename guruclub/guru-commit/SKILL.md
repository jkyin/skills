---
name: guru-commit
description: 为 GuruClub 及其 iOS 库准备或执行已授权的 Git 提交，检查依赖引用并生成中文提交信息。
---

# GuruClub Git 提交规范

## 执行边界

- 只生成 message：读取必要 diff 后给出 message，不暂存、格式化、commit 或 push。
- 准备提交：明确文件/hunk 范围、message 和必要验证，做到可审阅；未获提交授权则到此结束。
- 执行提交：已有对本轮具体范围的明确授权就继续，不机械重复确认。同一文件内的无关改动、已有暂存内容也不自动纳入。
- 推送、amend 或改写远端历史分别判断授权；commit 不隐含 push。缺少目标或操作授权时先完成只读检查和可审阅方案，再用当前环境允许的方式询问必要信息。

只查看 Git 状态、解释 Git 命令或一般仓库操作，不进入本 skill 的提交流程。

## 准备与检查

读取 `git status --short`、暂存及工作区 diff、近期 message，确定工作区和本轮范围。按逻辑拆分提交，不清理无关改动，不自动 stash、还原或整仓暂存。

- 在实际 GuruClub 主项目且存在 `Podfile.rb` 时，检查本次依赖是否仍引用 `local_pod`；发现时读取 [Pod 引用](references/podfile.md)。Pod 模块自身不套用主项目检查，不仅凭文件夹名认定项目。
- `Podfile.lock` 已明确纳入本轮范围则核对并保留；未明确纳入的变更保持原状。只有该提交必须依赖 lockfile 同步时，展示具体差异再询问是否扩展范围。
- 本轮包含 Swift 改动时读取 [格式化](references/formatting.md)。格式化独立成提交，保留项目约定和授权边界；纯文档、配置或脚本改动不自动运行 SwiftFormat。
- 使用与改动相称的项目检查；通过后不重复扩大验证。遵守项目禁止本地 fastlane 等约束，不把 CI 等待误报为通过。

## Message

格式为 `<type>: <简洁中文描述>`，不超过 72 字、无句号，API/文件名保留原文；不加 Co-Authored-By 等额外标签。

| type | 适用内容 |
| --- | --- |
| feat | 新功能 |
| fix | 修复问题 |
| refactor | 重构 |
| style | 纯格式化 |
| docs | 文档 |
| chore | 工具或依赖 |
| test | 测试 |

例如 `fix: 修复播放结束后封面显示异常`。message 概括最终变更，不罗列过程。

## 提交与完成

执行前核对暂存区只含该提交的已授权内容；按明确路径或 hunk 暂存，不用 `git add .`、`git add -A` 或 `git commit -a` 扩大范围。无关内容已暂存时，不将其带入，也不擅自取消用户暂存；使用可隔离的提交方式或提出具体冲突。

提交后回读 SHA、提交内容和剩余工作区。只在已授权时推送对应 remote/ref，并核实结果。最终报告 message、SHA、验证边界及未推送/已推送状态；未提交的准备任务交付具体范围和建议 message。
