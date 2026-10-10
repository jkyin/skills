# 私有 GitLab MR 取证与讨论操作

只在需要远程 MR 取证或获授权写入时读取本页。接口以目标 GitLab 实例实际支持的版本为准：[Merge requests API](https://docs.gitlab.com/api/merge_requests/)、[Discussions API](https://docs.gitlab.com/api/discussions/)。

## 读取

1. 从 MR URL 取得 host、项目路径和 IID，或从已核实的 remote/分支定位。优先用现有 `glab` 身份与 `glab api --hostname <host>`；项目路径整体 URL 编码。先核对 `glab` 本机帮助，不猜不支持的参数。
2. 读取 MR 详情中的 `sha`、`diff_refs`、source/target branch 与状态；取全 diffs/commits/discussions 的分页，检查 `too_large`、截断和折叠标记。历史实例若不支持 `/diffs`，确认后改用可用的 `/changes` 或版本接口。一次状态读取即可；不轮询。
3. 保留每个 discussion 下的全部 notes。识别原始评论、后续修正、是否已 resolve、是否仍能定位；不要用 AI summary 的编号替代 note ID。对当前 head 的文件取证，必要时查父版本与依赖锁定版本。本地 HEAD 不一致时使用对应 Git 对象或只读 repository API，不覆盖脏工作区。
4. 取证后核对 head 是否仍相同；若变化，只刷新受影响的证据。认证/网络失败可报告明确缺口和已完成的本地辅助分析，不冒充远程完整裁决；内网场景可尝试已授权的 host 网络路径，不反复撞同一失败路径。

## 已获授权的回复与 resolve

- 回复原线程：`POST /projects/:id/merge_requests/:merge_request_iid/discussions/:discussion_id/notes`，传 `body`。不要用 MR 级 notes API 留下游离回复。
- 解决讨论：`PUT /projects/:id/merge_requests/:merge_request_iid/discussions/:discussion_id`，传 `resolved=true`。若 `resolvable=false`，报告接口限制，不声称已 resolve。
- 每次写入前核对目标 discussion 和当前 head；写入后回读 note 是否出现在该线程、正文是否正确、讨论是否 resolved。POST 返回失败或超时先回读是否已写，避免重发。GET 成功不保证 POST 权限；分别报告实际结果。
- 多条部分成功时列出已写 note ID、已 resolve discussion ID 和未完成项。不因修复提交、diff 变化或机器人自动状态变化而推断评论已经得到回复。
