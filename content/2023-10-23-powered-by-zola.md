+++
title = "Powered by Zola"
date = 2023-10-23T20:23:45+08:00

[taxonomies]
categories = ["杂谈"]
tags = ["Blog"]
+++

在三年前这个博客从 Hexo 迁移到 Hugo 之后，这一次又从 Hugo 迁移到了 Zola。

我之前使用的 Hugo 主题 [LoveIt](https://github.com/dillonzq/LoveIt) 已经停止维护好久了 (所以爱是会消失的对吗)，本来我想 fork 一份自己维护一下的，取名为 [LikeIt](https://github.com/st1020/LikeIt)，意为比“Love”少一点，主要就是删除了一些我用不到组件，然后修了一些 Bug(虽然好像引入了一些新的 Bug)。

但在维护的过程中，我是在受不了。Go template 的阴间语法搭配上 Hugo 丰富而复杂的各种特性，再加上 LoveIt 主题本身的复杂性和我本身对 CSS 也不是很熟练，让维护工作十分不顺利。

尤其要点名批评 Go template 这个混沌邪恶的产物，它的语法实在是非常的反直觉了，感觉就像函数式语言和命令式语言的缝合。

除此之外，对于 Hugo 我也有一些抱怨，随着不断的发展，它已经太重了，这使得它的学习成本比较高，具体可以看一下 [Migrating my blog to Zola](https://mrkaran.dev/posts/migrating-to-zola/) 这篇博客中他迁移的原因。

所以，我觉得是时候换一个新的 SSG 了，对于新的 SSG 我有如下要求：

1.  拥有一个不那么阴间的模版语法。
2.  使用非脚本语言编写。往往脚本语言编写的 SSG 的速度都不是很理想，并且我也不是很喜欢生成博客时还需要装一个 Node 环境或者 Python 的虚拟环境，这也是多余的开销，我希望新的 SSG 最好零依赖，只有一个二进制文件。
3.  干净简单，约定优于配置，大多数功能都是可选的。
4.  满足上述条件的前提下，有尽可能多的使用人数和持续良好的维护。

综合上述条件，我最终找到了 [Zola](https://www.getzola.org/)。它是用 Rust 语言编写的，因此可以做到零依赖，并且性能比宣称“The world’s fastest framework for building websites”的 Hugo 还要好。它的模版引擎使用的是同一个作者开发 Tera，这是一个语法高度类似 Jinja 的模块引擎，也是 Rust 生态中最热门的模版引擎之一。更重要的它很简单清晰，Page、Section 的结构非常简单易懂。

但是，由于用户基数还不是很大，我并没有找到心仪的主题，也是防止新的主题再次停止维护，Zola 本身编写一个主题也十分简单，这次，我选择直接编写一个主题。

可我对自己的 UI 设计能力并没有自信，所以最终还是选择移植一个 Hugo 主题，并在它的基础上修改。

最终，我选择了 [hugo-paper](https://github.com/nanxiaobei/hugo-paper)，它是 Hugo 最热门的主题 [hugo-PaperMod](https://github.com/adityatelange/hugo-PaperMod) 的前身，足够简洁美观，代码量也非常少，并且使用了 TailwindCSS。

我把 hugo-paper 移植到了 Zola 之后还做了不少的修改，比如增加了目录、项目页面、存档页面、分类页面、Mermaid 支持、Admonition shortcode 等，还做了不少样式的调整，多亏了 TailwindCSS 和 Zola，修改起来非常容易。

我将新的主题命名为 [Kita](https://github.com/st1020/kita)，这个玩了一个三语梗，Zola 在中文中读起来就像“走啦”，而 Kita 是日语“来た”(来了) 的罗马音，同时也致敬了孤独摇滚里的“归去来兮女士”喜多郁代 (Kita Ikuyo) 的名字。

这次应该是最后一次迁移了 (如果 Zola 本身不停止维护的话，虽然即使停止维护功能也足够稳定和完整了)，有了自己的主题也方便之后随时修改啦。
