# Agent Skills

这个仓库用于制作和分发个人或项目可复用的 Codex skills，布局参考 `openai/skills`。

## 目录结构

```text
.
├── README.md
├── contributing.md
└── skills/
    ├── guruclub/
    │   ├── guru-review-triage/
    │   ├── guru-code-review/
    │   ├── guru-commit/
    │   ├── guru-mr-description/
    │   ├── guruclub-monthly-summary/
    │   └── guruclub-weekly-report/
    └── .experimental/
        ├── create-project-agents-doc-skills/
        ├── feature-spec/
        └── task-card/
```

`.curated/` 与 `.system/` 当前不存在，不需要为空目录占位。

当前技能：

- `skills/guruclub/`：GuruClub 周报、月报、Code Review、AI Review 裁决、MR 描述和提交规范。
- `skills/.experimental/create-project-agents-doc-skills`
- `skills/.experimental/feature-spec`
- `skills/.experimental/task-card`
- `skills/guruclub/guru-review-triage`：逐条裁决私有 GitLab MR 的已有评审评论（AI 或人工），按证据收敛本 MR 必修项。

## 安装

推荐使用 Codex 内置的 `$skill-installer`。

按 GitHub 目录 URL 安装需要的 skill：

```text
$skill-installer install https://github.com/jkyin/skills/tree/main/skills/.experimental/create-project-agents-doc-skills
$skill-installer install https://github.com/jkyin/skills/tree/main/skills/.experimental/feature-spec
$skill-installer install https://github.com/jkyin/skills/tree/main/skills/.experimental/task-card
$skill-installer install https://github.com/jkyin/skills/tree/main/skills/guruclub/guru-review-triage
```

安装 URL 须对应远端已推送的目录；仅有本地提交时，新 skill 的远程安装入口仍不可用。

安装完成后，skill 会在下一轮对话中可用；若未出现，再重启 Codex。

## 维护规则

- 每个 skill 是一个独立目录，必须包含 `SKILL.md`。
- 需要 UI metadata 或 Codex 调用策略时放在 `agents/openai.yaml`，不要求每个 skill 都有该文件。
- 不为单个 skill 添加 README、安装说明或 changelog；必要说明写进 `SKILL.md`。
- 实验中的 skill 放 `skills/.experimental/`。
- GuruClub 业务 skills 按领域集中放在 `skills/guruclub/<skill-name>/`。
- 通用实验 skill 稳定后可移动到 `skills/.curated/`；GuruClub 业务 skill 保留领域目录。
- Python 缓存属于本地产物，由 `.gitignore` 排除，不纳入 skill 分发内容。
- 修改后检查本地引用并运行适用的 skill 校验；保留跨客户端字段时分别说明校验器的兼容性限制。
