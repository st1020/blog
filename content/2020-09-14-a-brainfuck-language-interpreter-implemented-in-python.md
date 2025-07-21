+++
title = "Python 实现的 Brainfuck 语言解析器"
date = 2020-09-14T19:58:28+08:00

[taxonomies]
categories = ["Python"]
tags = ["Python", "Programming Languages"]
+++

## BrainFuck

BrainFuck 语言是一种深奥的编程语言 (Esoteric programming language，Esolang)，由 Urban Müller 于 1993 年创造。目的是为了创造一个简单的、最小的、符合图灵完全的编程语言。正如它的名字，BrainFuck 因为对人类极度不友好而广为人知。但是作为一种图灵完备的编程语言，理论上任何其他编程语言能够实现的程序都可以由 BrainFuck 实现。

<!--more-->

BrainFuck 基于一种简单的机器模型，这个机器包括八种指令，一个以字节 (0-255) 为单位、初始全部为零的数组，一个初始时指向该数组中第一个字节的指针，以及用于输入输出的两个字节流。

八种指令用字符表示如下：

| 字符 | 含义                                                              |
| ---- | ----------------------------------------------------------------- |
| `>`  | 指针前进一个字节                                                  |
| `<`  | 指针后退一个字节                                                  |
| `+`  | 指针指向的字节的值加一                                            |
| `-`  | 指针指向的字节的值减一                                            |
| `.`  | 输出指针指向的单元内容 (根据 ASCII 码)                            |
| `,`  | 输入指针指向的单元内容 (根据 ASCII 码)                            |
| `[`  | 如果指针指向的单元值为零，向后跳转到对应的 `]` 指令的次一指令处   |
| `]`  | 如果指针指向的单元值不为零，向前跳转到对应的 `[` 指令的次一指令处 |

注意，在对数组的字节进行加减时有两种特殊的规则：

1.  $0-1=255$
2.  $255+1=0$

并且数组本身向前是无限的 (或者说限制就是这种机器的内存)，但并不能反向延伸，也就是说，初始时，指针只能向前移动而不能向后。

我们可以仅仅根据以上的规则写一些简单的程序：

### 代码实例

#### 目前位置归零

```txt
[-]
```

#### 字符输入输出

```txt
,.
```

#### 小写字符转化为大写

```txt
,----------[----------------------.,----------]
```

#### Hello World\!

```txt
++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.
```

#### 加法器

```txt
>>[-]>[-]<<<        // clear cell #2 and #3
[->>+>+<<<]         // transfer cell #0 to #2 and #3
>
    >>[-<<<+>>>]<<  // transfer cell #3 to #0
    [->+>+<<]       // transfer cell #1 to #2 and #3
    >>[-<<+>>]<<    // transfer cell #3 to #1
<
```

#### 乘法器

```txt
>>[-]>[-]>[-]<<<<       // clear cell #2 and #3 and #4
[->
    [->+>+<<]           // add cell #1 to #2 and #3
    >>
        [-<<+>>]        // move cell #3 back to #1
        >+<             // copy cell #0 to #4
    <<
<]
>>>>[-<<<<+>>>>]<<<<    // move cell #4 back to #0
```

### 代码分析

下面以 Hello World 程序为例分析一下 BrainFuck 程序的运行过程：

```txt
++++++++++              将 0 号字节（第一个字节，以下简称#0）加到 10
[                       开始循环
    >+++++++                #1 加到 7
    >++++++++++             #2 加到 10
    >+++                    #3 加到 3
    >+                      #4 加到 1
    <<<<-                   返回 #0 并减 1
]                       由于此时指针位于 #0，所以当 #0 减至 0 时就退出循环
                        循环共运行 10 次，至此数组的内容为：0/70/100/30/10
>++.                    进入 #1，加 2，此时 #1 为 72，输出 'H'，以下同理
>+.                     输出 'e'
+++++++.                输出 'l'
.                       输出 'l'
+++.                    输出 'o'
>++.                    输出 ' '
<<+++++++++++++++.      输出 'W'
>.                      输出 'o'
+++.                    输出 'r'
------.                 输出 'l'
--------.               输出 'd'
>+.                     输出 '!'
>.                      输出 '\n'
```

## Python 实现

我使用 Python 实现的 Brainfuck 解释器代码如下：

