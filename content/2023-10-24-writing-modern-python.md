+++
title = "编写现代的 Python"
date = 2023-10-24T20:25:39+08:00

[taxonomies]
categories = ["Python"]
tags = ["Python", "Programming Languages"]
+++

好久没写博客了，今天想结合我个人的经验聊一聊如何编写现代的 Python 代码。

在聊这个问题之前，首先要定义一下什么是“现代的 Python”和我为什么想要使用这种方式编写 Python。

或许你听说过“Modern C++”，这通常指的是 C++11 之后的 C++ 标准，现代的 C++ 带来了许多新的特性，如智能指针、auto、更强大的标准库、增强的 for 循环、移动语义、lambda 表达式等，这些新特性使得 C++ 赶上了时代的脚步，大大提高了开发的效率。

而 Python 作为诞生于三十多年前的编程语言，在这三十年间也发生了许多变化，最著名的变化莫过于 Python 2 到 Python 3 的不兼容升级。但本文我想聊的并非所有的 Python 新特性，毕竟 Python 的新特性可以直接在 [What’s New in Python](https://docs.python.org/3/whatsnew/index.html) 中找到，我想说的是一种编程风格或者说编程范式。

这些思想很大程度上并非我的原创，而是来自于 Rust 语言。自从我开始使用 Rust 语言，它就很大程度上影响了我编写其他语言的的方式，尤其是 Python 语言。

这篇博客还受到了 [Writing Python like it's Rust](https://kobzol.github.io/rust/python/2023/05/20/writing-python-like-its-rust.html) 的启发，其中的很多思想都和我不谋而合 (实际上我是写到一半才发现这篇文章的，感觉他把我想说的都说的差不多了)。

## 开始之前：Formatter and Linter

在开始之前，我想先聊一个和本文关系不大的问题，那就是格式化和风格检查。

几乎所有的语言都有官方推荐或社区广泛认同的代码格式和风格，而许多诞生比较晚的现代语言还在工具链中附带了 Formatter 和 Linter，比如 Rust 的 `rustfmt` 和 `clippy`。但很遗憾 Python 并没有一个附带的 Formatter 和 Linter。

在所有 Python 的 Formatter 中我一直使用的是 [black](https://github.com/psf/black)，因为它相对比较严格，就像前端届的 Prettier 一样，它是一个“固执己见”(opinionated) 的格式化工具。我觉得 Formatter 的主要作用就是提供一个尽可能统一的格式，以尽可能省去手动格式化和时间和团队协作中对格式的争论，因此，Formatter 越严格越好，至于细节的格式，我并没有特别的偏好，只要不太奇怪，严格和统一就是最好的。

而在 Linter 中我首推 [Ruff](https://github.com/astral-sh/ruff)，它是一个用 Rust 编写的 Python Linter，因此具有极快的速度。是真的非常快，比传统的 Python Linter 快几个数量级。除此之外，它的规则也比较全，涵盖了代码风格的方方面面，可以完全替代 Flake8 和 isort。除此之外，如果需要更加细致的代码检查的话可以选择 [Pylint](https://github.com/pylint-dev/pylint)，它会对代码进行更加深入的静态检查，但代价是很慢，比 Ruff 慢 2-3 个数量级。

在现代语言中，我认为应该永远使用尽可能严格的 Formatter 和 Linter，人是一个不精确的机器，没有人能永远按照最佳实践编写代码，尽管关于软件架构和复杂的逻辑仍然需要人的设计，但至少我们应该在细节的代码格式和风格方面尽可能遵循最佳实践，计算机擅长干的事就不要让人来做，让工具来约束是最简单的。并且尽可能严格的 Formatter 和 Linter 也有助于团队协作时避免风格的差异。

## 现代 Python 的哲学

我认为，在程序设计中的一个很重要的原则就是“承诺”，比如 Rust 的宣传的重点就是它的安全性承诺和零开销抽象承诺，即只要不使用 `unsafe` 那就不可能出现内存安全问题，以及只需要为用到的功能付出时间、空间代价。

很显然，Python 作为一个有 GC 的语言，已经提供了安全性承诺，而零开销抽象也并非 Python 语言所关注的重点，这里我希望的是通过一种良好的代码风格做到健壮性 (也被翻译为鲁棒性，但我觉得这个翻译很糟糕)。

传统上，我们编写 Python 时很容易写出类似下面的代码：

```python
def get_person(person_id):
    ...
    return {
        "id": person_id,
        "name": "Alice",
        "permission": {
            "id": 0,
            "is_admin": True,
            "user_groups": [],
        },
    }


def check_permission(person):
    return person["permission"]["is_admin"] or "root" in person["permission"]["user_groups"]

```

这种代码是不好的，因为它很容易被误用，并且会提高修改、维护和使用的成本。当我们使用 `check_permission` 这个函数时，在不阅读函数体的情况下，我们无法确定这里需要的 person 参数到底是什么，在编写或修改这个函数时，我们也无法保证正确性，比如出现 person 字典的结构发生变更但忘记修改 `check_permission` 函数，或者 `check_permission` 函数里的字段名出现 typo 等。

就像墨菲定律一样，任何可能被误用的，最终一定会被误用。更重要的是，这样的代码没有提供任何健壮性承诺，当一个人 (也可能是自己) 在使用和修改这样的代码时，必须谨小慎微，并且永远无法保证自己没有出错。

因此，我认为，更加现代的 Python 编写风格就是要利用 Python 在近几个版本提供的几个有用的新特性来尽可能避免“不确定性”，提供更多的健壮性承诺，为了做到这一点，我们需要合理地限制 Python 的动态特性、坚持尽可能早的异常 (编译期异常优于运行时异常) 和使非法状态不可表示。

## 类型注解 (Type Hints)

首先，也是最重要的就是为 Python 代码编写类型注解，类型注解是在 [PEP 484](https://peps.python.org/pep-0484/) 和 [PEP 483](https://peps.python.org/pep-0483/) 中首次引入，并在 Python 3.5 版本正式开始支持的特性。直到现在仍在不断迭代和添加新特性中。

类型注解可以为 Python 提供静态的类型检查，它仅在静态类型检查器中被使用，而没有运行时性能损耗，即 Python 的类型注解会在运行时被忽略 (实际上可以被运行时获取，会被存储在 `__annotations__` 等魔术字段中，但不会进行检查)。

这相当于为 Python 引入了而外的编译期检查，能够在运行前避免常见的类型问题。常见的静态类型检查工具有 Python 官方提供的 [mypy](https://github.com/python/mypy)、微软提供的 [pyright](https://github.com/microsoft/pyright)、FaceBook 提供的 [pyre](https://github.com/facebook/pyre-check) 和 Google 提供的 [pytype](https://github.com/google/pytype)，他们在一些细节上有不同的处理方式。

需要指出的是，我觉得 Python 的类型注解并不十分强大，与 Rust 这种静态类型语言自然没法比，与 TypeScript 相比也有不小的差距 (TS 的类型系统甚至是图灵完备的)，但是，这也并非是一个缺点，Python 的类型注解系统是十分 Pythonic 的，并且足够简单易用，不会像 TS 一样有非常复杂的类型体操，更重要的是，Python 的类型注解一直在进步，几乎每个版本都有关于类型注解的新特性加入。

很多人觉得为 Python 编写类型注解会影响编码速度。但我认为并非如此，单纯考虑额外编写类型注解的时间当然至少增加了打字的时间。但首先，在大多数情况下，即使不编写类型注解，在编写代码时自己也是清楚变量的类型的，因为类型本身就是程序的一部分，因此，显式写出类型只增加了打字时间而没有增加思考时间，大部分编程的速度瓶颈都不在打字时间上。其次，编写类型注解可以充分利用编辑器的自动提示功能，在很多情况下反而可以加快编码速度。最后，大多数程序都不是只编写一次、只运行一次、长度很短的小脚本，算上修改维护的时间为 Python 编写类型注解绝对是合算的。

## 使用数据类 (dataclass)

数据类是在 Python 3.7 引入的，它基本上相当于 Python 中的结构体，不同于字典这种松散的结构，就像结构体一样，数据类可以限定字段的多少、名称、类型。

开始的例子使用数据类重写后：

```python
from dataclasses import dataclass


@dataclass
class Permission:
    id: int
    is_admin: bool
    user_groups: list[str]


@dataclass
class Person:
    id: int
    name: str
    permission: Permission


def get_person(person_id: int) -> Person:
    ...
    return Person(
        id=person_id,
        name="Alice",
        permission=Permission(
            id=0,
            is_admin=True,
            user_groups=[],
        ),
    )


def check_permission(person: Person) -> bool:
    return person.permission.is_admin or "root" in person.permission.user_groups

```

使用数据类而非字典的优势是显而易见的，首先，它提供了嵌套类型中的类型提示和检查，避免了类型和字段错误，其次，它非常方便重构，修改字段名称后大部分编辑器都可以自动进行重构。

Python 自带的 `dataclasses` 并不会进行运行时类型检查，因此不适用于序列化和反序列化场景中，如果需要运行时数据校验的话可以使用 [Pydantic](https://github.com/pydantic/pydantic)。

## NewType

在 Rust 中存在一种被称为 `NewType` 的用法，可以查看下面的 [Rust 官方的例子](https://doc.rust-lang.org/rust-by-example/generics/new_types.html)：

```rust
struct Years(i64);

struct Days(i64);

impl Years {
    pub fn to_days(&self) -> Days {
        Days(self.0 * 365)
    }
}


impl Days {
    /// truncates partial years
    pub fn to_years(&self) -> Years {
        Years(self.0 / 365)
    }
}

fn old_enough(age: &Years) -> bool {
    age.0 >= 18
}

fn main() {
    let age = Years(5);
    let age_days = age.to_days();
    println!("Old enough {}", old_enough(&age));
    println!("Old enough {}", old_enough(&age_days.to_years()));
    // println!("Old enough {}", old_enough(&age_days));
}

```

它可以指定一个和原有的类型完全一致的新类型，但额外指定它的预期用途，比如上面的例子，`i64` 只表示这是一个 64 位整数而没有任何其他的信息，而 `Years` 则进一步说明了这是一个用于表示年份的整数。同时 NewType 也限制了新类型的用法，即封装后的类型只有 `to_days()` 这一个关联方法，而无法再使用对 `i64` 可以使用的其他方法，因为其他方法对于“年”这个类型来说很可能是没有意义的。

这也是一个防止误用的技巧。如果上面的 `old_enough` 函数的签名是：`fn old_enough(age: &i64) -> bool`，那么使用者就无法从函数的读出 `age` 的单位是秒、天、月还是年，从而可能造成误用。使用 NewType 可以让类型包含更多的信息，进一步明确类型。

在获得上述好处的同时，完全没有任何性能代价，NewType 被编译后完全就是原本的类型，所有的限制都是编译期的，没有任何运行时损耗。

Python 中也提供了 NewType 的支持。

```python
from typing import NewType

Years = NewType("Years", int)
Days = NewType("Days", int)


def old_enough(age: Years) -> bool:
    return age >= 18


if __name__ == "__main__":
    age = Years(5)
    print(f"Old enough {old_enough(age)}")

```

Python 是支持继承的，因此上面的操作和创建一个 `Years` 类继承 `int` 的效果类似，但是，创建子类是有运行时开销的，而 NewType 则没有。NewType 仅在类型检查中被使用，相当于在类型检查中认为是一个子类，在运行时认为是它本身。

## 组合优于继承

在 Rust 中是没有类 (class) 的，但存在 [trait](<https://en.wikipedia.org/wiki/Trait_(computer_programming)>) 的概念，类似其他语言的接口 ([protocols/interfaces](<https://en.wikipedia.org/wiki/Interface_(object-oriented_programming)>))。

因为 Python 支持多继承和抽象基类，因此在 Python 中组合和继承的差别实际上是比较模糊的。

在 Python 中可以利用抽象基类实现组合：

```python
from abc import ABC, abstractmethod


class Openable(ABC):
    @abstractmethod
    def open(self):
        ...


class Closable(ABC):
    @abstractmethod
    def close(self):
        ...


class File(Openable, Closable):
    def open(self):
        print("open")

    def close(self):
        print("close")


def open_it(openable: Openable):
    openable.open()


open_it(File())

```

或者利用 [PEP 544](https://peps.python.org/pep-0544/) 在 Python 3.8 中引入的 Protocol 和结构子类型：

```python
from typing import Protocol


class Openable(Protocol):
    def open(self):
        ...


class Closable(Protocol):
    def close(self):
        ...


class File:
    def open(self):
        print("open")

    def close(self):
        print("close")


def open_it(openable: Openable):
    openable.open()


open_it(File())

```

它们的主要区别在于前者需要显示声明而后者不需要，前者提供了运行时检查 (有运行时开销) 而后者没有。通常认为后者是更加 pythonic 的。

## 构造函数

在 Rust 中不存在类似 Python 中 `__init__` 的默认构造器，取而代之的是使用普通的关联函数进行构造，这有什么好处呢？

这有助于更加明确地实现一个类型有多个构造器的情况，比如：

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn new(width: u32, height: u32) -> Self {
        Self { width, height }
    }

    fn square(size: u32) -> Self {
        Self {
            width: size,
            height: size,
        }
    }
}

fn main() {
    Rectangle::new(1, 2)
    Rectangle::square(1)
}

```

对于 Python 传统上则可能会写成：

```python
from typing import overload


class Rectangle:
    width: int
    height: int

    @overload
    def __init__(self, width: int) -> None:
        ...

    @overload
    def __init__(self, width: int, height: int) -> None:
        ...

    def __init__(self, width: int, height: int | None = None) -> None:
        if height is None:
            height = width
        self.width = width
        self.height = height


if __name__ == "__main__":
    Rectangle(1, 2)
    Rectangle(1)

```

为什么一个结构体/类只能有一个构造函数呢？即使使用了 `overload` 类型注解，上面的 Python 代码仍然并不利于识读，当一个不熟悉 `Rectangle` 的人看到类似 `Rectangle(1)` 的代码，他并无法直接认识到这是用于构造正方形的方法。

因此我认为可以使用下面的方式实现：

```python
from dataclasses import dataclass
from typing import Self


@dataclass
class Rectangle:
    width: int
    height: int

    @classmethod
    def square(cls, size: int) -> Self:
        return cls(size, size)


if __name__ == "__main__":
    Rectangle(1, 2)
    Rectangle.square(1)

```

## 代数数据类型和模式匹配

代数数据类型 ([algebraic data type(ADT)](https://en.wikipedia.org/wiki/Algebraic_data_type)) 指的是一种复合类型，包括积类型与和类型。

积类型的典型例子就是元组，其可能值是其字段类型可能值的笛卡尔积。

和类型的例子是 Rust 中的 `enum` 和 Python 中的 `Union`，其可能值是其字段类型的并集。

```python
class A: ...
class B: ...
class C: ...
class D: ...

Type1 = A | B
Type2 = C | D

product_type = tuple[Type1, Type2]
# possible values: (A, C) | (A, D) | (B, C) | (B, D)
sum_type = Type1 | Type2
# possible values: A | B | C | D

```

ADT 中积类型的应用比较简单，在大多数语言中均有广泛应用，下面重点关注一下和类型。

和类型和继承/接口不同在于，继承/接口是开放的，而和类型是封闭的，也就是说，如果我们指定一个函数可以接受 A 类型，那么它就可以接受 A 的所有子类型，但我们无从得知这个 A 有几个子类型，因此只能使用定义在 A 中的公共方法。而如果是和类型，则可以显式地得知这个它是由几个字段类型组合而成的，从而对每个字段类型分别进行处理。

结合模式匹配，就可以实现类似下面的例子，可以静态检查是否忘记了处理某种情况。

```rust
enum Node {
    If {
        test: Box<Node>,
        consequent: Box<Node>,
        alternate: Option<Box<Node>>,
    },
    While {
        test: Box<Node>,
        body: Box<Node>,
    },
    Add {
        left: Box<Node>,
        right: Box<Node>,
    },
    Ident(String),
}

fn eval(node: &Node) {
    match node {
        Node::If {
            test,
            consequent,
            alternate,
        } => todo!(),
        Node::While { test, body } => todo!(),
        Node::Add { left, right } => todo!(),
        Node::Ident(ident) => todo!(),
    }
}

```

对于 Python 来说，Python 在 3.10 引入了模式匹配 `match-case` 语法：

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import NewType, assert_never


@dataclass
class If:
    test: Node
    consequent: Node
    alternate: Node | None


@dataclass
class While:
    test: Node
    body: Node


@dataclass
class Add:
    left: Node
    right: Node


Ident = NewType("Ident", str)

Node = If | While | Add | Ident


def eval(node: Node):
    match node:
        case If(test, consequent, alternate):
            pass
        case While(test, body):
            pass
        case Add(left, right):
            pass
        case Ident(ident):
            pass
        case _:
            assert_never(node)
```

但是，Python 的类型系统并不强制要求匹配完所有可能的分支，因此，需要在最后添加 `assert_never` 以要求类型检查器在未匹配完成时报错。

## 总结

总之，编写所谓“现代的 Python”的关键就在于利用 Python 的类型系统来保证 Python 的健壮性。很多时候，在业务代码中，我们其实并不需要，也不应该需要 Python 提供的如此大的灵活性。

> Absolute freedom mocks at justice. Absolute justice denies freedom. To be fruitful, the two ideas must find their limits in each other.
>
> Albert Camus, The Rebel (1951)，as translated by Anthony Bower
