# 本地模式(没有托管平台,或平台不受支持)

当 `glab` 没有对该 remote 认证、remote 是 GitHub/Gitea/裸仓库、用户离线、或者用户只是想在提 MR
之前先审一遍时,用这个模式。

SKILL.md 第 3–8 步在这里完全一样。只有目标解析和第 9 步(发布)不同。

## 确定 base

整个审查的质量取决于这一步做对没有 —— diff 的好坏完全取决于 base。**不要猜。**

按顺序尝试,命中即停:

```bash
# 1. 显式的上游跟踪分支 —— 最可信
git rev-parse --abbrev-ref --symbolic-full-name @{u}

# 2. 仓库自己声明的默认分支
git symbolic-ref refs/remotes/origin/HEAD --short   # → origin/develop 或 origin/main
```

3. **规范文件里声明的 base**:第 4 步读的 `CLAUDE.md` / `AGENTS.md` 里如果写了主干分支是哪个
   (比如"本仓库主干为 `develop`"),以它为准。这是团队的明文声明,优先级高于任何猜测。

4. **都没有 → 用 merge-base 距离来定,而不是按名字优先级挑。** 枚举实际存在的候选分支,
   算每个候选到 HEAD 的距离,**取距离最小的那个** —— 你从哪个分支切出来的,跟它的 merge-base
   就最近:

```bash
for b in develop main master trunk; do
  git rev-parse --verify --quiet origin/$b >/dev/null || continue
  echo "$(git rev-list --count $(git merge-base origin/$b HEAD)..HEAD) origin/$b"
done | sort -n
```

   这条对 git-flow 仓库尤其重要:`master` 和 `develop` **会同时存在**。按名字优先级挑会选中
   `master`(上个 release 点),于是把别人合进 `develop` 的所有改动都算成你的,产出一份很长、
   很自信、且完全审错了对象的报告。而 merge-base 距离是**证据**:从 `develop` 切出来的 feature
   分支,到 `develop` 的距离就是你自己的几个 commit,到 `master` 的距离是整个发版周期。

5. **前几名距离接近、分不出来 → 停下来问用户。** 猜错 base 的代价远高于问一句。

拿到 base 之后:

```bash
BASE=$(git merge-base origin/<确定的分支> HEAD)
git diff $BASE...HEAD
git diff --name-only $BASE...HEAD
```

用**三个点**(`$BASE...HEAD`)。两个点会把你切分支之后 base 分支上新落的改动也包含进来,那些不是
你的改动,审它们纯属浪费所有人的时间。

**开始之前用一行跟用户确认 base,并说明是怎么定的** —— "将对照 `origin/develop`(来自
origin/HEAD;merge-base `a1b2c3d`)审查 12 个文件。"说明来源是为了让用户一眼看出你是不是搞错了;
悄无声息地对着错误的 base 做审查,只会产出一份自信满满但审错了对象的报告。

> 如果第 2 步返回空,说明本地没记录远端默认分支。这不是 skill 的问题,跑一次
> `git remote set-head origin -a` 就能一劳永逸地修好,之后第 2 步永远命中,后面的启发式都不会
> 再被用到。值得提醒用户。


## 其他目标

按需调整 —— skill 的其余部分不关心 diff 从哪来:

```bash
git diff                          # 未提交的改动
git diff --staged                 # 只看已暂存的
git show <sha>                    # 单个 commit
git diff <ref1>..<ref2>           # 任意两个 ref
```

如果用户在工作区不干净的情况下要求审查"我的改动",问清楚指的是哪个:已提交的分支工作,还是未提交的
改动。不要把两者混在一起 —— 它们是两次不同的审查。

## 历史 agent(A5)

在这里完全可用,不需要任何托管平台:

```bash
git log --oneline $BASE..HEAD
git log -p --follow <file>
git blame -L <start>,<end> <file>
```

## 第 9 步:发布

没有地方可发。跳过第 9 步,也不要问 —— 只在用户看起来想要下一步时,提供这几个选项:

- 把报告写到文件(`review-<branch>.md`),方便之后粘到托管平台上
- 直接动手处理这些发现(现在就修掉 CRITICAL 的)
- 什么都不做 —— 终端里那份报告就是交付物

**不要建议用户去装 `glab`**,除非他们自己提起想发评论。本地模式对很多人来说就是产品的全部,
把它当成一种降级状态来对待,只是噪音。
