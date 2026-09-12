# GitLab 描述写入

仅在需要创建或更新 MR 时读取。使用已认证的 `glab` CLI/API，host 来自本轮 MR URL 或已核实的 remote，项目路径 URL 编码；不硬编码 `ios/guruclub` 到其他项目。

先保存完整 UTF-8 `mr_body.md`，再生成 JSON。路径通过 argv 传给脚本，不将 Markdown 拼入 shell 命令；内容含中文、换行、反引号或 `$()` 时也应原样保存。

```bash
python3 - "<mr_body.md>" "<mr_desc.json>" <<'PYJSON'
import json, pathlib, sys
body = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
pathlib.Path(sys.argv[2]).write_text(json.dumps({'description': body}, ensure_ascii=False), encoding='utf-8')
PYJSON

glab api --hostname "<host>" --method PUT \
  "projects/<已编码项目>/merge_requests/<IID>" \
  -H "Content-Type: application/json" --input "<mr_desc.json>"
```

只将用户要求修改的字段放入 payload；标题也获授权时一并写入。新建 MR 使用当前 `glab` 帮助或官方 API 支持的创建参数，不把更新命令当作创建命令。

写前确认目标与当前状态，写后 GET 回读完整内容。请求结果不明时先 GET 核验，避免盲目重试。写入权限仅覆盖本轮 MR 描述/标题，不包含合并、批准或评论发布。

## 故障处理

只在发生问题时检查 `glab` 的真实路径、包装器、host 认证状态与准确错误。历史上有 op 包装器等待交互、仓库凭据不具 API 权限的情况；它们是排查线索，不是对当前环境的断言。

允许在本轮授权内修正明确的参数、host 或执行上下文问题；需要登录、额外 API 权限或用户交互时报告具体缺口并保留文案。不读取、打印或转用 Git credential、浏览器 cookie/token 绕过认证，也不改用 GitLab 浏览器自动化。
