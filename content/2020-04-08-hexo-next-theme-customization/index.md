+++
title = "Hexo-NexT 主题个性化定制"
date = 2020-04-08T11:22:14+08:00

[taxonomies]
categories = ["Web"]
tags = ["Hexo", "Blog"]
+++

本篇文章主要谈一谈我是如何个性化定制 Hexo 的 NexT 主题的。

Hexo 的主题有许多种，其中最知名的莫过于 NexT 主题了，我也选择了这款主题作为我的博客的默认主题。实际上，我本来是打算使用 Hugo 来搭建博客的，但苦于没有找到喜欢的主题，只好作罢。如果未来找到了足够好的主题，我应该会将博客迁移到 Hugo 上吧。本篇也是作为我折腾 Hexo 的一篇记录。

<!--more-->

{% admonition(type="warning") %}

自 2020 年 7 月 15 日起，本博客已经由 Hexo 迁移到了 Hugo，本文部分内容已经不适用了。

{% end %}

{% admonition(type="note") %}

本文基于 NexT 主题 7.8.0 版本，理论上适用于 NexT 7.0+。

下文中 `网站的配置文件` 指 Hexo 根目录下的 `_config.yml`，`主题的配置文件` 位置取决于你的主题配置情况。

{% end %}

## Hexo 搭建和主题安装

