+++
title = "Rust 中生命周期的子类型化和型变"

[taxonomies]
categories = ["Rust"]
tags = ["Rust"]
+++

众所周知，Rust 使用借用检查代替垃圾收集来进行内存管理。而为了实现借用检查，就需要为变量引入生命周期，在大多数情况下，Rust 编译器会自动决定变量的生命周期，而无需而外指定，有些情况则不然。

引用 Rust 官方文档中提供的例子：

```rust
fn main() {
    let r;                // ---------+-- 'a
                          //          |
    {                     //          |
        let x = 5;        // -+-- 'b  |
        r = &x;           //  |       |
    }                     // -+       |
                          //          |
    println!("r: {}", r); //          |
}                         // ---------+
```

```rust
fn main() {
    let x = 5;            // ----------+-- 'b
                          //           |
    let r = &x;           // --+-- 'a  |
                          //   |       |
    println!("r: {}", r); //   |       |
                          // --+       |
}                         // ----------+
```

Rust 正是像上面所示的那样利用变量生命周期避免了悬垂引用。

但是，考虑下面的函数：

```rust
fn t<'a>(a: &'a str, b: &'a str) -> (&'a str, &'a str) {
    (b, a)
}

fn main() {
    let a: &'static str = "a";
    let c: &str;
    let d: &str;
    {
        let b = &String::from("b");
        (c, d) = t(a, b);
        println!("{} {}", c, d);
    }
    // println!("{} {}", c, d);
}
```

`t` 函数要求接受两个生命周期为 `'a` 的引用，而显然，下面的传入的 `a` 的生命周期是 `'static` 而 `b` 的生命周期则短于 `'static`，两个生命周期并不一致，但程序仍然可以编译运行。除此之外，如果反注释掉最后一行，会发现编译器报错了，这表明借用检查正确生效了，编译器将 `c` 和 `d` 的生命周期推断为和较短的 `b` 相同。

这里的重点在于，为什么明明 `t` 函数要求接受两个生命周期为 `'a` 的引用，但我们传入两个生命周期不同的引用也能通过检查呢？

暂且保留这个疑问，先来介绍一下子类型。

## 子类型

在面向对象编程中，子类型是一个基础概念。

比如我们有一个 `Fruit` 类，它有 `Apple` 这个子类，那么 `Apple` 就是 `Fruit` 的子类型。

让我们更加深入一些，为什么 `Apple` 是 `Fruit` 的子类型呢？或者说，子类型到底表示两个类型之间怎样的关系？

用逻辑学的语言来说的话，就是“子类型相比其父类型内涵增加了，而外延收缩了”。

通俗的解释就是说，子类型所包含的特质属性增加了，而涵盖的具体事物范围减少了。对应上面的例子，包含的特质属性增加了是指：苹果这个概念相对于水果这个概念，它不仅包含了水果的全部属性，还包含了苹果的独特属性，比如特定的味道、特定的 DNA 片段等。涵盖的具体事物范围减少了是指：在全部能被称为水果个体中，能被称为苹果的只是一部分。

下面让我们将 `Apple` 是 `Fruit` 的子类型记为：`Apple <: Fruit`。

在编程中，当需要一个 `Fruit` 类型时，我们永远可以提供一个 `Apple` 类型……吗？

## 型变

还是从一个例子开始：

```java
class Fruit {}

class Apple extends Fruit {}

class Banana extends Fruit {}

void addApple(List<Fruit> fruits) {
    fruits.add(new Apple());
}

void test() {
    List<Banana> bananas = new ArrayList<>();
    addApple(bananas);
}
```

上面的例子，`addApple` 函数的参数是一个 `Fruit` 的列表，因此它当然可以向里面放一个苹果。下面的 `test` 函数调用了 `addApple`，因为 `addApple` 需要一个水果的列表，那我就提供一个香蕉的列表吧！Oops，在 `addApple` 之后，它就不再是一个香蕉的列表了，我们的类型系统彻底失效了。不过放心，上面的代码当然是不正确的，它是无法通过类型检查的，这里就要引出协变、逆变、不变的概念。

在此之前，类似 `List<T>` 这样的结构，我们一般称之为泛型，或者，我们也可以更加通用地将其称为“类型构造器”，你可以将它理解为一个“关于类型的函数”，它接受一个类型 `T`，返回一个新的类型。换句话说，这里的 `List<T>` 不是一个真正的类型，而是一个未完成的类型，只有填入了具体类型 `T` 之后，才是一个类型，比如 `List<Apple>`。

