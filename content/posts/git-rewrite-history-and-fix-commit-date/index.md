---
title: "Git 重写历史和修复提交日期"
date: 2021-08-15T21:19:46+08:00
draft: false
categories: ["Git"]
tags: ["Git"]
---

前几天，我发现之前项目中的一个历史提交的 commit 消息写错了，想要进行修改，记录一下修改的过程。

## 修改最后一次提交

修改最后一次提交很简单，git 已经提供了一个命令进行更改：

```shell
git commit --amend
```

上述命令会打开一个编辑器，可以在编辑器中编辑要修改的 commit 消息，然后退出即可保存。

可惜的是，我并不是这种情况，而是许多个提交之前的历史提交。

## 修改历史提交

假设我们当前的提交记录是这样的：

```text
commit c9837cd063d3591d86505d3ab095744173b863b2 (HEAD -> master)
Author: st1020 <stone_1020@qq.com>
Date:   Sun Aug 15 21:51:39 2021 +0800

    test commit 2

commit 98a8bb09d823c5800f1b9ffbe8e2cb40fc8a456c
Author: st1020 <stone_1020@qq.com>
Date:   Sun Aug 15 21:51:10 2021 +0800

    test commit 1

commit de14f7451ede9600a3172ef99f652d231791b16f
Author: st1020 <stone_1020@qq.com>
Date:   Sun Aug 15 21:50:34 2021 +0800

    Init Commit
```

需要将 `test commit 1` 这条提交消息更改为 `first commit` 。

首先，需要找到要修改的提交的前一个提交，即 `de14f74` ，执行变基：

```shell
git rebase -i de14f74
```

执行上述命令会进入文本编辑器，应该会得到类似下面的信息：

```text
pick 98a8bb0 test commit 1
pick c9837cd test commit 2

# 变基 de14f74..c9837cd 到 de14f74（2 个提交）
#
# 命令:
# p, pick <提交> = 使用提交
# r, reword <提交> = 使用提交，但编辑提交说明
# e, edit <提交> = 使用提交，但停止以便在 shell 中修补提交
# s, squash <提交> = 使用提交，但挤压到前一个提交
# f, fixup [-C | -c] <提交> = 类似于 "squash"，但只保留前一个提交
#                    的提交说明，除非使用了 -C 参数，此情况下则只
#                    保留本提交说明。使用 -c 和 -C 类似，但会打开
#                    编辑器修改提交说明
# x, exec <命令> = 使用 shell 运行命令（此行剩余部分）
# b, break = 在此处停止（使用 'git rebase --continue' 继续变基）
# d, drop <提交> = 删除提交
# l, label <label> = 为当前 HEAD 打上标记
# t, reset <label> = 重置 HEAD 到该标记
# m, merge [-C <commit> | -c <commit>] <label> [# <oneline>]
# .       创建一个合并提交，并使用原始的合并提交说明（如果没有指定
# .       原始提交，使用注释部分的 oneline 作为提交说明）。使用
# .       -c <提交> 可以编辑提交说明。
#
# 可以对这些行重新排序，将从上至下执行。
#
# 如果您在这里删除一行，对应的提交将会丢失。
#
# 然而，如果您删除全部内容，变基操作将会终止。
```

我们现在需要把要修改的那次提交前的 `pick` 更改为 `edit` 或者 `e` ，之后 `:wq` 保存退出：

```text
edit 98a8bb0 test commit 1
pick c9837cd test commit 2
```

会输出以下信息：

```text
停止在 98a8bb0... test commit 1
您现在可以修补这个提交，使用

  git commit --amend

当您对变更感到满意，执行

  git rebase --continue
```

修改完成后，执行 `git commit --amend` 进入编辑器编辑提交消息，或者直接使用 `git commit --amend -m "first commit"` 提交。

之后，只需执行 `git rebase --continue` 即可完成修改。

再次查看 `git log` ：

```text
commit 6118ceb757f15b602eff73db5adccb293a2d6821 (HEAD -> master)
Author: st1020 <stone_1020@qq.com>
Date:   Sun Aug 15 21:51:39 2021 +0800

    test commit 2

commit 3bf6a7f2d1d493e5d7c831f2bb2922796e8ca380
Author: st1020 <stone_1020@qq.com>
Date:   Sun Aug 15 21:51:10 2021 +0800

    first commit

commit de14f7451ede9600a3172ef99f652d231791b16f
Author: st1020 <stone_1020@qq.com>
Date:   Sun Aug 15 21:50:34 2021 +0800

    Init Commit
```

