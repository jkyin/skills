# GuruClub skills

本目录是五类 GuruClub 工作流的唯一维护源。2026-09-13 已完成规则精简与安装入口统一；现有 Codex、Agents、Claude 的 11 个入口均链接到这里。

## 技能与导入来源

| 技能 | 导入时本机源目录 | 当前入口行数 |
| --- | --- | --- |
| [周报](guruclub-weekly-report/SKILL.md) | `~/.codex/skills/guruclub-weekly-report` | 24 |
| [月报](guruclub-monthly-summary/SKILL.md) | `~/.codex/skills/guruclub-monthly-summary` | 40 |
| [Code Review](guru-code-review/SKILL.md) | `~/.agents/skills/guru-code-review` | 49 |
| [MR 描述](guru-mr-description/SKILL.md) | `~/.codex/skills/guru-mr-description` | 29 |
| [提交规范](guru-commit/SKILL.md) | `~/.agents/skills/commit-expert` | 46 |

每项保持独立、自包含；references 在需要对应流程时加载。以后直接修改 `guruclub/<skill-name>/`，通过现有链接共用，无需维护客户端副本。不要将历史差异目录作为 skill 安装。

提交规范已由 `commit-expert` 改名为 `guru-commit`，使用 `$guru-commit` 调用；表中和导入记录中的旧名称仅用于追溯原始来源。

## 本次调整

- 收窄触发描述；提交规范明确 message、准备、commit、push 的不同范围，避免整仓暂存或无授权的第二个格式化提交。
- 周报/月报都保留明确调用、首次范围确认和 `allow_implicit_invocation: false`；空回答不再当同意，同轮已确认内容不重复询问。
- Code Review 按风险选择独立视角和上下文；统一 GitLab 与本地 base 规则，远程取证失败不冒充完整审查；草稿、公开发布、approve 和 merge 分别判断授权。
- Swift 清单改为基于实际路径与影响，不将语法模式固定为 CRITICAL；月报填写按列名映射，不假定前三列。
- 周报的范围、证据、表格、Confluence 和提醒分开按需读；月报计算细则放入取证 reference，原统计脚本和调用策略未变。
- MR 描述按复杂度组织，以最终实现为中心；外部写入和故障处理按需加载，移除缺失的 code-formatter 依赖。

[原始建议](ASTRA-RECOMMENDATIONS.md) 保留为本次决策记录，观察针对改写前的源码。

## 来源与历史差异

[sources.json](sources.json) 保存 18 份导入文件的原始来源及导入哈希，是历史快照，不能用于校验已改写的技能正文。各源位置如今可能已成为指向本仓库的链接。

导入时：周报/月报的 Claude 入口链接到 Codex，提交规范的 Claude 入口链接到 Agents；MR 描述的 Codex/Claude 正文相同。Code Review 的 Agents/Claude 目录独立，两个 references 存在差异。

Claude 的两份旧 reference 保存在 [source-variants/claude/guru-code-review/references](source-variants/claude/guru-code-review/references/)，仅供历史追溯，不再参与执行。当前主目录已统一并纠正 base 推断规则；不能把这两份旧文件覆盖回去当成当前版本。

这些位置是已核实的本机导入来源，不代表找到了最初创作时的 Git 仓库。`guruclub-cms` 电报/题材属于另一个插件及配套 MCP 服务，未混入本目录。

## 安装、备份与恢复

[scripts/link_installed.py](scripts/link_installed.py) 只处理明列的 11 个既有入口，缺失入口跳过；先输出计划，执行时核对入口未变化，再备份和链接。重复执行不重复备份已指向本仓库的入口，普通执行失败会回退已完成部分。

本次备份：`/Users/jkyin/.codex/backups/guruclub-skills-20260913-011245-092576/`。

计划与结果见 [install-plan.json](validation/install-plan.json)、[installation.json](validation/installation.json)。未来重新切换时：

```bash
python3 guruclub/scripts/link_installed.py --plan /tmp/guruclub-install-plan.json
# 阅读计划后再执行
python3 guruclub/scripts/link_installed.py --apply --plan /tmp/guruclub-install-plan.json
```

如需恢复本次切换前的安装入口，从本项目执行：

```bash
python3 guruclub/scripts/link_installed.py --restore /Users/jkyin/.codex/backups/guruclub-skills-20260913-011245-092576/restore.json
```

恢复工具兼容此次 `commit-expert` → `guru-commit` 入口改名，会将原备份恢复到原入口名称。恢复仅替换仍指向本次目标的入口，不覆盖切换后被另行改动的入口。该操作不删除本仓库修订，也不执行 Git 操作。

## 验证

- 五项技能均通过官方 `quick_validate.py`：[结构结果](validation/structure.json)。PyYAML 仅临时安装到 `/private/tmp/guruclub-skill-validation-deps`，未加入项目或系统依赖。
- 独立 agent 完成八个离线场景，并复验修订后的 Confluence/Swift 路径及两个 MR 描述场景：[场景记录](validation/forward-test.md)。首轮发现与后续复验都保留，后续复验为当前结论。
- 临时 home 验证 11 入口切换、幂等、恢复、旧计划拒绝与缺失入口跳过：[安装测试](validation/link-installation.json)。注入中途失败、临时 Git base 场景、业务脚本/策略不变和链接完整性见 [离线检查](validation/behavior-checks.json)。
- 实际切换后核实 11 个链接目标，并验证备份内 18 份原始文件与导入哈希一致。
- 未执行真实周报/月报采集、MR 评论/描述写入、业务 Git 提交或 Confluence 发布；离线场景不能替代这些业务环境的实际验收。

可重跑的标准库离线检查：`PYTHONDONTWRITEBYTECODE=1 python3 guruclub/validation/check_local.py`。本脚本仅在临时目录建 Git fixture 和安装入口，不改用户实际安装。