现在，我们讨论一下已知 `T <: U` 对于类型构造器 `I` 来说 `I<T>` 和 `I<U>` 是什么关系？

还是让我们用 `Fruit` 和 `Apple` 举例吧。

- 协变（covariance）：`I<Apple> <: I<Fruit>`
- 逆变（contravariance）：`I<Fruit> <: I<Apple>`
- 不变（invariance）：`I<Fruit>` 和 `I<Apple>` 没有关系

那么，`I` 在什么情况下会是协变、逆变和不变呢？

首先，对于最简单的情况，例如我们要做水果沙拉，因此我们需要随便一些水果 `List<Fruit>`，这时无论提供的都是苹果 `List<Apple>` 还是都是香蕉 `List<Banana>`，又或者混合水果 `List<Fruit>` 都可以。因此，它是协变的。

其次，就是上面 `addApple` 这个例子。这个函数不管接受的是什么，它只向里面添加一个苹果。这时，它希望得到的是一个 `List<Apple>` 但我们却可以安全地提供一个 `List<Fruit>`。因此，它是逆变的。

看出差别了吗？

规律就是，当一个容器类型只读时，他就是协变的，当一个容器类型只写时，他就是逆变的。

而当它既可读又可写时，他就是不变的，也就是说我们无法假定任何他们的关系，否则就可能出错。因此对于类型构造器 `List<T>` 来说，它实际上是不变的。

举一个例子，对于只读容器 `ReadOnly<T>`，如果我希望能从中读取到一个 `Fruit`，那么给我给一个 `ReadOnly<Apple>`，我一定可以读到一个 `Apple`，而 `Apple` 是一个 `Fruit`，所以是可以的。对于只写容器 `WriteOnly<T>`，如果我希望向里面添加一个 `Apple`，那么给我一个 `WriteOnly<Fruit>`，我可以安全地向里面添加一个苹果，因为一个 `Apple` 一定是一个 `Fruit`。

除此之外还存在一种特殊的类型，函数类型。

考虑最简单的一元函数，即接受一个 `T` 类型的参数，返回一个 `U` 类型的结果，记为 `T -> U`，其中 `T` 是逆变，`U` 是协变的。

返回值 `U` 是协变的，因为当我需要一个返回任意水果的函数时，当然可以给我一个返回苹果的函数。

而参数 `T` 是逆变的，因为当我需要一个能够处理苹果的函数时，也可以给我一个更加通用的能够处理任意水果的函数。

## 生命周期的子类型化

上面我们讨论了面向对象的程序设计中的子类型和型变，可是，Rust 是没有继承的，也就没有子类型。所以它和 Rust 有什么关系呢？

Rust 虽然没有类型系统的继承，但是，它是有生命周期的。生命周期一样有子类型和型变。

子类型只是一种关系，而 Rust 的生命周期是平行于类型系统的另一种变量的属性，它一样也有子类型的关系。

然而，比较反直觉的是，在 Rust 中，大的生命周期是小的生命周期的子类型，即 `'static <: 'big <: small`，与 OOP 中 `Object` 是所有类型的父类型相反，`'static` 是所有生命周期的子类型。

我们可以这样理解，当我们需要读取一个 `'small` 生命周期的变量时，提供一个 `'big` 生命周期的变量通常是可以的，也就是说，通常，我们可以将 `'big` 生命周期视为 `'small` 生命周期处理，收窄生命周期是安全的，反之，如果我们将 `'small` 当作 `'big` 则会导致内存不安全。这和我们在读取时可以将 `Apple` 当作 `Fruit` 是类似的。而对于 `'static` 来说，当需要任意一个生命周期时，我们都可以安全的提供一个 `'static`，就好像在 OOP 中存在一个所有类型的子类型，无论需要什么类型都可以提供这个类型。

## Rust 中的型变

