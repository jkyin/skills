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

- `skills/.experimental/create-project-agents-doc-skills`
- `skills/.experimental/craft-agents-design-system`
- `skills/.experimental/feature-spec`
- `skills/.experimental/task-card`

## 安装

推荐使用 Codex 内置的 `$skill-installer`。

从 GitHub 目录 URL 安装：

```text
$skill-installer install https://github.com/<owner>/<repo>/tree/main/skills/.experimental/create-project-agents-doc-skills
```

如果本仓库以后有 `.curated` skills，可以按名称安装：

```text
$skill-installer create-project-agents-doc-skills
```

安装后重启 Codex，让新 skill 生效。

## 维护规则

- 每个 skill 是一个独立目录，必须包含 `SKILL.md`。
- UI metadata 放在 `agents/openai.yaml`。
- 不为单个 skill 添加 README、安装说明或 changelog；必要说明写进 `SKILL.md`。
- 实验中的 skill 放 `skills/.experimental/`。
- 稳定后再移动到 `skills/.curated/`。
