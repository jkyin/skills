# GitLab(`glab`)

gitlab.com 和自建实例都一样能用。先确认 host:

```bash
glab auth status
```

只要对你的实例认证通过,下面所有东西都原样可用 —— `glab` 会从 git remote 读取 host。

## 确定目标

```bash
glab mr view <N>
```

不带参数时解析当前分支对应的 MR。列出候选:

```bash
glab mr list --state opened
```

需要解析结构化元信息时:

```bash
glab api projects/:fullpath/merge_requests/<N>
```

相关字段:`state`(`opened`/`closed`/`merged`/`locked`)、`draft`、`title`、`author.name`、
`source_branch`、`target_branch`、`diff_refs`、`sha`。

**`target_branch` 就是 base,直接用,不要再去猜。** MR 自己声明了要合进哪个分支(`develop`、
`master`、还是别的),这是权威信息,`references/local.md` 里那套 base 推断启发式在 MR 模式下
完全不需要。

## diff 和文件

```bash
glab mr diff <N>
glab api projects/:fullpath/merge_requests/<N>/changes --jq '.changes[].new_path'
```

然后用 Read 工具完整读取每个路径(SKILL.md 第 3 步)。

## 发布:draft notes

用 `draft_notes` 接口:在用户点击 **Submit review** 之前,这些 note 是不可见的,整批评论作为一次
review 落地,而不是 N 条通知一条条往外漏。优先用它。只有在用户明确要求评论立即公开时,
才用 `notes`/`discussions`。

### 1. 拿到 diff refs

每条带位置的 note 都需要这三个 SHA:

```bash
glab api projects/:fullpath/merge_requests/<N> --jq '.diff_refs | .base_sha, .head_sha, .start_sha'
```

### 2. 逐条发行内 draft note

```bash
python3 - <<'PYEOF'
import json
payload = {
    "note": "**[C1]** <发现内容,用用户的语言>",
    "position": {
        "base_sha":  "<base_sha>",
        "head_sha":  "<head_sha>",
        "start_sha": "<start_sha>",
        "new_path":  "src/auth.ts",
        "old_path":  "src/auth.ts",
        "position_type": "text",
        "new_line": 72
    }
}
open("/tmp/mr_c1.json", "w").write(json.dumps(payload))
PYEOF

glab api projects/:fullpath/merge_requests/<N>/draft_notes \
  --method POST --input /tmp/mr_c1.json -H "Content-Type: application/json"
```

**这里 `-F` 用不了。** `glab api -F 'position[base_sha]=...'` 会把嵌套对象当成扁平的表单字段发出去;
GitLab 直接忽略它们,于是这条 note 会静默地变成一条不带位置的普通评论,而不是行内评论。
永远构造 JSON 文件然后用 `--input`。

### 3. 汇总作为不带位置的 draft note 发出

同一个接口,只给 `note`,不给 `position` 字段。

### 4. 不要提交

把 note 留在草稿状态,并告诉用户:

> 草稿评论已创建。打开 MR 检查一遍,按需编辑或删除,然后点击 "Submit review"。

## hunk 规则(这条最容易踩)

行必须在 diff 里可见。如果不在,GitLab **不会拒绝**请求 —— 它会接受,返回 `line_code: null`,
然后**把这条评论在该文件的每一个 hunk 边界上重复渲染一遍**。看起来像是你的工具有 bug,而且手工
清理起来非常烦人。

所以每次发之前都要验证。解析目标文件的 hunk 头:

```
@@ -old_start,old_count +new_start,new_count @@
```

确认存在某个 hunk 满足 `new_start <= new_line <= new_start + new_count - 1`。如果不满足:
改指到最近的一个 hunk 内的行,并在正文里点明真实的行号("在第 190 行:……"),或者把这条发现
挪进汇总 note。

该设哪个行号字段:

| diff 行 | 设置 |
|---|---|
| 新增(绿色) | 只设 `new_line` |
| 删除(红色) | 只设 `old_line` |
| 未改动的上下文行 | `new_line` 和 `old_line` 都设 |

对**重命名的文件**(`old_path` ≠ `new_path`),位置解析不可靠 —— 仔细核对 hunk 范围,拿不准就用
汇总 note。

## 兜底:普通评论

```bash
glab mr note <N> --message "$(cat /tmp/summary.md)"
```

## 自建实例说明

如果实例要求 SSO/SAML,用 personal access token(`api` scope)走
`glab auth login --hostname <host>` 通常是阻力最小的路径 —— 内部实例上浏览器 OAuth 流程经常是关掉的。