会发现提交消息已经被修改了，并且因为变基，这次修改的提交及其之后的提交的 SHA-1 全都发生了改变。

如果已经将这些提交推送到了远程仓库，那么可以执行 `git push -f` 强制推送。

## 修复提交日期

但是，当我强制推送到了 github 远程仓库后却发现，github 提交记录中被修改的提交后的提交的日期是全都变成了今天，但是 `git log` 中的明明没有问题啊？

经过一番查找，我最终发现，git 的 commit 的日期实际上包含了两个日期，分别是 `AuthorDate` 和 `CommitDate` ，`git log` 中默认显示的是 `AuthorDate` 而 github 的提交记录中显示的则是 `CommitDate` ，上述的变基操作不会改变 `AuthorDate` 但却改变了 `CommitDate` 。

我们可以通过 `git log --pretty=fuller` 命令查看：

```text
commit 6118ceb757f15b602eff73db5adccb293a2d6821 (HEAD -> master)
Author:     st1020 <stone_1020@qq.com>
AuthorDate: Sun Aug 15 21:51:39 2021 +0800
Commit:     st1020 <stone_1020@qq.com>
CommitDate: Sun Aug 15 22:09:37 2021 +0800

    test commit 2

commit 3bf6a7f2d1d493e5d7c831f2bb2922796e8ca380
Author:     st1020 <stone_1020@qq.com>
AuthorDate: Sun Aug 15 21:51:10 2021 +0800
Commit:     st1020 <stone_1020@qq.com>
CommitDate: Sun Aug 15 22:07:22 2021 +0800

    first commit

commit de14f7451ede9600a3172ef99f652d231791b16f
Author:     st1020 <stone_1020@qq.com>
AuthorDate: Sun Aug 15 21:50:34 2021 +0800
Commit:     st1020 <stone_1020@qq.com>
CommitDate: Sun Aug 15 21:50:34 2021 +0800

    Init Commit
```

或者通过 `git log --format=format:"%h %ai %ci"` 方便地比较 `AuthorDate` 和 `CommitDate` 。

```text
6118ceb 2021-08-15 21:51:39 +0800 2021-08-15 22:09:37 +0800
3bf6a7f 2021-08-15 21:51:10 +0800 2021-08-15 22:07:22 +0800
de14f74 2021-08-15 21:50:34 +0800 2021-08-15 21:50:34 +0800
```

**第一种方法**是，我们可以在前面的提交步骤中，将命令修改为：

```shell
GIT_COMMITTER_DATE="2021-08-15 21:51:10 +0800" git commit --amend -m "first commit"
```

这里的 `GIT_COMMITTER_DATE` 要设置成这次提交的 `AuthorDate` 。

但是即使这样做，这次提交之后的提交的日期也会变化，得到的 `git log --format=format:"%h %ai %ci"` 会类似这样：

```text
ff6edfd 2021-08-15 21:51:39 +0800 2021-08-15 22:31:06 +0800
699345c 2021-08-15 21:51:10 +0800 2021-08-15 21:51:10 +0800
de14f74 2021-08-15 21:50:34 +0800 2021-08-15 21:50:34 +0800
```

我们需要类似之前修改提交消息的方法，通过变基再去修改它的后一条消息的提交时间，提交时的命令使用：

```shell
GIT_COMMITTER_DATE="2021-08-15 21:51:39 +0800" git commit --amend --no-edit
```

但如果要修改的消息的提交后有很多的提交，就需要反复执行上面的操作，非常麻烦，所以显然不是什么好办法。

**第二种方法**就简单了很多，我们可以直接执行下面的命令即可将所有的提交的 `CommitDate` 修改为 `AuthorDate` 。虽然 `filter-branch` 指令因为有很多的坑已经不推荐使用了，但像我们这种简单的操作还是没问题的。

```shell
git filter-branch --env-filter 'export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"'
```

## 参考资料

- [Git - 重写历史](https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E9%87%8D%E5%86%99%E5%8E%86%E5%8F%B2)
- [Force GIT_COMMITTER_DATE = GIT_AUTHOR_DATE](https://gist.github.com/bfoz/568898)
- [Git - git-filter-branch Documentation](https://git-scm.com/docs/git-filter-branch)
- [Git - pretty-formats Documentation](https://git-scm.com/docs/pretty-formats)
- [Git - git-commit Documentation - COMMIT INFORMATION](https://git-scm.com/docs/git-commit#_commit_information)
