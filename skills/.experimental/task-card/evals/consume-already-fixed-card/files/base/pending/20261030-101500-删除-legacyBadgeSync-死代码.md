# 删除 legacyBadgeSync 死代码

1. 定位：当前仓库根目录，从 develop 切分支。
2. 问题：`FeedViewController.legacyBadgeSync()` 只在 `if false` 分支内被调用，属于死代码。
3. 证据：
   - 已确认：commit `a1b2c3d` 上 `grep -rn "legacyBadgeSync" Sources/` 共 3 处——
     `Sources/Feed/FeedViewController.swift:7`（`if false` 内唯一调用）/ `:11`（注释）/ `:12`（定义）。
   - 未验证：是否存在通知名 `LegacyBadgeSync` 的外部监听者。
4. 任务：
   1. 先核实目标分支上该问题是否仍存在（当前发现基于 commit `a1b2c3d`）；
      若已被其它改动修掉：只回报结论，不要动代码；若仍在：继续下列步骤。
   2. 删除 `legacyBadgeSync()` 定义、`if false` 调用块及相关注释。
   3. 搜索 `LegacyBadgeSync` 通知名，确认没有监听者。
   完成判定：`grep -rn "legacyBadgeSync\|LegacyBadgeSync" Sources/` 0 命中，且工程可编译。
5. 约束：只删除死代码，不顺带重构 Feed 角标逻辑。
6. 来源：分支 feat/badge-center，commit `a1b2c3d`，当时在接入 BadgeCenter。
