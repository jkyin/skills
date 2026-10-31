#!/usr/bin/env bash
# 在运行目录建出评测用 git 仓库：files/base 为初始提交。
set -eu
src="$(dirname "$0")/files"
git init -q -b develop
git config user.name eval
git config user.email eval@example.com
cp -R "$src/base/." .
git add -A
git commit -qm "chore: 初始化"
