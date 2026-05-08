+++
title = "简单但强大的 Pratt Parsing【译】"
authors = ["Alex Kladov"]

[taxonomies]
categories = ["Programming Languages"]
tags = ["Translated", "Programming Languages", "Rust"]
+++

**原文：<https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html>**

欢迎阅读我关于 Pratt 解析的文章——语法分析的 monad 教程。关于 Pratt 解析文章数量如此之多，以至于存在一个[调查帖子](https://www.oilshell.org/blog/2017/03/31.html) :)

这篇文章的目标是：

- 提出所谓的左递归（left-recursion）问题被夸大了。
- 抱怨 BNF 不足以表示中缀表达式。
- 提供仅包含核心且不引入 DSL-y 抽象的 Pratt 解析算法的描述和实现。
- 希望这是最后一次让自己理解该算法。我曾经[实现过](https://github.com/rust-analyzer/rust-analyzer/blob/c388130f5ffbcbe7d3131213a24d12d02f769b87/crates/ra_parser/src/grammar/expressions.rs#L280-L281)一个生产级的 Pratt 解析器，但我不再理解该代码:-)

这篇文章假设你对解析技术有一定的了解，例如，本文没有解释什么是上下文无关语法（context free grammar）。

## 介绍

解析是编译器将 Token *序列*转换为*树*表示的过程：

```txt
                            Add
                 Parser     / \
 "1 + 2 * 3"    ------->   1  Mul
                              / \
                             2   3
```

完成这项任务的方法有很多，大致可以分为两类：

- 使用 DSL 指定语言的抽象语法
- 手写解析器

Pratt 解析是手写解析最常用的技术之一。

## BNF

语法分析理论的巅峰是发现了上下文无关语法符号（通常使用 BNF 具体语法）用于将线性结构解码为树：

```txt
Item ::=
    StructItem
  | EnumItem
  | ...

StructItem ::=
    'struct' Name '{' FieldList '}'

...
```

我记得我曾经很喜欢这个想法，尤其是它与自然语言句法结构的相似性。然而，一旦我们开始描述表达式，我的乐观很快就消失了。自然表达式语法确实让人们了解表达式是什么。

```txt
Expr ::=
    Expr '+' Expr
  | Expr '*' Expr
  | '(' Expr ')'
  | 'number'
```

虽然这个语法看起来很棒，但实际上它是模糊且不严密的，需要重写才能用于自动解析器生成。具体来说，我们需要指定运算符的优先级（precedence）和结合性（associativity）。确定的语法如下所示：

```txt
Expr ::=
    Factor
  | Expr '+' Factor
Factor ::=
    Atom
  | Factor '*' Atom
Atom ::=
    'number'
  | '(' Expr ')'
```

对我来说，表达式的“形状”在这个新的表述中完全消失了。此外，我花了三四门正式的语言*课程*才能够自己可靠地创建这种语法。

这就是我喜欢 Pratt 解析的原因——它是递归下降解析（recursive descent parsing）算法的增强，它使用优先级和结合性这种自然的术语来解析表达式，而不是语法混淆技术。

## 递归下降和左递归

手写解析器的最简单技术是递归下降法，它将语法建模为一组相互递归的函数。例如，上面的 item 语法片段如下所示：

```rust
fn item(p: &mut Parser) {
    match p.peek() {
        STRUCT_KEYWORD => struct_item(p),
        ENUM_KEYWORD   => enum_item(p),
        ...
    }
}

fn struct_item(p: &mut Parser) {
    p.expect(STRUCT_KEYWORD);
    name(p);
    p.expect(L_CURLY);
    field_list(p);
    p.expect(R_CURLY);
}

...
```

传统上，教科书指出左递归语法是这种方法的致命弱点，并利用这一缺点来引出更先进的 LR 解析技术。有问题的语法示例如下所示：

```txt
Sum ::=
    Sum '+' Int
  | Int
```

确实，如果我们简单地编写 `sum` 函数，它不会生效：

```rust
fn sum(p: &mut Parser) {
    // 尝试第一种情况
    sum(p); // ➊
    p.expect(PLUS);
    int(p);

    // 如果失败了，尝试其他情况
    ...
}
```

1.  这时我们立即进入了死循序并且发生栈溢出

该问题的理论上解决方法包括重写语法以消除左递归。然而在实践中，对于手写的解析器，解决方案要简单得多——摆脱纯粹的*递归*范式并使用循环：

## Pratt 解析的大体结构

仅使用循环不足以解析中缀表达式。因此，Pratt 解析*同时*使用循环和递归：

```rust
fn parse_expr() {
    ...
    loop {
        ...
        parse_expr()
        ...
    }
}
```

它不仅能让你的思维进入莫比乌斯环形状的仓鼠轮，还能处理结合性和优先级！

## 从优先级（Precedence）到绑定力（Binding Power）

我必须承认：我对“高优先级”和“低优先级”感到困惑。在 `a + b * c` 中，加法的优先级较低，但它位于解析树的顶部......

因此，我发现绑定力的思考方式更加直观。

```txt
expr:   A       +       B       *       C
power:      3       3       5       5
```

`*` 绑定力更强，它能更有力地将 `B` 和 `C` 结合在一起，因此表达式被解析为 `A + (B * C)`。

那么结合性又是什么呢？在 `A + B + C` 中，所有运算符似乎都具有相同的绑定力，并且不清楚首先折叠哪个 `+` 。但如果我们让它稍微不对称的话，这也可以用绑定力来建模：

```txt
expr:      A       +       B       +       C
power:  0      3      3.1      3      3.1     0
```

在这里，我们稍微增加了 `+` 右侧的绑定力，以便它更紧密地结合右操作数。我们还在两端添加了零，因为两侧没有要绑定的运算符。在这里，第一个（并且只有第一个）`+` 比相邻运算符的更紧密地结合其两个操作数，因此我们可以折叠它：

> 译注：观察 `A` 两侧，3 > 0，其被第一个 `+` 吸引，观察 `B` 两侧，3.1 > 3，其也被第一个 `+` 吸引。

```txt
expr:     (A + B)     +     C
power:  0          3    3.1    0
```

现在我们可以折叠第二个加号并得到 `(A + B) + C` 。或者，就语法树而言，第二个 `+` 确实比起左侧操作数更喜欢右侧操作数，因此它急于结合 C。当它这样做时，第一个 `+` 已经捕获了 `A` 和 `B`，因此没有争议。

Pratt 解析的作用是通过从左到右处理字符串来找到这些比邻居运算符更强大的“坏蛋”。我们即将开始编写一些代码，但让我们首先看一下另一个可以运行的示例。我们将使用函数组合运算符 `.`（点）作为具有高绑定力的*右*结合运算符。即， `f . g . h` 被解析为 `f . (g . h)`，或者，其绑定力如下：

```txt
  f     .    g     .    h
0   8.5    8   8.5    8   0
```

## 最小的 Pratt 解析器

我们将要解析一种将*单字符*数字和变量作为基本原子，将标点符号作为操作符的表达式。让我们定义一个简单的词法解析器（tokenizer）：

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Token {
    Atom(char),
    Op(char),
    Eof,
}

struct Lexer {
    tokens: Vec<Token>,
}

impl Lexer {
    fn new(input: &str) -> Lexer {
        let mut tokens = input
            .chars()
            .filter(|it| !it.is_ascii_whitespace())
            .map(|c| match c {
                '0'..='9' |
                'a'..='z' | 'A'..='Z' => Token::Atom(c),
                _ => Token::Op(c),
            })
            .collect::<Vec<_>>();
        tokens.reverse();
        Lexer { tokens }
    }

    fn next(&mut self) -> Token {
        self.tokens.pop().unwrap_or(Token::Eof)
    }
    fn peek(&mut self) -> Token {
        self.tokens.last().copied().unwrap_or(Token::Eof)
    }
}
```

为了确保我们得到正确的~~优先级~~绑定力，我们将把中缀表达式转换为黄金标准（无论出于何种原因，在波兰不太流行）明确记号—— S-表达式（S-expressions）：`1 + 2 * 3 == (+ 1 (* 2 3))`.

> 译注：S-表达式也叫做波兰表达式。

```rust
use std::fmt;

enum S {
    Atom(char),
    Cons(char, Vec<S>),
}

impl fmt::Display for S {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            S::Atom(i) => write!(f, "{}", i),
            S::Cons(head, rest) => {
                write!(f, "({}", head)?;
                for s in rest {
                    write!(f, " {}", s)?
                }
                write!(f, ")")
            }
        }
    }
}
```

让我们从这里开始：带有原子和两个中缀二元运算符 `+` 和 `*` 的表达式：

```rust
fn expr(input: &str) -> S {
    let mut lexer = Lexer::new(input);
    expr_bp(&mut lexer)
}