关于 Hexo 搭建和主题安装的教程可以说是数不胜数了，我这里就不做赘述了。我使用了 Github page 来储存发布网页，同时同步到 Zeit.co 上作为镜像，并且将 [st1020.top](https://www.st1020.top/) 域名解析到这两个网址，让 DNS 自动选择线路。许多其他教程还同时部署到了 Coding 来加速国内的访问，我并没有这么做，主要懒得再注册一个账户了，并且实际测试下来网站的访问速度还在可以接受的范围内。如果你想要查看我的博客配置，可以访问我的 [Gtihub](https://github.com/st1020/st1020.github.io/tree/hexo)。

## 安装插件

Hexo 支持很多方便的插件，我安装的主要如下：

- [hexo-cake-moon-menu](https://github.com/jiangtj-lab/hexo-cake-moon-menu)
- [hexo-deployer-git](https://github.com/hexojs/hexo-deployer-git)
- [hexo-generator-feed](https://github.com/hexojs/hexo-generator-feed)
- [hexo-generator-searchdb](https://github.com/hexo-next/hexo-generator-searchdb)
- [hexo-generator-sitemap](https://github.com/hexojs/hexo-generator-sitemap)
- [hexo-related-popular-posts](https://github.com/tea3/hexo-related-popular-posts)
- [hexo-renderer-pandoc](https://github.com/wzpan/hexo-renderer-pandoc)
- [hexo-symbols-count-time](https://github.com/theme-next/hexo-symbols-count-time)

其配置可直接参看 NexT 主题文档和上面的插件链接。

## hexo-cake-moon-menu

[hexo-cake-moon-menu](https://github.com/jiangtj-lab/hexo-cake-moon-menu) 是一款来自 [hexo-theme-inside](https://github.com/ike-c/hexo-theme-inside) 主题的悬浮菜单模块，支持自定义菜单项。我打算为其增加夜间模式和简体/繁体自动切换的功能。由于我之前对 Web 前端开发基本上是一窍不通的，所以下面的过程可能有不恰当的地方，还请各位见谅。

### 配置方法

根据 Github 上的方法，自定义 hexo-cake-moon-menu 需要自己编写 JS 插件脚本进行注入，修改布局文件，再修改 `网站配置文件`，看起来很复杂，但好在 NexT 主题已经提供自定义布局的方法，我们只需要修改 `主题的配置文件` 中的 `custom_file_path:` 配置即可。

而对于 hexo-cake-moon-menu 插件的配置，按照作者的说明是这样的：

```yaml
moon_menu:
  chat:
    icon: fa fa-comments
    func: openGitter
```

其中 `icon` 参数为该项的图标，可以在 [Font Awesome](https://fontawesome.com/icons) 中找到，`func` 则为点击这一项时运行的 JavaScript 函数名。所以我们的大体思路就是：

1.  编写一个 JavaScript 脚本实现相关功能
2.  添加自定义布局，使网页加载对应的脚本
3.  修改配置文件，指向相应的函数

### 添加简体/繁体转换

关于这个功能的实现，网上已经有了相关脚本了，我参考的是这篇教程：

[两步让你的网站支持简体繁体切换](http://qingbo.site/2016/10/11/how-set-Chinese-Simplified-switch-to-Chinese-Traditional/)

其中提供了一个简繁转换的脚本，我在此基础上做了一点修改，功能上应该是相同的，可以点击 [这里](http://st1020.top/hexo-next-theme-customization/tw_cn.js) 下载，如果想要下载原脚本的话可以访问上面的网站。

首先下载上面的脚本，放在 `/source/js/tw_cn.js`。

然后我们需要修改 `主题的配置文件`，找到其中的 `custom_file_path:` 选项，把下面这行反注释：

```yaml
footer: source/_data/footer.swig
```

然后新建 `/source/_data/footer.swig` 文件，写入：

```html
<div class="translate-style">
  繁/简：<a id="translateLink" href="javascript:translatePage();">繁体</a>
</div>
<script type="text/javascript" src="/js/tw_cn.js"></script>
```

这相当于在每个网页的 `footer` 部分都添加了上面两行 HTML 代码，第一行表示创建一个 `<div>`，里面包含两部分，一部分是文字 `繁/简：`，另一部分是一个超链接，`id` 为 `"translateLink"`，点击后会运行 JS 函数 `translatePage()`，第二行就是引入 `/js/tw_cn.js` 脚本。

如果你使用的是原来的 JS 脚本而非我修改的那个的话，还需要按照上面的地址中的教程添加一些配置项，如果是用我修改的那个话就什么都不用做了。

最后，我们需要修改 `网站配置文件`，加入以下代码：

```yaml
moon_menu:
  zh:
    icon: fas fa-atlas
    func: translatePage
```

这样，简繁切换菜单就添加完成了。如果你不想要在页脚显示的话还需要修改一下 JS 脚本，去掉里面关于更改文字的代码。

## 夜间模式

NexT 主题是自带了夜间模式支持的，但是只支持根据系统的夜间模式与否来切换，并不是很方便，于是我打算自己写一个来代替原来的夜间模式，实现根据系统的夜间模式和时间自动切换，同时支持使用 hexo-cake-moon-menu 手动切换。

首先，我们需要知道 NexT 主题自带的夜间模式是怎么实现的，我们可以在 `/theme/next/source/css/_colors.styl` 中找到以下内容：

```css
:root {
  --body-bg-color: $body-bg-color;
  --content-bg-color: $content-bg-color;
  --card-bg-color: $card-bg-color;
  --text-color: $text-color;
  ...;
}

if (hexo-config("darkmode")) {
  @media (prefers-color-scheme: dark) {
    :root {
      --body-bg-color: $body-bg-color-dark;
      --content-bg-color: $content-bg-color-dark;
      --card-bg-color: $card-bg-color-dark;
      --text-color: $text-color-dark;
      ...;
    }

    img {
      opacity: 0.75;

      &:hover {
        opacity: 0.9;
      }
    }
  }
}
```

上面的 CSS 代码使用了 `:root` 选择器 `@media` 查询，当浏览器配置为 `prefers-color-scheme: dark` 时便会设置为夜间模式的配色，并且设置图片透明度增加，不过需要注意的是，我们并不能直接使用上面的代码，因为后面对应的并非颜色，而是变量，会在渲染时替换为颜色，我们可以在 `/theme/next/source/css/_variables/base.styl` 中找到变量对应的颜色，不过手动替换太麻烦了，我选择在 `主题配置文件` 中设置 `darkmode: true`，运行 `hexo g` 生成静态文件，然后在 `/public/css/main.css` 中找到需要的 CSS 代码，得到的代码如下：

```css
:root {
  --body-bg-color: #282828;
  --content-bg-color: #333;
  --card-bg-color: #555;
  --text-color: #ccc;
  --blockquote-color: #bbb;
  --link-color: #ccc;
  --link-hover-color: #eee;
  --brand-color: #ddd;
  --brand-hover-color: #ddd;
  --table-row-odd-bg-color: #282828;
  --table-row-hover-bg-color: #363636;
  --menu-item-bg-color: #555;
  --btn-default-bg: #222;
  --btn-default-color: #ccc;
  --btn-default-border-color: #555;
  --btn-default-hover-bg: #666;
  --btn-default-hover-color: #ccc;
  --btn-default-hover-border-color: #666;
}
img {
  opacity: 0.75;
}
img:hover {
  opacity: 0.9;
}
```

我们把上面的代码保存在 `/source/css/dark.css` 中备用。

下面我们要做的就是让网站在合适的情况下加载 `dark.css`，我参考了 [网站夜间模式的实现](https://qqdie.com/archives/night-mode-of-website.html) 这篇文章，这篇文章是用于动态网站的，不过大同小异，思路都是一致的。

首先，我们要编辑 `主题配置文件`，把下面这行反注释：

```yaml
head: source/_data/head.swig
```

然后新建 `/source/_data/head.swig` 文件，写入：

```html
<link
  href="/css/dark.css"
  rel="alternate stylesheet"
  type="text/css"
  title="dark"
/>
<script type="text/javascript" src="/js/darkmode.js"></script>
```

上面两行表示引入了 `/css/dark.css` 和 `/js/darkmode.js`，注意第一行的 `rel` 属性为 `alternate stylesheet`，表示将 `/css/dark.css` 作为备用 CSS，默认并不启用。还有要注意的是，这两行的内容不能调换，必须先引入 CSS 再引入 JS，因为 JS 是对 CSS 进行操作的，如果先引入 JS 的话，它就没有可操作的对象了。

还要，之所以我们把这两行写入了 `head.swig` 而非像简繁转换一样写入 `footer.swig`，是因为简繁转换可以在页面其他部分加载完后再运行，而夜间模式则应该在页面加载前就运行了，否则会导致页面加载过程中一直是亮色的，页面加载完成后才变为夜间模式。

然后我们就可以开始编写 JS 脚本了。

首先我们来实现手动切换部分。我们可以使用以下代码来启用或禁用 `dark.css`：

```javascript
// 启用夜间模式
document.querySelector('link[title="dark"]').disabled = true;
document.querySelector('link[title="dark"]').disabled = false;
```

```javascript
// 关闭夜间模式
document.querySelector('link[title="dark"]').disabled = false;
```

然后我们可以写一个函数实现切换功能：

```javascript
var night = 0;
function switchDarkMode() {
  if (night == 0) {
    document.querySelector('link[title="dark"]').disabled = true;
    document.querySelector('link[title="dark"]').disabled = false;
    var night = 1;
  } else {
    document.querySelector('link[title="dark"]').disabled = true;
    document.cookie = "dark=0;path=/";
    var night = 0;
  }
}
```

但是上面的函数有一个问题，那就是只能在一个页面生效，当读者刷新了页面或这访问了其他的页面后就又会恢复为亮色模式了。那么有什么办法能够在整个网站中传递信息呢，很简单，那就是 cookie。我们可以通过设置 cookie 来实现对整个网站设置夜间模式，修改后的代码如下：

```javascript
function switchDarkMode() {
  var night =
    document.cookie.replace(
      /(?:(?:^|.*;\s*)dark\s*\=\s*([^;]*).*$)|^.*$/,
      "$1"
    ) || "0";
  if (night == "0") {
    document.querySelector('link[title="dark"]').disabled = true;
    document.querySelector('link[title="dark"]').disabled = false;
    document.cookie = "dark=1;path=/";
  } else {
    document.querySelector('link[title="dark"]').disabled = true;
    document.cookie = "dark=0;path=/";
  }
}
```

函数内的第一行表示读取 cookie 并使用正则表达式取出名称为 `dark` 的 cookie 的值，如果没有设置 cookie 那么就设置 `night` 变量为 `'0'`，之后，在每次运行函数后设置对应的 cookie。

最后我们就可以编辑 `网站配置文件` 给 hexo-cake-moon-menu 添加配置项：

```yaml
moon_menu:
  dark:
    icon: fas fa-adjust
    func: switchDarkMode
```

这样手动切换功能就完成了，下面我们来继续完成自动切换部分。

首先，手动切换的优先级肯定是要高于自动切换的，那么我们就要首先判断是否定义了 cookie，如果定义了就使用定义的，没定义就判断时间和系统情况。注意，由于我们在上面设置 cookie 时没有设置持续时间，cookie 是会在浏览器会话结束后自动清除的。代码如下：

```javascript
if (
  document.cookie.replace(
    /(?:(?:^|.*;\s*)dark\s*\=\s*([^;]*).*$)|^.*$/,
    "$1"
  ) == ""
) {
  // 判断时间和系统情况
} else {
  if (
    document.cookie.replace(
      /(?:(?:^|.*;\s*)dark\s*\=\s*([^;]*).*$)|^.*$/,
      "$1"
    ) == "1"
  ) {
    document.querySelector('link[title="dark"]').disabled = true;
    document.querySelector('link[title="dark"]').disabled = false;
  }
}
```

然后，我们来编写判断时间和系统情况的代码，时间好说，那系统夜间模式开启情况呢？实际上我们并没有办法使用 JS 直接获取到这一信息，但是我们可以使用 CSS 获取后间接传递给 JS。

首先反注释主题配置文件中的 `style: source/_data/styles.styl` 并新建 `/source/_data/styles.styl`，写入：

```css
html {
  content: "";
}
/* Light mode */
@media (prefers-color-scheme: light) {
  html {
    content: "light";
  }
}
/* Dark mode */
@media (prefers-color-scheme: dark) {
  html {
    content: "dark";
  }
}
```

上面的代码会在渲染静态页面时插入到 `/css/main.css` 中，它会使用 `@media` 判断系统的 `prefers-color-scheme` 并设置 html 的 `content` 属性，`content` 属性有一些特殊用法，但这里我们没有用到，可以姑且认为 `content` 属性在这里不会对页面的显示样式产生任何影响，只是起到了传递信息的作用，我们可以使用 JS 读出这一属性并保存为常量，代码如下：

```javascript
const mode = getComputedStyle(document.documentElement).getPropertyValue(
  "content"
);
```

最后完整的 `dark.js` 代码如下：

```javascript
const mode = getComputedStyle(document.documentElement).getPropertyValue(
  "content"
);
if (
  document.cookie.replace(
    /(?:(?:^|.*;\s*)dark\s*\=\s*([^;]*).*$)|^.*$/,
    "$1"
  ) == ""
) {
  if (
    mode == '"dark"' ||
    new Date().getHours() > 22 ||
    new Date().getHours() < 6
  ) {
    document.querySelector('link[title="dark"]').disabled = true;
    document.querySelector('link[title="dark"]').disabled = false;
  }
} else {
  if (
    document.cookie.replace(
      /(?:(?:^|.*;\s*)dark\s*\=\s*([^;]*).*$)|^.*$/,
      "$1"
    ) == "1"
  ) {
    document.querySelector('link[title="dark"]').disabled = true;
    document.querySelector('link[title="dark"]').disabled = false;
  }
}

function switchDarkMode() {
  var night =
    document.cookie.replace(
      /(?:(?:^|.*;\s*)dark\s*\=\s*([^;]*).*$)|^.*$/,
      "$1"
    ) || "0";
  if (night == "0") {
    document.querySelector('link[title="dark"]').disabled = true;
    document.querySelector('link[title="dark"]').disabled = false;
    document.cookie = "dark=1;path=/";
  } else {
    document.querySelector('link[title="dark"]').disabled = true;
    document.cookie = "dark=0;path=/";
  }
}
```

这样夜间模式就完成了！

## 一言

[一言 (hitokoto.cn)](https://hitokoto.cn/) 是一个分享一句话的平台，提供了一个很方便的 API 来进行访问，我设置了在我的网站首页显示一言，你可以在我的网站首页的侧边栏中查看实现效果。

添加一言相对来说比较简单，官方不仅提供了 API 还提供了示例代码，可以访问 [一言开发者中心](https://developer.hitokoto.cn/) 查看详情。但官方的示例只获取了句子内容，我稍微修改了以下，让它也同时获取句子来源。

接下来我们需要自定义侧边栏，和上面一样，还是反注释 `主题配置文件` 中的 `sidebar: source/_data/sidebar.swig` 并新建 `/source/_data/head.swig` 文件。

一言部分我直接使用了和友情链接 (blogroll) 相同的样式，代码如下：

```html
<div class="links-of-blogroll motion-element">
  <div class="links-of-blogroll-title" id="hitotitle">
    <i class="fa fa-paragraph"></i>
    <b>一言</b>
  </div>
  <p id="hitokoto" style="padding: 0; margin: 0;">:D 获取中...</p>
  <p
    id="hitofrom"
    style="font-style: italic; text-align: right; padding: 0; margin: 0;"
  >
    :D 获取中...
  </p>
  <script>
    if (CONFIG.page.isHome) {
      fetch("https://v1.hitokoto.cn")
        .then((response) => response.json())
        .then((data) => {
          const hitokoto = document.getElementById("hitokoto");
          const hitofrom = document.getElementById("hitofrom");
          hitokoto.innerText = data.hitokoto;
          hitofrom.innerText = "——" + data.from;
        })
        .catch(console.error);
    } else {
      document.getElementById("hitokoto").style.display = "none";
      document.getElementById("hitofrom").style.display = "none";
      document.getElementById("hitotitle").style.display = "none";
    }
  </script>
</div>
```

我设置为了仅在博客的首页显示，如果你需要在博客所有页面都显示的话可以将 `<script>` 部分更换为以下代码：

```html
<script>
  fetch("https://v1.hitokoto.cn")
    .then((response) => response.json())
    .then((data) => {
      const hitokoto = document.getElementById("hitokoto");
      const hitofrom = document.getElementById("hitofrom");
      hitokoto.innerText = data.hitokoto;
      hitofrom.innerText = "——" + data.from;
    })
    .catch(console.error);
</script>
```

## 最后

你可能发现我的博客样式几乎就是 NexT 的 Gemini 主题的默认样式，并没有做什么更改。是的，我没有添加华丽的鼠标特效或是 live2D 的二次元看板娘，没有设置好听的背景音乐和特别的背景特效，甚至于连背景图片和字体都没有换。其实这都是因为我非常喜欢简约的风格，我认为博客最重要的是其内容，而主题的作用就是突出内容和帮助呈现内容，如果太过华丽就喧宾夺主了。我一直认为，最好的科技应该让人们察觉不到其存在，好的设计应该让人用起来很舒服，一切都是自然而然的，就像使用自己的四肢一样自然。

其实如果你细心观察的话，这个博客还是有一些自定义配置的，比如上面提到的简繁转换、夜间模式和首页的一言，还有 NexT 提供的网页顶部的阅读进度条、右上角会自动保存也能手动设置的书签、文章标题旁边的页面 Markdown 源码入口、点击图片后弹出的 FancyBox、延迟加载图片和自动缓存接下来的页面，以及由各种插件提供的右下角显示阅读进度百分比的悬浮菜单、侧边栏中的搜索功能、文章标题下面的字数统计和阅读时长、文章底部的 Gitalk 的评论。它们都是些不起眼的小功能，但都确确实实地方便了博客的浏览，这才是我需要的博客个性化配置。
