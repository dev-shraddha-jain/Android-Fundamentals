# Interview QnA: Programming Languages (Kotlin & Java)

### Q1. [How Mechanism] How does Kotlin's `lazy` property work internally?
**The Mechanism:**
*   By default, `lazy` uses a `SynchronizedLazyImpl` which ensures thread safety.
*   The first thread that accesses the property enters a `synchronized` block, computes the value, and stores it.
*   Subsequent calls skip the computation and return the cached value.

**How to Answer:**
*   Mention that it is a "Delegated Property".
*   Explain the different thread-safety modes (`SYNCHRONIZED`, `PUBLICATION`, `NONE`).
*   Highlight that `lazy` is only for `val` (read-only) properties.

---

### 2. [Tricky] Why can't you use a `reified` type parameter in a regular function?
**The Reason:**
*   In the JVM, generic types are **erased** at runtime. You cannot do `T::class.java`.
*   `reified` is only possible in `inline` functions because the compiler copies the actual type into the call site during the inlining process.

**How to Answer:**
*   Start with the concept of "Type Erasure".
*   Explain that `inline` functions act as a code-copying mechanism, which is what allows the type to be "reified" (made real) at the call site.

---

### 3. [What If] What if a Kotlin Coroutine is "Cancelled" but is currently running a heavy CPU loop?
**The Scenario:**
*   The coroutine will **continue to run** unless the code explicitly checks for the cancellation status.
*   Coroutines are "Cooperative". They don't stop unless they hit a suspension point (`delay()`, `yield()`) or check `isActive`.

**How to Answer:**
*   Define cancellation as "Cooperative".
*   Suggest checking `ensureActive()` or `yield()` inside heavy loops to make them responsive to cancellation.
