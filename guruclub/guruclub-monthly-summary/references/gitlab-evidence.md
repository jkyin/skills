# GitLab 取证与统计

仅在执行月度数据收集时读取本文件。所有 GitLab 操作均为只读。

## 来源参数

从开始前的确认结果取得每个来源的 `host` 和 `project_path`。默认值分别为 `git.gelonghui.com`、`ios/guruclub`；用户选择其他项目时必须替换，不把默认值当成固定检索范围。

将项目路径整体 URL 编码，例如 Python `urllib.parse.quote(project_path, safe="")`。下文 `{project}` 表示编码后的项目路径或已核实的数字项目 ID。`REPORT_GITLAB_HOST` 表示本轮确认的主机名，使用任务专属变量，不修改通用环境配置。

每个主机分别核对当前用户身份；不同主机的同名用户 ID 不能混用。每个项目独立分页并保存到 `work/<source-key>/`，跨来源用“主机/项目/MR IID”组合标识，不能只用 IID 去重。非 GitLab 来源不得直接套用这些端点或提交 JSON 格式。

## 当前身份与候选集合

1. 调用 `glab api --hostname "$REPORT_GITLAB_HOST" user`，用返回的 `id` 筛选作者，不根据本地 Git 姓名、审核人或 assignee 猜测归属。
2. 将用户指定月份的月初按 `Asia/Shanghai` 换算为 UTC，作为候选搜索的 `updated_after`。它只用于缩小检索范围，不是最终计入口径。
3. 分页读取 `projects/{project}/merge_requests`，参数包括 `scope=all`、`state=all`、`author_id`、`updated_after`、`order_by=updated_at`、`sort=desc`、`per_page=100` 和 `page`。
4. 直到分页结束，不把第一页当成全部。对会话明确提到但候选检索没覆盖到的 MR 额外读取；仍核对作者、状态和本月提交活动。
5. 只保留 `author.id` 等于当前身份、`state` 为 `opened` 或 `merged` 的候选。排除 `release/…` 分支和实际用于 release 集成或提版的 MR。不要仅因正常功能描述里含有 release 一词就误排除。

`glab` 不支持 `--jq` 时，用 Python 标准库解析 JSON。调用 shell 时正确引用 URL 参数；也可以用 `subprocess.run([...])` 避免字符串拼接和 shell 展开。认证失败、DNS/网络受限、权限不足分别处理，不输出 token。无法取得的数据明确标为缺失。

## 锁定 MR 与完整提交记录

对每个候选读取最新 MR 详情及：

- `projects/{project}/merge_requests/{iid}/commits`，取完所有分页。
- MR `sha` / `diff_refs.head_sha`、作者、Draft 标记、目标分支、合并和 squash SHA。
- 原始描述及需要解释实际变更的提交信息；描述里的验证结论有争议时回查相关会话或验证输出。

记录检索时间。取完提交后核对 head 没变化；若变化，重取该 MR，不能混用不同 head 的统计和状态。保留获取成功且完整的 JSON 到 `work/`。

## 计算活跃日

主口径是统计截止前，MR 第一父链内的 `本月活跃日期数 / 全部活跃日期数`。按原始 `authored_date` 转统计时区，同日多提交只计一天；它不是实际工时，不能改用 `committed_date`、MR 创建或更新时间。保留本分支集成提交，排除合入其他分支的整段历史。

用精确整数门槛 `本月活跃日 × 3 >= 全部活跃日`，不先四舍五入。每个 MR 独立判断后再按任务汇总；同时保留提交条数占比，临界项查看剔除集成提交后的辅助比例，不能以一个合格补修 MR 纳入整个旧需求。

脚本用 Python 3.9+ 标准库，不安装项目依赖。将 `SKILL_DIR` 替换为当前 skill 的实际目录：

```bash
python3 "$SKILL_DIR/scripts/commit_activity.py" \
  --mr work/source-key/mr-detail.json \
  --commits work/source-key/mr-commits.json \
  --month YYYY-MM \
  --timezone Asia/Shanghai \
  --output work/source-key/mr-activity.json
```

`--as-of` 可传带时区的 ISO 时间，或统计时区中的 `YYYY-MM-DD`（包含当天）；默认当前时间。它只限制提交活动统计，不会把当前 MR 或 tag 快照还原到历史时点。

输入 `--mr` 是单个 MR 详情对象，`--commits` 是已经合并所有分页的数组。脚本从该 MR 的 head 沿 `parent_ids[0]` 前进，走出提交集合时停止，输出：

- `first_parent`：主统计口径，含本分支集成提交；
- `non_merge_first_parent`：剔除集成提交后的辅助口径；
- `all_mr_records`：未经第一父链排除的原始口径，只用于对照；
- `eligibility`：`eligible`、`needs_assessment` 或 `no_month_activity`；
- 统计时间、月初/月末、各口径提交数/活跃日数/比例和排除的外部分支提交数量。

脚本缺少 head、原始日期、父节点信息或遇到循环时会失败，不会猜测。提交列表未分页完可能造成链路提前终止，所以必须先确保完整性。`warnings` 不为空时检查时区、异常未来日期或历史截止条件，不能直接照抄输出。

以单 MR 为单位应用门槛后再按需求分组。多 MR 属于同一任务时，正文只认领合格或明确纳入的部分；汇总日期去重，不把不同 MR 的百分比做算术平均。

## 版本 tag 与状态

读取项目版本 tag 列表并核实命名规则，常见正式版本形如 `10.16.1` 或 `v10.16.1`。临时测试标签、任意分支和流水线成功均不能自动证明已上线；用户定义其他版本标签时按其口径处理。

通过以下接口取得代码所在的 tag，并保存作为状态证据：

`projects/{project}/repository/commits/{sha}/refs?type=tag&per_page=100&page=…`

- 已合并任务核查实际 `merge_commit_sha` / `squash_commit_sha`；fast-forward 等场景使用可确认的交付 head。不要仅检查可能在 squash 后消失的原始 head。
- 未合并任务使用当前 head；分支上的旧提交被 tag 包含，不能证明当前全部增量也已上线。
- 若接口不足以确认，可在具有完整对象和最新 tag 的本地仓库使用只读的 `git merge-base --is-ancestor` / `git tag --contains`。浅克隆或缺失对象必须明确处理，不把缺失解释为未发布。
- 不把“日期早于最新 tag”当作“代码被 tag 包含”。任一已确认版本 tag 包含本次交付代码即可使用已上线，不必只看最新一个 tag。
- 用户指定历史截止日时，还须证明该 tag 在截止时已存在；代码作者日期不等于 tag 创建或发布时间。证据不足则单列待核实。

再依次判断：被版本 tag 包含 → 已上线；否则 Draft → 开发中；其余 → 已交付。所有实时证据只在本轮成立，下次运行重新获取。

## 最小审计记录

每个候选保留：来源主机与项目、MR 作者与 IID、目标任务标题、head、活跃日分数、提交条数分数、纳入决定及原因、Draft 标记、状态所用 SHA/tag、会话证据、验证边界。审计记录放在 `work/<source-key>/`，主表不带 MR 链接或 GitLab 状态。
