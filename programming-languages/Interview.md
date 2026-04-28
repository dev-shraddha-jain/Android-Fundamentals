# Interview QnA: Programming Languages (Kotlin & Java)

### Q1. How does Kotlin's `lazy` property work internally?
**Answer:**
*   `lazy` is a **delegated property**. It wraps a lambda that is only invoked on the first access.
*   By default, it uses `SynchronizedLazyImpl` — on first access, the calling thread acquires a lock, executes the lambda, stores the result, and releases the lock.
*   Subsequent accesses return the cached value immediately, bypassing the lock entirely.
*   Only works on `val` (read-only). Three modes: `SYNCHRONIZED` (default, thread-safe), `PUBLICATION` (safe for multiple threads to initialize, first one wins), `NONE` (no thread safety, fastest).

---

### Q2. Why can't you use a `reified` type parameter in a regular function?
**Answer:**
*   The JVM uses **Type Erasure** — generic type parameters are removed at compile time. At runtime, `List<String>` and `List<Int>` are both just `List`. You cannot call `T::class.java` in a regular generic function.
*   `reified` works **only in `inline` functions** because the Kotlin compiler copies the entire function body into every call site. At each call site, the actual type is known at compile time, so the compiler substitutes it directly — the type is "reified" (made real).
*   Practical use: `inline fun <reified T> Gson.fromJson(json: String): T = fromJson(json, T::class.java)`.

---

### Q3. What if a Kotlin Coroutine is cancelled but is running a heavy CPU loop?
**Answer:**
*   The coroutine will **keep running** — it does NOT stop automatically.
*   Kotlin coroutine cancellation is **cooperative**. A coroutine is only cancelled when it reaches a **suspension point** (`delay()`, `yield()`, any `suspend` function that checks the job).
*   A tight CPU loop with no suspension points is completely blind to cancellation.
*   **Fix:** Add `ensureActive()` or `yield()` calls periodically inside the loop. `ensureActive()` throws `CancellationException` if the job is cancelled. `yield()` also suspends briefly, letting other coroutines run.

---

### Q4. How does JNI work under the hood when a Kotlin `external fun` is called?
**Answer:**
*   **Library Load:** At startup, `System.loadLibrary("native-lib")` instructs ART's linker to load `libnative-lib.so` into the process memory.
*   **Symbol Resolution:** ART maps the Kotlin `external fun getToken()` to a C++ function either by name convention (`Java_com_example_MyClass_getToken`) or via an explicit `RegisterNatives()` call in `JNI_OnLoad`.
*   **Boundary Crossing:** When called, execution leaves the **managed ART heap** and enters native memory. The C++ function receives `JNIEnv*` (a thread-local table of JNI helper functions) and `jobject thiz` (the calling Java object).
*   **Type Marshaling:** Native code must use `JNIEnv` to convert between C++ and Java types (e.g., `env->NewStringUTF("result")` creates a Java `String`).
*   **Return:** ART converts the returned JNI type back into the Kotlin `String`.
*   **Performance cost:** Every boundary crossing involves object marshaling, GC coordination, and context switch overhead — minimize JNI call frequency.
*   **Common crashes:** ABI mismatch (`arm64-v8a` vs `armeabi-v7a`), missing symbols, native thread not attached (`AttachCurrentThread`), ProGuard renaming the class used in manual `RegisterNatives`.
