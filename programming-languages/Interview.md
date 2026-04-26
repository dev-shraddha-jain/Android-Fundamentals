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


### 4. JNI Mechanism (Senior) Suppose Kotlin code calls:

```kotlin
external fun getToken(): String
```

Explain **full internal mechanism** from this Kotlin call until C/C++ code executes and returns.

Include:

* `System.loadLibrary()`
* symbol resolution
* JNI bridge
* JNIEnv
* thread attachment
* string conversion
* performance cost
* common crash reasons

**Answer**

1. App startup calls:

```kotlin
System.loadLibrary("native-lib")
```

2. ART asks linker to load `libnative-lib.so`.

3. Native library loaded into process memory.

4. Optional `JNI_OnLoad(JavaVM*)` executes for initialization and native registration.

5. Kotlin calls:

```kotlin
external fun getToken(): String
```

6. ART/JNI resolves mapped native function by:

* naming convention (`Java_pkg_Class_getToken`)
* or `RegisterNatives()`

7. Execution crosses managed ART → native C/C++ boundary.

8. Native method receives:

```cpp
JNIEnv* env, jobject thiz
```

9. Native code creates return string:

```cpp
env->NewStringUTF("abc")
```

10. ART converts JNI return object back to Java/Kotlin `String`.

### JNIEnv

* Thread-local function table.
* Used for:

  * strings
  * objects
  * exceptions
  * method calls
  * arrays

### Thread Attachment

Only needed for threads created in native side:

```cpp
vm->AttachCurrentThread(...)
```

Detach later.

### Performance Cost

* Crossing JNI boundary
* Marshaling objects/strings
* GC coordination
* Context switches between managed/native runtime semantics

### Common Crash Reasons

* Wrong signature mismatch
* Missing symbol
* Null pointer in C++
* Use-after-free
* Local reference overflow
* Thread not attached
* Returning invalid jobject
* ABI mismatch (`arm64-v8a`, `armeabi-v7a`)
* ProGuard renamed class used in manual registration

---
