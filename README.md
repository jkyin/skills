# Agent Skills

这个仓库用于制作和分发个人或项目可复用的 Codex skills，布局参考 `openai/skills`。

## 目录结构

```text
skills/
  .curated/        # 相对稳定、可按名称安装的 skills
  .experimental/   # 实验中或个人使用的 skills
  .system/         # 系统级 skills；本仓库通常不放这里
```

当前包含：

- `guruclub/`：GuruClub 周报、月报、Code Review、MR 描述和提交规范；[来源与版本说明](guruclub/README.md)
- `skills/.experimental/create-project-agents-doc-skills`
- `skills/.experimental/feature-spec`
- `skills/.experimental/task-card`

## 安装

推荐使用 Codex 内置的 `$skill-installer`。

按 GitHub 目录 URL 安装需要的 skill：

```text
$skill-installer install https://github.com/jkyin/skills/tree/main/skills/.experimental/create-project-agents-doc-skills
$skill-installer install https://github.com/jkyin/skills/tree/main/skills/.experimental/feature-spec
$skill-installer install https://github.com/jkyin/skills/tree/main/skills/.experimental/task-card
```

安装完成后，skill 会在下一轮对话中可用；若未出现，再重启 Codex。

## 维护规则

- 每个 skill 是一个独立目录，必须包含 `SKILL.md`。
- UI metadata 放在 `agents/openai.yaml`。
- 不为单个 skill 添加 README、安装说明或 changelog；必要说明写进 `SKILL.md`。
- 实验中的 skill 放 `skills/.experimental/`。
- GuruClub 业务 skills 按领域集中放在 `guruclub/<skill-name>/`。
- 稳定后再移动到 `skills/.curated/`。