fn expr_bp(lexer: &mut Lexer) -> S {
    todo!()
}

#[test]
fn tests() {
    let s = expr("1 + 2 * 3");
    assert_eq!(s.to_string(), "(+ 1 (* 2 3))")
}
```

所以，我们用来处理左递归的方法大体上就是——从解析第一个数字开始，然后循环，消费运算符，然后……？

```rust
fn expr_bp(lexer: &mut Lexer) -> S {
    let lhs = match lexer.next() {
        Token::Atom(it) => S::Atom(it),
        t => panic!("bad token: {:?}", t),
    };

    loop {
        let op = match lexer.next() {
            Token::Eof => break,
            Token::Op(op) => op,
            t => panic!("bad token: {:?}", t),
        };

        todo!()
    }

    lhs
}

#[test]
fn tests() {
    let s = expr("1"); // ➊
    assert_eq!(s.to_string(), "1");
}
```

1.  请注意，我们已经可以解析这个简单的测试了！

我们想要使用这个绑定力的想法，所以让我们计算运算符的左绑定力和右绑定力。我们将使用 `u8` 来表示绑定力，因此，为了表示结合性，我们将增加 `1`。我们将为输入的末尾保留为 `0` 绑定力，因此运算符可以拥有的最低绑定力是 `1`。

> 译注：`+`、`-`、`*`、`/` 都具有左结合性，因此其右侧的绑定力高于左侧，即 `r_bp = l_bp + 1`。

```rust
fn expr_bp(lexer: &mut Lexer) -> S {
    let lhs = match lexer.next() {
        Token::Atom(it) => S::Atom(it),
        t => panic!("bad token: {:?}", t),
    };

    loop {
        let op = match lexer.peek() {
            Token::Eof => break,
            Token::Op(op) => op,
            t => panic!("bad token: {:?}", t),
        };
        let (l_bp, r_bp) = infix_binding_power(op);

        todo!()
    }

    lhs
}

