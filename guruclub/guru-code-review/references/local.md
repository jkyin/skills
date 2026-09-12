# 本地范围与 base

仅在本地审查时读取；MR 已声明的目标分支与 diff refs 由 [GitLab 取证](gitlab.md) 处理。

## 范围优先

先采用用户指定的对象：

| 请求 | 比较内容 |
| --- | --- |
| 未暂存改动 | `git diff` |
| 已暂存改动 | `git diff --cached` |
| 全部未提交改动 | `git diff HEAD`，另用 `git ls-files --others --exclude-standard` 识别未跟踪文件并按范围读取 |
| 单个提交 | `git show <sha>`；merge commit 的比较父节点按请求确认 |
| 两个明确快照 | `git diff <ref1> <ref2>` |
| 分支相对目标的工作 | 确认 base 后 `git diff <base>...HEAD` |

用户只说“我的改动”且分支、暂存、未暂存各有不同工作时，先列出紧凑清单再确认含义。明确范围时不反复询问，也不将其他范围混入。

## 分支 base

1. 采用用户指定且可解析的比较分支/ref。
2. 没有指定时，结合本轮已知合并目标、有效项目分支约定和实际 remote HEAD 判断，并显示依据。`git symbolic-ref refs/remotes/origin/HEAD --short` 仅在实际 remote 为 origin 时使用；默认分支是候选，不必然是该 feature 的目标。
3. `git rev-parse --abbrev-ref --symbolic-full-name '@{u}'` 只提供跟踪信息。若 upstream 是当前 feature 的远端副本，不能用它替代目标分支，否则已推送的改动可能全部消失。
4. 分支名字和 merge-base 距离只能辅助比较，不能证明分支的创建来源。候选冲突、多个 merge base 或缺少可靠依据时，展示候选再问一个必要问题，不按 main/master/develop 名称排序猜。

确定后记录实际 ref 和 SHA，并运行：

```bash
git merge-base --all "<已确认 base>" HEAD
git diff "<已确认 base>...HEAD"
git diff --name-only "<已确认 base>...HEAD"
```

上面的三点比较使用共同祖先到 HEAD；若已得到唯一 merge-base SHA，`git diff <merge-base-sha> HEAD` 等价。两点形式比较的是两个端点；不能笼统宣称在已使用 merge-base SHA 时两点会引入目标分支的新变化。[Git 官方说明](https://git-scm.com/docs/git-diff)

用一句话说明“对照哪个 ref、依据及 merge-base SHA、覆盖哪些改动”。已确定的范围用告知即可，不再要求用户确认同一结论。

历史信息只在解释变更必要时读取，例如 `git log -p --follow -- <file>`、`git blame -L <start>,<end> -- <file>`。本地报告不调用发布接口，不因没有平台工具中止明确的本地审查。