根据 [The Rustonomicon](https://doc.rust-lang.org/nomicon/subtyping.html) 里面的表格。

|                 |  'a  |    T     |  U   |
| --------------- | :--: | :------: | :--: |
| `&'a T`         | 协变 |   协变   |      |
| `&'a mut T`     | 协变 |   不变   |      |
| `Box<T>`        |      |   协变   |      |
| `Vec<T>`        |      |   协变   |      |
| `UnsafeCell<T>` |      |   不变   |      |
| `Cell<T>`       |      |   不变   |      |
| `fn(T) -> U`    |      | **逆变** | 协变 |
| `*const T`      |      |   协变   |      |
| `*mut T`        |      |   不变   |      |

让我们来逐条分析一下：

- `&'a T` 对 `'a` 和 `T` 协变，这是因为 `&` 是一个只读容器。
- `&'a mut T` 对 `'a` 协变，对 `T` 不变。对 `T` 不变很好理解，因为 `&mut` 是可读写容器，就像前面例子里的 `List<T>` 一样。对 `'a` 协变是因为，和类型系统的子类型不同，生命周期不存在读取和写入和区别，它只是指示了变量何时可用，当变量不可用时，即不能读取，也不能写入。所以可以将生命周期视为类型系统里的读取关系，所以它一直是协变的。
- `Box<T>` 和 `Vec<T>` 对 `T` 协变，这放在其他语言里是不可能的，但是在 Rust 中，如果当前拥有着一个容器的所有权时，可以保证一定没有其他人能够读取和修改它。
- `UnsafeCell<T>` 和 `Cell<T>` 是用来实现内部可变性的，因此它是可读写容器，对 `T` 不变。
- `fn(T) -> U` 函数类型和前面的函数类型是一样的，特别的是，这里的对函数参数 `T` 逆变是 Rust 中唯一的逆变。
- `*const T` / `*mut T` 和 `&'a T` / `&'a mut T` 类似，这里就不再赘述。

最后，引用 _The Rustonomicon_ 中的例子，稍作修改：

```rust
fn assign<T>(input: &mut T, val: T) {
    *input = val;
}

fn main() {
    let mut hello: &'static str = "hello";
    {
        let world: &str = &String::from("world"); // &'world str
        assign(&mut hello, world);
    }
    println!("{hello}");
}
```

很明显，这里是不安全的，无法通过编译，在最后的 `println!()` 处 `world` 已经被释放了。

这里的问题在于，调用 `assign` 时，我们传入的两个类型是 `&mut &'static str` 和 `&'world str`，根据 `&'a T` 对 `'a` 协变，所以 `&'static str` 是 `&'world str` 的子类型。但是 `&'a mut T` 对 `T` 不变，所以这里，编译器不能对它做任何子类型化，因此，按照函数声明中的要求，`val` 参数的 `T` 和 `&mut T` 中的 `T` 必须“完全相同”，而这里 `val` 中的 `T` 是 `&'world str`，不是 `&'static str`，所以生命周期检查失败了。

如果修改成这样就可以通过检查了：

```rust
fn assign<T>(input: &mut T, val: T) {
    *input = val;
}

fn main() {
    let hello: &'static str = "hello";
    {
        let mut world: &str = &String::from("world"); // &'world str
        assign(&mut world, hello);
    }
}
```

我们传入的两个类型是 `&mut &'world str` 和 `&'static str`，同样，要求 `val` 中的 `T` 和 `&mut T` 中的 `T` 完全相同，可是这里传入的也不相同啊？这涉及到了 Rust 的类型自动强转机制，“在函数传参时，实参将自动转换为形参”，允许转换的规则中有一条“子类型可以转换为父类型”，虽然 `&mut` 无法进行子类型化，但 `&'static str` 是 `&'world str` 的子类型，`&'static str` 被自动强转为 `&'world str`，因此通过了生命周期检查。上面的例子，则无法进行上述的自动强转，所以生命周期检查失败了。

## 参考

- [Subtyping and Variance - The Rustonomicon](https://doc.rust-lang.org/nomicon/subtyping.html) （[中文翻译](https://nomicon.purewhite.io/subtyping.html)）
- [Subtyping and Variance - The Rust Reference](https://doc.rust-lang.org/reference/subtyping.html) （[中文翻译](https://rustwiki.org/zh-CN/reference/subtyping.html)）
- [Type coercions - The Rust Reference](https://doc.rust-lang.org/reference/type-coercions.html) （[中文翻译](https://rustwiki.org/zh-CN/reference/type-coercions.html)）
- [逆变、协变与子类型，以及 Rust](https://ioover.net/dev/variance-and-subtyping/)
