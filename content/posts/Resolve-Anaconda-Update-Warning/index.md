---
title: "解决 Anaconda 使用清华源后更新时的警告"
date: 2020-10-30T22:26:12+08:00
draft: false
categories: ["categorie"]
tags: ["tag1", "tag2"]
---

Anaconda 是一个免费开源的 Python 和 R 语言的发行版本，用于计算科学（数据科学、机器学习、大数据处理和预测分析），Anaconda 致力于简化包管理和部署。

使用 Anaconda 可以省去很多配置 Python 环境和依赖和时间，并且 Anaconda 提供了类似 Virtualenv 的方便的虚拟环境。不过，由于国内网络问题，使用 Anaconda 时会遇到很多问题，所以，我们需要更换 Anaconda 的软件源为国内源。由于 Anaconda 是 Anaconda, Inc. 的商标，任何未经授权的公开镜像都是不允许的，而国内得到授权的镜像站并不多，其中最为常用的是清华大学的TUNA镜像源。

但是，当我安装好 Anaconda 并按照 [清华大学开源软件镜像站](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/) 的说明设置好 `.condarc` 文件后，运行 `conda update --all` 时却出现了以下警告：

> Warning: >10 possible package resolutions (only showing differing packages):
>
> ...

我试图重新安装 Anaconda ，但是问题并没有解决。最后，我在网络上搜索到了这篇博文 [Anaconda 使用清华源并解决警告](https://yuweihung.com/post/anaconda-channel/) ，解决方案如下：

修改 `.condarc` 如下：

```
channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/pro
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
show_channel_urls: true
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```

这样即可成功解决更新时的警告。