fn infix_binding_power(op: char) -> (u8, u8) {
    match op {
        '+' | '-' => (1, 2),
        '*' | '/' => (3, 4),
        _ => panic!("bad op: {:?}")
    }
}
```

现在到了巧妙的部分，让我们引入递归。让我们考虑一下这个例子（具有以下绑定力）：

```txt
a   +   b   *   c   *   d   +   e
  1   2   3   4   3   4   1   2
```

光标在第一个 `+` 号处，我们知道左边的 `bp` 是 `1`，右边的是 `2`。`lhs` 存储了 `a`。`+` 的后的下一个运算符是 `*`，所以我们不应该将 `b` 和 `a` 相加。问题是我们还没有看到下一个运算符，我们只通过了 `+` 号。那么我们可以添加一个 lookahead（译注：向前检视数个字符）吗？看起来不行——我们得通过所有的 `b`、`c` 和 `d` 才能找到下一个具有较低绑定力的运算符，这听起来似乎没有边界。但我们发现了一些东西！我们当前的右优先级是 `2`，为了能够折叠表达式，我们需要找到下一个具有较低优先级的运算符。所以让我们从 `b` 开始递归调用 `expr_bp`，但同时告诉它一旦 `bp` 低于 `2` 就停止。这需要在主函数中添加 `min_bp` 参数。

瞧，我们有了一个功能齐全的最小 Pratt 解析器：

```rust
fn expr(input: &str) -> S {
    let mut lexer = Lexer::new(input);
    expr_bp(&mut lexer, 0) // ❺
}

fn expr_bp(lexer: &mut Lexer, min_bp: u8) -> S { // ➊
    let mut lhs = match lexer.next() {
        Token::Atom(it) => S::Atom(it),
        t => panic!("bad token: {:?}", t),
    };

    loop {
        let op = match lexer.peek() {
            Token::Eof => break,
            Token::Op(op) => op,
            t => panic!("bad token: {:?}", t),
        };

        let (l_bp, r_bp) = infix_binding_power(op);
        if l_bp < min_bp { // ➋
            break;
        }

        lexer.next(); // ❸
        let rhs = expr_bp(lexer, r_bp);

        lhs = S::Cons(op, vec![lhs, rhs]); // ❹
    }

    lhs
}

