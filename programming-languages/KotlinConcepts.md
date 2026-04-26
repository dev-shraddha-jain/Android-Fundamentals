# Kotlin Concepts (Beginner to Advanced)

## 🟢 Beginner: Modern Basics
Kotlin is designed to be expressive and safe.

*   **Null Safety:** `String?` vs `String`. The compiler forces you to handle `null`.
*   **Conciseness:** No semicolons, Type inference (`val x = 10`), and String templates (`"Hello $name"`).
*   **Val vs Var:** `val` is immutable (read-only), `var` is mutable.

---

## 🟡 Intermediate: Functional Power
*   **Extension Functions:** `fun View.hide() { this.visibility = View.GONE }`.
*   **Higher-Order Functions:** Functions that take other functions as parameters.
*   **Scope Functions:** `let`, `run`, `with`, `apply`, `also`. 
    *   *Apply:* Used for object configuration.
    *   *Let:* Used for null checks and mapping.
*   **Data Classes:** One-line classes for data storage.

---

## 🔴 Advanced: Performance & Concurrency
### 1. Inline, Noinline, Crossinline
*   **`inline`**: Copies code to the call site to save memory from lambda object creation.
*   **`noinline`**: Prevents a specific lambda in an inline function from being inlined.
*   **`crossinline`**: Prevents a lambda from using `return` (non-local return).

### 2. Coroutines & Flow
*   **Coroutines:** Asynchronous code that looks synchronous. 
*   **Flow (Cold):** Only emits values when collected (e.g., Database stream).
*   **StateFlow/SharedFlow (Hot):** Emits values even if no one is listening (e.g., UI State).

### 3. Delegation
*   **Class Delegation:** `class MyList : List<Int> by ArrayList()`.
*   **Property Delegation:** `val name by lazy { ... }`.

### 4. Generics Variance
*   **`out T` (Covariance):** Producer only. Safe to go from `List<String>` to `List<Any>`.
*   **`in T` (Contravariance):** Consumer only.

---

## 🎨 Interactive Coroutine Visualization
Check out the tool below to understand Structured Concurrency:

<iframe src="./coroutines_visualization.html" width="100%" height="500px" style="border:none; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);"></iframe>

---

## 🎯 Interview-Ready Answer (Senior)

**Q: What is a "Reified" type and why is it only possible with "inline"?**

**Answer:**
> Normally, generics are **erased** at runtime (you don't know what `T` is). By using `inline`, the compiler copies the actual type into the call site. Marking it `reified` allows the code to access the type at runtime (e.g., `T::class.java`), which is impossible in Java.
