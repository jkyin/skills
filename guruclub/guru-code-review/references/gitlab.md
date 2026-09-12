# GitLab 取证

MR URL 提供 host、项目路径和 IID；未给 URL 时从已核实的 remote 与分支定位。GuruClub 默认 host 为 `git.gelonghui.com`，不能靠是否含 gitlab.com 判断平台。

使用 `glab` CLI/API，并显式传目标 host。项目路径整体 URL 编码；下文占位符须用本轮已核实值替换。先读取当前 CLI 帮助确认支持的参数，不用浏览器或读取其他凭据绕过认证。

```bash
glab auth status --hostname "<host>"
glab api --hostname "<host>" "projects/<project>/merge_requests/<IID>"
```

## 当前审查快照

读取 MR 的作者、state/Draft、source_branch、target_branch、sha、diff_refs。`target_branch` 是 MR 的合并目标，不执行本地 base 猜测；diff_refs 锁定具体比较快照。

按 [MR API](https://docs.gitlab.com/api/merge_requests/) 及实例版本读取完整 diffs/commits；列表端点取完分页。常用端点：

- `projects/<project>/merge_requests/<IID>/diffs`
- `projects/<project>/merge_requests/<IID>/commits`
- `projects/<project>/merge_requests/<IID>/discussions`
- `projects/<project>/merge_requests/<IID>/pipelines`

分页需结合当前 `glab api` 的 `--paginate` 帮助或逐页请求；检查响应中的截断、过大文件或折叠 diff 标记，不能把 API 返回的部分结果称为完整 diff。旧实例只有其他端点时先核实支持情况。

源码必须与被审查 head 对应：本地 HEAD 不同、有脏改动、MR 来自 fork 或文件被删除时，使用相应仓库/ref 的对象或只读 repository API。不要为了读文件覆盖当前工作区；删除代码从旧侧读取，rename 同时保留 old/new path。

检查当前 head 对应的讨论、已有审查意见、pipeline 及必要 job；旧 head 的成功 CI 不代表当前通过。按变更读取消费者、依赖解析结果和相关历史。连续复审时明确上次已审 SHA 与本次增量及仍适用的契约。

取证后核对 head 未变化，变化则刷新受影响证据，不能混用 SHA。持续变化或权限缺口时报告已覆盖部分与未完成项，不以本地辅助分析替代远程审查。

只有进入已授权评论写入时才读 [评论接口与定位](gitlab-comments.md)。
