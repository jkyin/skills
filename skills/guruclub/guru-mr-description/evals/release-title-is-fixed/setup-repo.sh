#!/usr/bin/env bash
# 在运行目录建出评测用 git 仓库：files/base 为初始提交，再在 release/10.18.0 分支提交 files/change。
set -eu
src="$(dirname "$0")/files"
git init -q -b develop
git config user.name eval
git config user.email eval@example.com
cp -R "$src/base/." .
git add -A
git commit -qm "chore: 初始化"
git switch -q -c release/10.18.0
cp -R "$src/change/." .
git add -A
git commit -qm "chore: 更新版本号至 10.18.0"
