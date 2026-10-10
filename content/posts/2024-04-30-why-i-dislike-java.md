+++
title = "为什么我不喜欢 Java"

[taxonomies]
categories = ["Programming Languages"]
tags = ["Java", "Programming Languages"]
+++

我知道有很多人很喜欢 Java，也知道 Java 的生态非常庞大，JVM 本身更是一个相当优秀的工程。但是，我还是忍不住要吐槽：这个语言实在是太丑了。尤其是当我必须把一些用 Kotlin 写的代码手工翻译成 Java 时，每写下一行都感到内心的煎熬。

这里面既有语言设计的问题，也有历史兼容性的妥协，还有一些只是我的个人偏好。下面，就让我细数一下 Java 的“罪恶”。

## 类型擦除

首先是类型擦除，这已经是一个老生常谈的问题了。Java 的泛型主要提供编译期检查，编译后类型参数会被[擦除](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html)，替换为其上界，没有显式上界时则是 `Object`。

这意味着，`List<String>` 和 `List<Integer>` 在运行时并不是两个不同的类。再加上为了兼容旧代码而保留的原始类型（raw type），我们就可以写出这样的代码：

```java
List<String> strings = new ArrayList<>();
strings.add("Hello");

List raw = strings;
raw.add(42); // 编译器会给出 unchecked 警告，但仍然允许编译

System.out.println(strings); // [Hello, 42]
String value = strings.get(1); // ClassCastException
```

明明声明了一个字符串列表，却可以通过原始类型向里面放入整数，而且错误要等到取出元素时才暴露。编译器会给出警告，但作为一个所谓的静态类型语言，这种绕过泛型检查的入口不应该如此容易被使用。

类型擦除还会影响那些需要在运行时获取类型的场景。比如，用 Gson 将 JSON 解析成一个泛型类型，就不能简单地传入 `List<String>.class`，而需要用下面这种繁琐的写法：

```java
Gson gson = new Gson();
Type listType = new TypeToken<List<String>>() {}.getType();
List<String> strings = gson.fromJson("[\"Hello\", \"world\"]", listType);
```

类型擦除作为一个编译器的实现方式并没有什么问题，比如 Haskell 同样会进行类型擦除，但是，搭配上 Java 的原始类型和反射机制，就很容易导致运行时错误和繁琐的代码。

## 数组协变

如果说上面的原始类型至少还会触发编译器警告，那么数组的设计就更让我难以理解了：

```java
String[] strings = {"Hello"};
Object[] objects = strings;
objects[0] = 42; // ArrayStoreException
```

这段代码不需要强制类型转换，也没有 unchecked 警告，却会在运行时抛出异常。

