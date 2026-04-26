# JNI (Java Native Interface) & NDK

## Definition
JNI is the bridge that allows Kotlin/Java (running in ART) to call functions in native C/C++ libraries. The **NDK (Native Development Kit)** is the set of tools used to compile that C/C++ code into `.so` (Shared Object) files.

---

## 🚀 Senior Level: The Deep Dive

### 1. JNIEnv and Thunks
When you call a native method, the system passes a `JNIEnv*` pointer. This is effectively a "function table" that contains all the methods needed to interact with the JVM (e.g., creating Java objects, calling methods).
> **Note:** `JNIEnv` is thread-local. You cannot pass it from one native thread to another.

### 2. Reference Management (Crucial for Memory)
JNI has its own reference system to prevent the Java GC from collecting objects while C++ is using them.
*   **Local References:** Automatically deleted when the native method returns.
*   **Global References:** Must be manually deleted using `DeleteGlobalRef`. Failure to do so leads to **Native Memory Leaks**.

### 3. Crossing the "JNI Bridge"
Calling a native method is **not free**. There is overhead in:
*   Context switching between ART and Native.
*   Marshalling data (converting Java Strings/Arrays to C types).
*   **Optimization Tip:** If you need to pass a lot of data, use a **Direct ByteBuffer**. It allows both Java and C++ to access the same memory address without copying data.

---

## 💻 Advanced Example: Threading
To call Java from a native thread, you must first **attach** the thread to the JVM.

```cpp
// Native thread function
void* myNativeThread(void* arg) {
    JNIEnv* env;
    javaVM->AttachCurrentThread(&env, NULL); // Link thread to JVM
    
    // Call Java methods here...
    
    javaVM->DetachCurrentThread(); // Clean up
    return NULL;
}
```

---

## 🎯 Interview-Ready Answer (Senior Level)

**Q: How do you pass large amounts of data between Java and Native efficiently?**

**Answer:**
> I would use a `Direct ByteBuffer`. Unlike a regular Java array, a Direct ByteBuffer is allocated outside the Java heap. This allows the native C++ code to access the memory directly via a pointer without the overhead of copying the data across the JNI bridge.

---

**Q: What is the risk of not calling DeleteGlobalRef in JNI?**

**Answer:**
> It causes a native memory leak. The Java object will be held in memory indefinitely because the JNI global reference acts as a "Strong Root" for the Garbage Collector. If this happens in a loop or a frequently called service, the app will eventually crash with an `OutOfMemoryError` or be killed by the system.
