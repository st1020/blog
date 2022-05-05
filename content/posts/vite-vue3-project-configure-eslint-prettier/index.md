---
title: "Vite Vue3 项目配置 Eslint Prettier"
date: 2022-03-12T21:11:30+08:00
draft: false
categories: ["前端"]
tags: ["Vue", "Vite"]
---

简单记录一下为 Vite+Vue3+TypeScript 项目配置 ESLint 和 Prettier 工具。

简单介绍一下 Vite，Vite 是一种新型前端构建工具，作为 webpack 的替代者，有着极快的构建和热更新速度。

而 ESLint 和 Prettier 则是分别用于代码检查和代码格式化的工具。

以下均使用 pnpm 作为包管理器，其他包管理器如 npm 或 yarn 类似。

## 创建项目

首先使用 Vite 创建项目并初始化：

```shell
pnpm create vite my-vue-app -- --template vue-ts
cd my-vue-app
pnpm install
```

## 安装所需依赖

```shell
pnpm add -D eslint eslint-plugin-vue prettier eslint-plugin-prettier @vue/eslint-config-prettier @vue/eslint-config-typescript
```

## 创建配置文件

.eslintrc.js

```javascript
module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-essential',
    '@vue/eslint-config-typescript/recommended',
    '@vue/eslint-config-prettier'
  ],
  globals: {
    defineProps: 'readonly'
  }
}

```

.prettierrc

```yaml
semi: false
singleQuote: true
printWidth: 80
trailingComma: 'none'
arrowParens: 'avoid'
```

## 配置 VSCode 插件

如果配合 VSCode 使用的话，需要安装 [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) 和 [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) 这两个插件。对于 Vue 可以尝试一下最新的 [Vue Language Features (Volar)](https://marketplace.visualstudio.com/items?itemName=johnsoncodehk.volar) 插件。
