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