```python
# Python 实现的 Brainfuck 解释器

test = '++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.'
test1 = ',----------[----------------------.,----------]'


def bf_interpreter(bf_code):
    main_list = [0]
    now_id = 0
    now_position = 0
    while now_position < len(bf_code):
        command = bf_code[now_position]
        if command == '<':
            if now_id == 0:
                print_error(1, '内存错误，指针位于 -1')
            else:
                now_id -= 1
        elif command == '>':
            now_id += 1
            if now_id >= len(main_list):
                main_list.append(0)
        elif command == '+':
            main_list[now_id] += 1
            if main_list[now_id] == 256:
                main_list[now_id] = 0
        elif command == '-':
            main_list[now_id] -= 1
            if main_list[now_id] == -1:
                main_list[now_id] = 255
        elif command == '.':
            print(chr(main_list[now_id]), end='')
        elif command == ',':
            while True:
                input_chr = input('请输入：')
                if len(input_chr) == 1:
                    if ord(input_chr) < 128:
                        main_list[now_id] = ord(input_chr)
                        break
                    else:
                        print_error(2, '输入错误，只能输入 ASCII 字符')
                else:
                    print_error(2, '输入错误，只能输入一个字符')
        elif command == '[':
            if main_list[now_id] == 0:
                try:
                    now_position = bf_code.index(']', now_position) - 1
                except ValueError:
                    print_error(3, '代码错误，缺失：]')
        elif command == ']':
            if main_list[now_id] != 0:
                try:
                    now_position = len(bf_code) - bf_code[::-1].index('[', len(bf_code) - now_position - 1) - 1
                except ValueError:
                    print_error(3, '代码错误，缺失 [')
        else:
            print_error(0, '无法解析的字符：' + command)
        now_position += 1
    print(main_list)


def print_error(error_code, msg):
    print(error_code, msg)


if __name__ == '__main__':
    bf_interpreter(test)
```

程序十分简单，主要就是使用一个 `while` 循环来执行 BrainFuck 代码的解析，并使用一个 `list` 来作为进行操作的数组。

至于这个程序以及 Brainfuck 语言到底有什么用处，毕竟不会真的有人会拿它写代码的，实际上，因为 BrainFuck 语言非常容易实现，因此是一种非常方便地证明一种新语言是图灵完备的方法，只要一种语言能够实现一个 BrainFuck 语言解释器，就可以证明这个语言是图灵完备的了。

当然，Brainfuck 并非是唯一一种 Esolang，也不是其中规则最简单或是最奇怪的，其实也不是最让人感到“Brainfuck”的，这世界上总有一群有趣的人设计出各种奇奇怪怪的语言。

## 彩蛋

最后，你想要做一个巧克力酱蛋糕吗？下面是菜谱，不保证口味哦～

```txt
Hello World Cake with Chocolate sauce.

This prints hello world, while being tastier than Hello World Souffle. The main
chef makes a " world!" cake, which he puts in the baking dish. When he gets the
sous chef to make the "Hello" chocolate sauce, it gets put into the baking dish
and then the whole thing is printed when he refrigerates the sauce. When
actually cooking, I'm interpreting the chocolate sauce baking dish to be
separate from the cake one and Liquify to mean either melt or blend depending on
context.

Ingredients.
33 g chocolate chips
100 g butter
54 ml double cream
2 pinches baking powder
114 g sugar
111 ml beaten eggs
119 g flour
32 g cocoa powder
0 g cake mixture

Cooking time: 25 minutes.

Pre-heat oven to 180 degrees Celsius.

Method.
Put chocolate chips into the mixing bowl.
Put butter into the mixing bowl.
Put sugar into the mixing bowl.
Put beaten eggs into the mixing bowl.
Put flour into the mixing bowl.
Put baking powder into the mixing bowl.
Put cocoa  powder into the mixing bowl.
Stir the mixing bowl for 1 minute.
Combine double cream into the mixing bowl.
Stir the mixing bowl for 4 minutes.
Liquify the contents of the mixing bowl.
Pour contents of the mixing bowl into the baking dish.
bake the cake mixture.
Wait until baked.
Serve with chocolate sauce.

chocolate sauce.

Ingredients.
111 g sugar
108 ml hot water
108 ml heated double cream
101 g dark chocolate
72 g milk chocolate

Method.
Clean the mixing bowl.
Put sugar into the mixing bowl.
Put hot water into the mixing bowl.
Put heated double cream into the mixing bowl.
dissolve the sugar.
agitate the sugar until dissolved.
Liquify the dark chocolate.
Put dark chocolate into the mixing bowl.
Liquify the milk chocolate.
Put milk chocolate into the mixing bowl.
Liquify contents of the mixing bowl.
Pour contents of the mixing bowl into the baking dish.
Refrigerate for 1 hour.
```

## 参考

[Brainfuck - 维基百科](https://zh.wikipedia.org/wiki/Brainfuck)

[深奥的编程语言 - 维基百科](https://zh.wikipedia.org/zh-hans/%E6%B7%B1%E5%A5%A5%E7%9A%84%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80)
