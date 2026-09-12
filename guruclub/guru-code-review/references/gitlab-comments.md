# GitLab 评论与定位

仅在报告内容、目标与写入范围明确后读取。`--comment` 本身未选定具体内容；用户已确认本轮发现 ID 或全文时，不再为同一写入重复询问。

默认创建 draft notes，只有明确要求公开发布/提交 review 才执行相应动作。创建 draft 本身也是远程写入，需要评论授权；不能把“只 review”当作授权。

## 定位

写前刷新 MR head/diff_refs，与已审查 SHA 比较；变化则复核受影响发现。使用实际 old_path/new_path 和 base_sha、start_sha、head_sha。

逐行解析 unified diff：hunk 头设置 old/new 起点；上下文行同时递增，两侧新增/删除行仅递增对应侧，文件头与“无末尾换行”标记不算源码行。新增只设 new_line，删除只设 old_line，上下文同时设两者。位置须确实出现在当前 hunk 中。

真实问题在 hunk 外、rename 定位不明确或位置无法核验时，改为不带位置的说明并写清实际路径/行号；不要为了生成行内评论挂到无关的最近一行。

历史上自建实例出现过位置无效但请求成功、评论重复显示的情况，不把该现象当作所有版本的 API 保证。成功状态码不足以证明定位成功，必须回读校验正文与位置。

## 写入

用 UTF-8 JSON 文件与 `--input` 传嵌套对象，不拼接 Markdown 到 shell。示例 payload：

```json
{
  "note": "**[I1]** 已确认的发现正文",
  "position": {
    "base_sha": "<base_sha>",
    "start_sha": "<start_sha>",
    "head_sha": "<head_sha>",
    "position_type": "text",
    "old_path": "<old_path>",
    "new_path": "<new_path>",
    "new_line": 72
  }
}
```

```bash
glab api --hostname "<host>" --method POST \
  "projects/<project>/merge_requests/<IID>/draft_notes" \
  -H "Content-Type: application/json" --input "<本轮 payload.json>"
```

不带位置的 note 省略 position。只发已获授权的具体发现/汇总，不自动附加表扬或另一条汇总消息。

保存返回的 note ID，GET 回读正文、目标 MR 和 position。请求结果不明时先列表核对是否已存在，不盲目重发。部分成功时报告已写 ID 与未写项，避免重复。

提交 review/公开评论前确认该操作获授权。若还有用户其他草稿，不使用会连带发布它们的批量接口；只处理本轮获授权 ID，缺乏相应接口时报告具体限制。创建草稿成功后报告草稿状态和 MR 链接，不声称已经公开发布、approve 或 merge。

接口以当前实例支持的 [GitLab Draft Notes API](https://docs.gitlab.com/api/draft_notes/) 为准；公开讨论位置规则见 [Discussions API](https://docs.gitlab.com/api/discussions/)。