fn infix_binding_power(op: char) -> (u8, u8) {
    match op {
        '+' | '-' => (1, 2),
        '*' | '/' => (3, 4),
        _ => panic!("bad op: {:?}"),
    }
}

#[test]
fn tests() {
    let s = expr("1");
    assert_eq!(s.to_string(), "1");

    let s = expr("1 + 2 * 3");
    assert_eq!(s.to_string(), "(+ 1 (* 2 3))");

    let s = expr("a + b * c * d + e");
    assert_eq!(s.to_string(), "(+ (+ a (* (* b c) d)) e)");
}
```

1.  `min_bp` 参数是关键的补充。 `expr_bp` 现在解析具有相对较高绑定力的表达式。一旦它发现比 `min_bp` 绑定力弱的运算符，它就会停止。
2.  这是“停止”的点。
3.  在这里我们越过运算符本身并进行递归调用。注意我们如何使用 `l_bp` 来检查 `min_bp`，以及将 `r_bp` 作为递归调用的新 `min_bp`。因此，你可以将 `min_bp` 看作是当前表达式左侧运算符的绑定力。
4.  最后，在解析正确的右侧之后，我们组装新的当前表达式。
5.  开始递归时，我们使用的绑定力为零。记住，在开始时左侧运算符的绑定力是最低的，即为零，因为那里实际上没有运算符。

是的，这 40 行*就是* Pratt 解析算法。它们很巧妙，但是，如果你理解它们，其他一切都是简单的添加。

## 花哨的东西

现在让我们添加各种奇怪的表达式来展示算法的强大功能和灵活性。首先，我们添加一个高优先级的右结合函数复合运算符：`.`：

```rust,hl_lines=5
fn infix_binding_power(op: char) -> (u8, u8) {
    match op {
        '+' | '-' => (1, 2),
        '*' | '/' => (3, 4),
        '.' => (6, 5),
        _ => panic!("bad op: {:?}"),
    }
}
```

是的，只有一行！请注意运算符的左侧绑定得更加紧密，这为我们提供了所需的右关联性：

```rust
let s = expr("f . g . h");
assert_eq!(s.to_string(), "(. f (. g h))");

let s = expr(" 1 + 2 + f . g . h * 3 * 4");
assert_eq!(s.to_string(), "(+ (+ 1 2) (* (* (. f (. g h)) 3) 4))");
```

现在，让我们添加一元运算符 `-`，它的绑定比二元算术运算符更紧密，但不如组合紧密。这需要改变我们开始循环的方式，因为我们不再假设第一个标记是原子，并且还需要处理减号。但让类型来驱动我们吧。首先，我们从绑定力开始。由于这是一个一元运算符，它实际上只有右绑定力，所以，咳咳，让我们直接编写一下代码：

```rust
fn prefix_binding_power(op: char) -> ((), u8) { // ➊
    match op {
        '+' | '-' => ((), 5),
        _ => panic!("bad op: {:?}", op),
    }
}

fn infix_binding_power(op: char) -> (u8, u8) {
    match op {
        '+' | '-' => (1, 2),
        '*' | '/' => (3, 4),
        '.' => (8, 7), // ➋
        _ => panic!("bad op: {:?}"),
    }
}
```

1.  在这里，我们返回一个空 `()`，以明确表示这是一个前缀运算符，而不是后缀运算符，因此只能绑定右侧的内容。
2.  注意，因为我们想在 `.` 和 `*` 之间添加一元负号 `-`，所以我们需要将 `.` 的优先级提高两个等级。一般规则是我们使用奇数优先级作为基础，如果运算符是二元的，则通过一个单位来调整优先级。对于一元运算符负号 `-` 来说，这无关紧要，我们可以使用 `5` 或 `6`，但使用奇数优先级会更一致。

将其插入 `expr_bp`，我们得到：

```rust
fn expr_bp(lexer: &mut Lexer, min_bp: u8) -> S {
    let mut lhs = match lexer.next() {
        Token::Atom(it) => S::Atom(it),
        Token::Op(op) => {
            let ((), r_bp) = prefix_binding_power(op);
            todo!()
        }
        t => panic!("bad token: {:?}", t),
    };
    ...
}
```

现在，我们只有 `r_bp` 而没有 `l_bp`，所以让我们只复制主循环中一半的代码？记住，我们在递归调用中使用 `r_bp`。

```rust
fn expr_bp(lexer: &mut Lexer, min_bp: u8) -> S {
    let mut lhs = match lexer.next() {
        Token::Atom(it) => S::Atom(it),
        Token::Op(op) => {
            let ((), r_bp) = prefix_binding_power(op);
            let rhs = expr_bp(lexer, r_bp);
            S::Cons(op, vec![rhs])
        }
        t => panic!("bad token: {:?}", t),
    };

    loop {
        let op = match lexer.peek() {
            Token::Eof => break,
            Token::Op(op) => op,
            t => panic!("bad token: {:?}", t),
        };

        let (l_bp, r_bp) = infix_binding_power(op);
        if l_bp < min_bp {
            break;
        }

        lexer.next();
        let rhs = expr_bp(lexer, r_bp);

        lhs = S::Cons(op, vec![lhs, rhs]);
    }

    lhs
}