原因是 Java 的数组支持协变：`String` 是 `Object` 的子类型，`String[]` 也就被视为 `Object[]` 的子类型。但把一个字符串数组当成对象数组使用之后，我们就可以向它写入整数，而实际的数组又只能容纳字符串。为了避免破坏数组的类型约束，JVM 只好在写入时进行[运行时检查](https://docs.oracle.com/javase/specs/jls/se21/html/jls-10.html#jls-10.5)。

如果是只读容器，协变是很自然的。但对于同时支持读取和写入的容器，这种转换并不安全。Java 的泛型集合在这方面反而做出了正确的限制，`List<String>` 不能直接赋值给 `List<Object>`。于是，同样是存储一组元素，数组和泛型集合却有两套不同的规则。

## 反射和字节码增强

我一直觉得 Java 生态有一点太过于依赖反射、动态代理和字节码增强了。在 Spring 的依赖注入、ORM、JSON 库的对象绑定等场景中，经常可以看到这些机制。

它们确实很方便：只需要在类上添加几个注解，框架就能在运行时扫描类、读取字段、创建对象，再把它们组装起来。但是，其中很多信息在编译时就已经确定了，为什么还要等到程序启动之后再来发现呢？

比如，一个依赖关系固定的对象，如果漏掉了它需要的依赖，我希望在编译时就得到错误，而不是等到应用启动时才看到一大串异常。序列化一个结构已知的类，也完全可以提前生成相应的代码，不必在运行时逐个发现它的字段。

Java 并非完全没有编译时代码生成能力，比如[注解处理器](https://docs.oracle.com/en/java/javase/21/docs/api/java.compiler/javax/annotation/processing/Processor.html)。但相比 Rust 的过程宏、Go 和 Dart 生态中常用的静态代码生成等机制，Java 在这方面的表达能力和使用体验仍然非常受限，很多事情最终还是交给框架在运行时完成。

这并不是说 Java 不应该具有这些动态特性。Java 运行在虚拟机上，又拥有稳定的字节码规范，理所当然地可以支持这些很有用的能力。在 APM 和 IAST 的动态插桩、运行时加载插件、热替换模块等场景中，我们本来就需要在程序运行后改变它的行为。

但如果一个功能并不需要运行时的灵活性，我更希望它能在编译时完成。这不只是性能问题，更重要的是错误出现的时机以及代码是否容易理解和调试。相比一个只有启动后才能确定的对象关系，可以直接检查、可以被编译器静态验证的代码明显更加安全和易用。

## 面向对象

Java 对 OOP 过于“尊崇”了，很多本来可以独立表达的东西，都要先套上一层类或者接口。

比如，Java 虽然支持 lambda 表达式，但并没有独立的函数类型，lambda 必须依附于一个函数式接口。标准库提供了 `Function`、`Consumer`、`Supplier` 等接口，普通的情况还算方便，但如果我希望定义一个会抛出受检异常（checked exception）的闭包，`Function` 的 `apply` 方法就无法直接表达这个要求。

于是，我还需要先定义一个接口：

```java
@FunctionalInterface
interface ThrowingFunction<T, R, E extends Exception> {
    R apply(T value) throws E;
}
```

然后再用 lambda 表达式实现它：

```java
ThrowingFunction<Boolean, String, IOException> foo = ok -> {
    if (!ok) {
        throw new IOException("Not OK");
    }
    return "Hello world!";
};
```

调用的时候则需要使用 `foo.apply(true)`，并处理或声明 `IOException`。

在 Kotlin 中，同样的逻辑可以直接写成：

```kotlin
val foo: (Boolean) -> String = { ok ->
    if (!ok) {
        throw IOException("Not OK")
    }
    "Hello world!"
}
```

然后用 `foo(true)` 调用即可。

更何况 Java 对面向对象的坚持也并未一以贯之。比如，存在所谓的基本类型（Primitive Data Types）和包装类（Wrapper Classes），`int` 和 `Integer`、`boolean` 和 `Boolean` 等。

在 JVM 层保留基本类型有性能上的考虑，但这并不意味着语言层面一定要暴露两套不同的用法。Kotlin 同样运行在 JVM 上，却可以在语言层面统一使用 `Int`，再根据场景编译为基本类型或者装箱类型。这不会让装箱开销消失，但至少不必把底层表示的差异全部交给开发者处理。

## 受检异常

前面的闭包例子还涉及另一个问题：受检异常。

受检异常的出发点其实是好的，一个方法可能发生某种错误，就应该在接口中声明，并要求调用者处理或者继续向上传播。但是，Java 的受检异常与泛型、函数式接口组合起来，使用体验就非常糟糕了。

比如，假设 `paths` 是一个 `List<Path>`，我希望读取这些路径对应的文件，很自然地会写出：

```java
List<String> contents = paths.stream()
    .map(Files::readString) // 编译错误：未处理 IOException
    .toList();
```

`Files.readString()` 会抛出 `IOException`，但 `map()` 接受的 `Function` 接口并没有声明这个异常。即使在外层方法上添加 `throws IOException` 也没有用，因为方法引用本身就无法满足这个接口的要求。

于是，一个本来非常简单的操作就需要写成：

```java
List<String> contents = paths.stream()
    .map(path -> {
        try {
            return Files.readString(path);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    })
    .toList();
```

为了接入标准库的接口，我们把一个需要静态检查的受检异常包装成了无法静态检查的非受检异常。代码变得更啰嗦了，原本的检查也被绕过去了。当然，也可以放弃 Stream，改用普通循环，但这又意味着同一个操作能不能方便地组合取决于它会不会抛出受检异常。

Kotlin 直接放弃了对受检异常的强制检查，所以前面的 Kotlin 闭包也没有提供与 Java 相同的异常检查。相比之下，我更喜欢 Rust 的 `Result<T, E>`，把成功和失败都表示为普通的值，既可以在类型中声明错误，又可以通过 `map()`、`and_then()` 等方法组合操作，传播错误时还有 `?` 可以使用。

我不反对要求开发者明确处理错误，但语言既然提出了这个要求，就应该提供方便、一致的表达方式，而不是让受检异常在很多场景中变成一个需要想办法绕过的障碍。

## 运算符重载和属性

Java 不支持自定义运算符重载，也没有 Kotlin 和 C# 那样的属性语法。这两点本身都可以理解为语言设计中对明确性和灵活性的取舍，但我并不喜欢这种取舍。

尤其是属性。Java 社区通常建议按照封装的要求隐藏字段，通过 getter/setter 方法访问和修改状态。但语言又不提供对应的语法，于是就需要手动编写大量 `getXXX()` 和 `setXXX()` 方法，或者使用 Lombok 之类的工具生成。

即使生成这些方法不需要自己动手，调用时的代码依然很啰嗦：

```java
person.getAddress().setCity("Shanghai");
```

对比 Kotlin：

```kotlin
person.address.city = "Shanghai"
```

后者明显更容易阅读。而且它并不意味着直接暴露字段，属性背后仍然可以有自定义的 getter/setter，进行计算或者校验。封装和简洁的访问语法完全可以同时存在。

运算符重载也类似。比如，使用 `BigDecimal` 时，简单的算术表达式也需要写成一串 `add()`、`multiply()` 调用。滥用运算符重载会让代码难以理解，但对于本来就具有明确数学含义的类型，高级语言应该允许它们使用更自然的表达方式。

## 空安全

我真的很讨厌拿到一个对象之后，还需要先判断它是否为空。只看一个返回引用类型的方法签名，我几乎永远无法肯定它到底会不会返回 `null`。

比如：

```java
User findUser(long id);
```

如果用户不存在，它会返回 `null`，还是抛出异常？返回的 `User` 中，哪些字段又可能为空？这些信息需要靠文档、注解或者阅读实现来补充，类型本身并没有告诉我。

而 Kotlin 等几乎所有现代语言（除了在这方面同样很糟糕的 Go）都可以通过类似 `User` 和 `User?` 的语法区分这两种情况。比如，取一个可能为空的用户名，并提供默认值，可以写成：

```kotlin
val name = user?.name ?: "Anonymous"
```

Java 当然也有补救方案，比如 `Optional<T>`，以及各种 `@NotNull`、`@Nullable` 注解。这些注解配合 IDE 或静态检查工具，也可以发现一些问题。但 `Optional<T>` 的语法非常啰嗦和难用，`@NotNull`、`@Nullable` 注解也并非 Java 语言本身提供可空类型规则，检查效果取决于项目选择了哪些注解、启用了哪些工具，以及第三方库是否提供了足够的信息。

如果一个约束能够由类型系统表达，那么它应该直接成为接口的一部分，并由工具强制检查，而不是每次都依赖开发者记得遵守。

## 集合的可变性

除了空安全，集合能不能被修改，同样是一个应该由类型表达的约束。但 Java 的集合接口在这方面做的也不好：

```java
List<String> names = List.of("Alice");
names.add("Bob"); // UnsupportedOperationException
```

`List.of()` 创建的是不可修改的列表，但它返回的类型仍然是 `List<String>`，仍然暴露了 `add()`、`remove()`、`set()` 这些修改方法。编译器允许调用，等到运行时再告诉我这个操作不支持。

这是 Java 标准库明确的设计，修改集合的方法是[可选操作](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html)。也就是说，当一个方法返回 `List<String>` 时，只看类型，我们根本无法知道它支持哪些修改操作，需要查文档或者看它的具体实现。

虽然不像 Rust 提供了严格的统一可变性语义，Kotlin 至少在接口层面区分了只读的 `List<T>` 和可修改的 `MutableList<T>`。如果一个函数只需要读取列表，就可以接受 `List<T>`，调用者也可以从类型中知道它没有进行修改列表的操作。

## 向后兼容？

说到这里，很多问题最终都会得到同一个解释：为了向后兼容。泛型的类型擦除和原始类型，就是 Java 在引入新特性时为了兼容已有代码而作出的妥协。

我理解兼容性对于 Java 生态的重要性。一个维护了很多年的系统，能够升级工具链而不必重写大量业务代码，这当然是很有价值的。语言也应该尽可能避免破坏性的变更，Python 2 到 Python 3 的阵痛已经足够说明问题。

但是，“向后兼容”也需要区分源码兼容、二进制兼容和行为兼容，绝对的向后兼容是不可能的，新增关键字可能影响已有的标识符、Java 许多库都有很严格的 JDK 版本限制、任何一个实际的项目升级 JDK 版本也都是一个大工程。

保留下来的错误设计不会只影响旧代码，它们也会继续影响今天新写的每一行代码。如果所有历史选择都必须原样保留，那么语言就很难修正自己的不一致性。语法变更并不是不可接受的，只要存在合理的迁移路径即可，一个比较好的例子是 Rust 的 [edition](https://doc.rust-lang.org/edition-guide/) 设计：一个 crate 可以明确选择自己的 edition，旧代码继续使用旧规则，不同 edition 的 crate 仍然可以互相依赖，而迁移工具则帮助开发者完成大部分机械修改。

Java 的很多设计都有其历史原因，但理解这些原因并不会让我在写代码时感到更舒服。
