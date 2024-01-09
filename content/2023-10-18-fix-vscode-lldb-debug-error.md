+++
title = "修复 MacOS 升级后 VSCode LLDB 调试错误"
date = 2023-10-18T20:26:56+08:00

[taxonomies]
categories = ["VSCode"]
tags = ["VSCode", "Mac"]
+++

最近升级了 MacOS 14 之后，发现无法使用 VSCode 调试 Rust 程序了，点击调试后程序直接闪退。调试控制台输出 `Process exited with code -1.`。

初步判断是 [CodeLLDB](https://github.com/vadimcn/codelldb) 拓展的问题，并在它的 GitHub 仓库里找到了解决方案。

<https://github.com/vadimcn/codelldb/discussions/456>

<https://github.com/vadimcn/codelldb/issues/999>

看起来是一个老问题了，从 MacOS 12 开始就一直存在，修复的方法也很简单，只需要删除拓展目录下的 `vadimcn.vscode-lldb-1.x.x/lldb/bindebugserver` 即可，删除 `bindebugserver` 后拓展会自动使用系统提供的 `bindebugserver`。

根据作者的说法，CodeLLDB 捆绑的 debugserver 来自 XCode 10，但最新的 XCode 已经更新到 15 了，应该是新版本 MacOS 和老版本 debugserver 存在兼容性问题。