#[test]
fn tests() {
    ...

    let s = expr("--1 * 2");
    assert_eq!(s.to_string(), "(* (- (- 1)) 2)");

    let s = expr("--f . g");
    assert_eq!(s.to_string(), "(- (- (. f g)))");
}
```

有趣的是，这种纯粹机械化、类型驱动的转换是有效的。当然，你也可以推理出它为什么有效。同样的论点也适用于：在我们处理了一个前缀运算符后，操作数由绑定得更加紧密的的运算符组成，而我们恰好有一个函数可以解析比指定优先级更加紧密的表达式。

好吧，越来越简单了。如果使用 `((), u8)` 对前缀运算符“正好奏效”，那么 `(u8, ())` 能处理后缀运算符吗？好，让我们添加 `!` 作为阶乘运算符。它应该比 `-` 绑定得更紧，因为 `-(92!)` 显然比 `(-92)!` 更有用。所以，熟悉的流程——新的优先级函数，调整 `.` 的优先级（这一点在 Pratt 解析器中确实很烦人），复制粘贴代码...

```rust
let (l_bp, ()) = postfix_binding_power(op);
if l_bp < min_bp {
    break;
}

let (l_bp, r_bp) = infix_binding_power(op);
if l_bp < min_bp {
    break;
}
```

等等，这里有些问题。在我们解析前缀表达式之后，我们可能会看到一个后缀或中缀运算符。但是我们在遇到未识别的运算符时会退出，这样是行不通的……所以，我们让 `postfix_binding_power` 返回一个 option，以便在运算符不是后缀的情况下处理：

```rust,hl_lines=19-27 50-56
fn expr_bp(lexer: &mut Lexer, min_bp: u8) -> S {
    let mut lhs = match lexer.next() {
        Token::Atom(it) => S::Atom(it),
        Token::Op(op) => {
            let ((), r_bp) = prefix_binding_power(op);
            let rhs = expr_bp(lexer, r_bp);
            S::Cons(op, vec![rhs])
        }
        t => panic!("bad token: {:?}", t),
    };

    loop {
        let op = match lexer.peek() {
            Token::Eof => break,
            Token::Op(op) => op,
            t => panic!("bad token: {:?}", t),
        };

        if let Some((l_bp, ())) = postfix_binding_power(op) {
            if l_bp < min_bp {
                break;
            }
            lexer.next();

            lhs = S::Cons(op, vec![lhs]);
            continue;
        }

        let (l_bp, r_bp) = infix_binding_power(op);
        if l_bp < min_bp {
            break;
        }

        lexer.next();
        let rhs = expr_bp(lexer, r_bp);

        lhs = S::Cons(op, vec![lhs, rhs]);
    }

    lhs
}

fn prefix_binding_power(op: char) -> ((), u8) {
    match op {
        '+' | '-' => ((), 5),
        _ => panic!("bad op: {:?}", op),
    }
}

fn postfix_binding_power(op: char) -> Option<(u8, ())> {
    let res = match op {
        '!' => (7, ()),
        _ => return None,
    };
    Some(res)
}

fn infix_binding_power(op: char) -> (u8, u8) {
    match op {
        '+' | '-' => (1, 2),
        '*' | '/' => (3, 4),
        '.' => (10, 9),
        _ => panic!("bad op: {:?}"),
    }
}

