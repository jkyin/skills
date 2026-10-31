#!/usr/bin/env bash
# 在运行目录建出评测用 git 仓库：files/base 为初始提交，再在 fix/empty-feed-copy 分支提交 files/change。
set -eu
src="$(dirname "$0")/files"
git init -q -b develop
git config user.name eval
git config user.email eval@example.com
cp -R "$src/base/." .
git add -A
git commit -qm "chore: 初始化"
git switch -q -c fix/empty-feed-copy
cp -R "$src/change/." .
git add -A
git commit -qm "fix: 修正空列表提示文案"
