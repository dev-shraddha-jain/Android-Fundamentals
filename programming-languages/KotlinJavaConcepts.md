# Java Concepts (Beginner to Advanced)

## 🟢 Beginner: Core Basics

Java is an object-oriented, class-based language. In Android, it was the primary language before Kotlin.

- **OOP Principles:** Encapsulation, Inheritance, Polymorphism, and Abstraction.
- **Collections Framework:** List (ArrayList), Set (HashSet), Map (HashMap).
- **Static vs Instance:** `static` members belong to the class, not an object instance.

---

## 🟡 Intermediate: The "Why"

- **Generics & Wildcards:** Java uses `? extends T` (Upper Bound) and `? super T` (Lower Bound).
  - _PECS Rule:_ Producer Extends, Consumer Super.
- **Exception Handling:** Checked vs. Unchecked exceptions. (Android handles `UncaughtExceptionHandler` for crashes).
- **Annotations:** Used heavily in libraries like Retrofit or Room (`@Query`, `@Entity`).

---

## 🔴 Advanced: Under the Hood

### 1. JVM Architecture

The Java Virtual Machine (JVM) consists of:

- **ClassLoader:** Loads `.class` files.
- **Runtime Data Areas:**
  - **Stack:** Stores local variables and method calls (Thread-specific).
  - **Heap:** Stores all objects (Shared across threads).
- **Execution Engine:** JIT Compiler and Garbage Collector.

### 2. Memory Management & Reference Types

How the Garbage Collector (GC) decides what to kill:

- **Strong Reference:** Default. Object won't be GC'd as long as the ref exists.
- **Weak Reference:** GC will collect it immediately during the next cycle if no strong refs exist. (Crucial for avoiding Memory Leaks in `Handlers` or `Contexts`).
- **Soft Reference:** GC only collects it if the system is low on memory.

### 3. Reflection

The ability to inspect or modify classes at runtime.

> **Senior Note:** Reflection is powerful but slow. Dependency Injection libraries like Dagger used to use reflection but moved to **Annotation Processing** (code generation) for better performance.

---

## 🎯 Interview-Ready Answer (Senior)

**Q: Explain the difference between JVM, DVM, and ART.**

**Answer:**

> **JVM** is the standard Java machine. **DVM (Dalvik Virtual Machine)** was built for older Android; it used register-based architecture and JIT. **ART (Android Runtime)** is the modern successor; it uses **AOT (Ahead-of-Time)** compilation to compile DEX into native machine code during installation, making apps launch faster and perform better.
# Kotlin Concepts (Beginner to Advanced)

## 🟢 Beginner: Modern Basics

Kotlin is designed to be expressive and safe.

- **Null Safety:** `String?` vs `String`. The compiler forces you to handle `null`.
- **Conciseness:** No semicolons, Type inference (`val x = 10`), and String templates (`"Hello $name"`).
- **Val vs Var:** `val` is immutable (read-only), `var` is mutable.

---

## 🟡 Intermediate: Functional Power

- **Extension Functions:** `fun View.hide() { this.visibility = View.GONE }`.
- **Higher-Order Functions:** Functions that take other functions as parameters.
- **Scope Functions:** `let`, `run`, `with`, `apply`, `also`.
  - _Apply:_ Used for object configuration.
  - _Let:_ Used for null checks and mapping.
- **Data Classes:** One-line classes for data storage.

---

## 🔴 Advanced: Performance & Concurrency

### 1. Inline, Noinline, Crossinline

- **`inline`**: Copies code to the call site to save memory from lambda object creation.
- **`noinline`**: Prevents a specific lambda in an inline function from being inlined.
- **`crossinline`**: Prevents a lambda from using `return` (non-local return).

### 2. Coroutines & Flow

- **Coroutines:** Asynchronous code that looks synchronous.
- **Flow (Cold):** Only emits values when collected (e.g., Database stream).
- **StateFlow/SharedFlow (Hot):** Emits values even if no one is listening (e.g., UI State).

### 3. Delegation

- **Class Delegation:** `class MyList : List<Int> by ArrayList()`.
- **Property Delegation:** `val name by lazy { ... }`.

### 4. Generics Variance

- **`out T` (Covariance):** Producer only. Safe to go from `List<String>` to `List<Any>`.
- **`in T` (Contravariance):** Consumer only.

---

## 🎨 Interactive Coroutine Visualization

Check out the tool below to understand Structured Concurrency:

<iframe src="./coroutines_visualization.html" width="100%" height="500px" style="border:none; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);"></iframe>

---

## 🎯 Interview-Ready Answer (Senior)

**Q: What is a "Reified" type and why is it only possible with "inline"?**

**Answer:**

> Normally, generics are **erased** at runtime (you don't know what `T` is). By using `inline`, the compiler copies the actual type into the call site. Marking it `reified` allows the code to access the type at runtime (e.g., `T::class.java`), which is impossible in Java.
# Java & Kotlin Interoperability

## 🔍 The Bridge

Since both Java and Kotlin compile to the same **JVM Bytecode**, they can exist in the same project and call each other seamlessly.

### 1. Calling Java from Kotlin

- **Properties:** Java getters/setters (`getName()`, `setName()`) are accessed as properties (`user.name`).
- **Platform Types:** Java types are seen as `T!` (could be null or not). Kotlin doesn't enforce null checks here unless you add `@Nullable` or `@NotNull` in Java.

### 2. Calling Kotlin from Java (The "Jvm" Annotations)

Kotlin generates code that looks natural to Java using these annotations:

| Annotation          | Purpose                                                   | Result in Java               |
| :------------------ | :-------------------------------------------------------- | :--------------------------- |
| **`@JvmStatic`**    | Makes a member of an `object` a real static method.       | `MyObject.method()`          |
| **`@JvmOverloads`** | Generates multiple Java methods for default parameters.   | Multiple overloaded methods. |
| **`@JvmField`**     | Exposes a property as a public field instead of a getter. | `myObject.field`             |
| **`@JvmName`**      | Changes the name of the generated Java class or method.   | `UtilsKt` becomes `MyUtils`. |

## 🧠 Real-World Scenario: Migration

Most companies migrate by converting one file at a time.

1.  **Step 1:** Convert Data Models to Kotlin (Data Classes).
2.  **Step 2:** Convert Utility classes.
3.  **Step 3:** Convert Activities/Fragments.

> **Pro Tip:** Keep your internal APIs in Kotlin but use `@JvmStatic` and `@JvmOverloads` if you still have Java consumers to keep their code clean.

---

## 🎯 Interview-Ready Answer (Senior)

**Q: What is a "Platform Type" and how do you handle it?**

**Answer:**

> A Platform Type is a type that comes from Java code where nullability is not specified (no `@Nullable` or `@NonNull` annotation). In Kotlin, it is represented with an exclamation mark (e.g., `String!`). You should handle it cautiously by checking for null or, better yet, by adding proper annotations to the Java source code so Kotlin can treat it as a safe non-nullable or nullable type.