#[test]
fn tests() {
    let s = expr("-9!");
    assert_eq!(s.to_string(), "(- (! 9))");

    let s = expr("f . g !");
    assert_eq!(s.to_string(), "(! (. f g))");
}
```

很好，新旧测试都通过了。

现在，我们准备添加一种新的表达式：括号表达式。实际上，这并不难，我们本来可以从一开始就做到这一点，但在这里处理这个问题是有意义的，稍后你就会明白为什么。括号只是一个 primary 表达式，其处理方式与原子类似：

```rust
let mut lhs = match lexer.next() {
    Token::Atom(it) => S::Atom(it),
    Token::Op('(') => {
        let lhs = expr_bp(lexer, 0);
        assert_eq!(lexer.next(), Token::Op(')'));
        lhs
    }
    Token::Op(op) => {
        let ((), r_bp) = prefix_binding_power(op);
        let rhs = expr_bp(lexer, r_bp);
        S::Cons(op, vec![rhs])
    }
    t => panic!("bad token: {:?}", t),
};
```

不幸的是，以下测试失败：

```rust
let s = expr("(((0)))");
assert_eq!(s.to_string(), "0");
```

panic 来自下面的循环——我们唯一的终止条件是到达 eof，而 `)` 显然不是 eof。修复这个问题的最简单方法是让 `infix_binding_power` 在遇到未识别的操作数时返回 `None`。这样，它将也变得类似于 `postfix_binding_power`！

```rust,hl_lines=4-8 34-44 67-75
fn expr_bp(lexer: &mut Lexer, min_bp: u8) -> S {
    let mut lhs = match lexer.next() {
        Token::Atom(it) => S::Atom(it),
        Token::Op('(') => {
            let lhs = expr_bp(lexer, 0);
            assert_eq!(lexer.next(), Token::Op(')'));
            lhs
        }
        Token::Op(op) => {
            let ((), r_bp) = prefix_binding_power(op);
            let rhs = expr_bp(lexer, r_bp);
            S::Cons(op, vec![rhs])
        }
        t => panic!("bad token: {:?}", t),
    };

    loop {
        let op = match lexer.peek() {
            Token::Eof => break,
            Token::Op(op) => op,
            t => panic!("bad token: {:?}", t),
        };

        if let Some((l_bp, ())) = postfix_binding_power(op) {
            if l_bp < min_bp {
                break;
            }
            lexer.next();

            lhs = S::Cons(op, vec![lhs]);
            continue;
        }

        if let Some((l_bp, r_bp)) = infix_binding_power(op) {
            if l_bp < min_bp {
                break;
            }

            lexer.next();
            let rhs = expr_bp(lexer, r_bp);

            lhs = S::Cons(op, vec![lhs, rhs]);
            continue;
        }

        break;
    }

    lhs
}

fn prefix_binding_power(op: char) -> ((), u8) {
    match op {
        '+' | '-' => ((), 5),
        _ => panic!("bad op: {:?}", op),
    }
}

fn postfix_binding_power(op: char) -> Option<(u8, ())> {
    let res = match op {
        '!' => (7, ()),
        _ => return None,
    };
    Some(res)
}

fn infix_binding_power(op: char) -> Option<(u8, u8)> {
    let res = match op {
        '+' | '-' => (1, 2),
        '*' | '/' => (3, 4),
        '.' => (10, 9),
        _ => return None,
    };
    Some(res)
}
```

现在让我们添加数组索引运算符：`a[i]`。它是什么类型的运算符？周围类型？如果只是 `a[]`，它显然是后缀的。如果只是 `[i]`，它会像括号一样工作。关键在于：`i` 部分实际上并不参与整个绑定力游戏，因为它有明确的范围。因此，我们可以这样做：

```rust,hl_lines=30-36
fn expr_bp(lexer: &mut Lexer, min_bp: u8) -> S {
    let mut lhs = match lexer.next() {
        Token::Atom(it) => S::Atom(it),
        Token::Op('(') => {
            let lhs = expr_bp(lexer, 0);
            assert_eq!(lexer.next(), Token::Op(')'));
            lhs
        }
        Token::Op(op) => {
            let ((), r_bp) = prefix_binding_power(op);
            let rhs = expr_bp(lexer, r_bp);
            S::Cons(op, vec![rhs])
        }
        t => panic!("bad token: {:?}", t),
    };

    loop {
        let op = match lexer.peek() {
            Token::Eof => break,
            Token::Op(op) => op,
            t => panic!("bad token: {:?}", t),
        };

        if let Some((l_bp, ())) = postfix_binding_power(op) {
            if l_bp < min_bp {
                break;
            }
            lexer.next();

            lhs = if op == '[' {
                let rhs = expr_bp(lexer, 0);
                assert_eq!(lexer.next(), Token::Op(']'));
                S::Cons(op, vec![lhs, rhs])
            } else {
                S::Cons(op, vec![lhs])
            };
            continue;
        }

        if let Some((l_bp, r_bp)) = infix_binding_power(op) {
            if l_bp < min_bp {
                break;
            }

            lexer.next();
            let rhs = expr_bp(lexer, r_bp);

            lhs = S::Cons(op, vec![lhs, rhs]);
            continue;
        }

        break;
    }

    lhs
}

