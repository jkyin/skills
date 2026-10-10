# 范围内的 Swift 格式化

只在准备/执行提交且本轮含 Swift 变更时读取。格式化与功能改动保持独立提交。

1. 先确认授权的 Swift 文件/hunk、项目配置和实际工具版本。优先用仓库提供的检查模式，检查失败才准备格式修复；纯文档任务不运行格式化。
2. 按明确文件列表运行，不把 `.` 作为默认目标，不遍历 Pods、生成代码、子模块或未纳入的文件。同文件混有无关改动时，先隔离补丁或暂不改写该文件，不能整文件格式化后全部纳入。
3. 对格式化结果检查 diff，确保每一处都是本轮目标的格式调整。只有已经授权格式修复的范围才写入；发现超出范围的历史格式问题保持不变。
4. 格式化单独提交为 `style: 格式化代码`。用户只批准一个功能提交时，不自动追加第二个提交；先准备格式补丁和拆分方案。用户已批准功能与格式两个范围则直接按拆分执行，无需再次确认。
5. 若先提交功能再执行格式化，将“后续格式化及独立提交”纳入此前可审阅方案；不能在完成用户唯一授权的提交后才自动改写工作区。无需更改时，不创建空 style 提交。

## 项目命令

先读取该项目的格式化配置与文档，使用当前有效命令。GuruClub 主项目历史上使用 `Pods/SwiftFormat/CommandLineTool/swiftformat`，Pod 模块使用 PATH 中的 `swiftformat`；先核实可执行文件和版本，不因主项目工具缺失擅自升级或替换版本。

项目没有新配置覆盖时，以下为已有 GuruClub 参数参考；以明确的 Swift 文件替换路径，每个路径独立引用，不按空格拆分文件列表：

```bash
"<已核实的 swiftformat 路径>" "<本轮文件1.swift>" "<本轮文件2.swift>" \
  --disable redundantSelf,blankLinesAroundMark,blankLinesAtStartOfScope,wrapMultilineStatementBraces,initCoderUnavailable,enumNamespaces,typeSugar,redundantParens,wrapPropertyBodies,docComments,wrapFunctionBodies,redundantProperty,redundantMemberwiseInit,simplifyGenericConstraints \
  --swiftversion 5.5 --stripunusedargs closure-only --nospaceoperators '...,..<' \
  --wraparguments before-first --wrapcollections before-first
```

检查模式与参数以当前工具帮助为准。不运行全仓格式化命令来处理局部任务，不自动安装依赖或执行本地 fastlane。