fn prefix_binding_power(op: char) -> ((), u8) {
    match op {
        '+' | '-' => ((), 5),
        _ => panic!("bad op: {:?}", op),
    }
}

fn postfix_binding_power(op: char) -> Option<(u8, ())> {
    let res = match op {
        '!' | '[' => (7, ()), // ➊
        _ => return None,
    };
    Some(res)
}

fn infix_binding_power(op: char) -> Option<(u8, u8)> {
    let res = match op {
        '+' | '-' => (1, 2),
        '*' | '/' => (3, 4),
        '.' => (10, 9),
        _ => return None,
    };
    Some(res)
}

#[test]
fn tests() {
    ...

    let s = expr("x[0][1]");
    assert_eq!(s.to_string(), "([ ([ x 0) 1)");
}
```

1.  注意，我们为 `!` 和 `[` 使用了相同的优先级。一般来说，为了算法的正确性，在做决策时，优先级永远不能相等。否则，我们可能会遇到类似之前的小调整中的情况，那时有两个同样合适的折叠候选项。然而，我们只比较右侧的 `bp` 和左侧的 `bp`！因此，对于两个后缀运算符，它们具有相同的优先级是可以的，因为它们都是右侧的。

最后，所有运算符的最终 boos，可怕的三元运算符：

```txt
c ? e1 : e2
```

这是……“所有其他地方”类型运算符吗？好吧，让我们稍微改变一下三元运算符的语法：

```txt
c [ e1 ] e2
```

让我们回忆一下，`a[i]` 被认为是一个后缀运算符 + 括号的组合……所以，`?` 和 `:` 实际上是一对奇特的括号！让我们这样处理它们吧！现在，优先级和结合性呢？在这种情况下，结合性到底是什么？

```txt
a ? b : c ? d : e
```

为了弄清楚这一点，我们只需要将括号部分变形：

```txt
a ?: c ?: e
```

这可以解析为

```txt
(a ?: c) ?: e
```

或者

```rust
a ?: (c ?: e)
```

哪一种更有用呢？对于这样的 `?` 链：

```txt
a ? b :
c ? d :
e
```

右结合的解读更有用。在优先级方面，三元运算符优先级较低。在 C 语言中，只有 `=` 和 `,` 的优先级更低。既然提到这里了，我们也添加上 C 语言风格的右结合 `=`。

这是我们最完整、最完美的简单 Pratt 解析器版本：

```rust
use std::{fmt, io::BufRead};

enum S {
    Atom(char),
    Cons(char, Vec<S>),
}

impl fmt::Display for S {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            S::Atom(i) => write!(f, "{}", i),
            S::Cons(head, rest) => {
                write!(f, "({}", head)?;
                for s in rest {
                    write!(f, " {}", s)?
                }
                write!(f, ")")
            }
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Token {
    Atom(char),
    Op(char),
    Eof,
}

struct Lexer {
    tokens: Vec<Token>,
}

impl Lexer {
    fn new(input: &str) -> Lexer {
        let mut tokens = input
            .chars()
            .filter(|it| !it.is_ascii_whitespace())
            .map(|c| match c {
                '0'..='9'
                | 'a'..='z' | 'A'..='Z' => Token::Atom(c),
                _ => Token::Op(c),
            })
            .collect::<Vec<_>>();
        tokens.reverse();
        Lexer { tokens }
    }

    fn next(&mut self) -> Token {
        self.tokens.pop().unwrap_or(Token::Eof)
    }
    fn peek(&mut self) -> Token {
        self.tokens.last().copied().unwrap_or(Token::Eof)
    }
}

fn expr(input: &str) -> S {
    let mut lexer = Lexer::new(input);
    expr_bp(&mut lexer, 0)
}

fn expr_bp(lexer: &mut Lexer, min_bp: u8) -> S {
    let mut lhs = match lexer.next() {
        Token::Atom(it) => S::Atom(it),
        Token::Op('(') => {
            let lhs = expr_bp(lexer, 0);
            assert_eq!(lexer.next(), Token::Op(')'));
            lhs
        }
        Token::Op(op) => {
            let ((), r_bp) = prefix_binding_power(op);
            let rhs = expr_bp(lexer, r_bp);
            S::Cons(op, vec![rhs])
        }
        t => panic!("bad token: {:?}", t),
    };

    loop {
        let op = match lexer.peek() {
            Token::Eof => break,
            Token::Op(op) => op,
            t => panic!("bad token: {:?}", t),
        };

        if let Some((l_bp, ())) = postfix_binding_power(op) {
            if l_bp < min_bp {
                break;
            }
            lexer.next();

            lhs = if op == '[' {
                let rhs = expr_bp(lexer, 0);
                assert_eq!(lexer.next(), Token::Op(']'));
                S::Cons(op, vec![lhs, rhs])
            } else {
                S::Cons(op, vec![lhs])
            };
            continue;
        }

        if let Some((l_bp, r_bp)) = infix_binding_power(op) {
            if l_bp < min_bp {
                break;
            }
            lexer.next();

            lhs = if op == '?' {
                let mhs = expr_bp(lexer, 0);
                assert_eq!(lexer.next(), Token::Op(':'));
                let rhs = expr_bp(lexer, r_bp);
                S::Cons(op, vec![lhs, mhs, rhs])
            } else {
                let rhs = expr_bp(lexer, r_bp);
                S::Cons(op, vec![lhs, rhs])
            };
            continue;
        }

        break;
    }

    lhs
}

fn prefix_binding_power(op: char) -> ((), u8) {
    match op {
        '+' | '-' => ((), 9),
        _ => panic!("bad op: {:?}", op),
    }
}

fn postfix_binding_power(op: char) -> Option<(u8, ())> {
    let res = match op {
        '!' => (11, ()),
        '[' => (11, ()),
        _ => return None,
    };
    Some(res)
}

fn infix_binding_power(op: char) -> Option<(u8, u8)> {
    let res = match op {
        '=' => (2, 1),
        '?' => (4, 3),
        '+' | '-' => (5, 6),
        '*' | '/' => (7, 8),
        '.' => (14, 13),
        _ => return None,
    };
    Some(res)
}

#[test]
fn tests() {
    let s = expr("1");
    assert_eq!(s.to_string(), "1");

    let s = expr("1 + 2 * 3");
    assert_eq!(s.to_string(), "(+ 1 (* 2 3))");

    let s = expr("a + b * c * d + e");
    assert_eq!(s.to_string(), "(+ (+ a (* (* b c) d)) e)");

    let s = expr("f . g . h");
    assert_eq!(s.to_string(), "(. f (. g h))");

    let s = expr(" 1 + 2 + f . g . h * 3 * 4");
    assert_eq!(
        s.to_string(),
        "(+ (+ 1 2) (* (* (. f (. g h)) 3) 4))",
    );

    let s = expr("--1 * 2");
    assert_eq!(s.to_string(), "(* (- (- 1)) 2)");

    let s = expr("--f . g");
    assert_eq!(s.to_string(), "(- (- (. f g)))");

    let s = expr("-9!");
    assert_eq!(s.to_string(), "(- (! 9))");

    let s = expr("f . g !");
    assert_eq!(s.to_string(), "(! (. f g))");

    let s = expr("(((0)))");
    assert_eq!(s.to_string(), "0");

    let s = expr("x[0][1]");
    assert_eq!(s.to_string(), "([ ([ x 0) 1)");

    let s = expr(
        "a ? b :
         c ? d
         : e",
    );
    assert_eq!(s.to_string(), "(? a b (? c d e))");

    let s = expr("a = 0 ? b : c = d");
    assert_eq!(s.to_string(), "(= a (= (? 0 b c) d))")
}

fn main() {
    for line in std::io::stdin().lock().lines() {
        let line = line.unwrap();
        let s = expr(&line);
        println!("{}", s)
    }
}
```

代码也可以在[这个仓库](https://github.com/matklad/minipratt)中找到，Eof :-)
