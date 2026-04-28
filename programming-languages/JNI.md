# JNI (Java Native Interface) & NDK

> 📖 **[View JNI Guide]** (prgramming-languages/jni.html)- Interactive HTML version

## Definition
JNI is the bridge that allows Kotlin/Java (running in ART) to call functions in native C/C++ libraries. The **NDK (Native Development Kit)** is the set of tools used to compile that C/C++ code into[...]

---
## How JNI works ?

Flow chart: 

1. **Loading the Library:** When your Kotlin code calls `System.loadLibrary("native-lib")`, the JVM uses the Android Runtime's ClassLoader to find and load the `.so` file from your app's `lib/` di[...]
2. **Linking Native Methods:** The JVM searches the native library for functions whose names match the mangled signatures of your `external` functions (e.g., `Java_com_myapp_MainActivity_sayHello`[...]
3. **Context Switch:** Once a match is found, the JVM updates its internal function table (the JNI function pointers) and creates a `JNIEnv` pointer.
4. **Execution:** Your Kotlin code executes, which triggers the jump to the C++ function. The CPU switches from the ART (ART VM) context to the Native context to execute the C++ instructions.
5. **Data Marshalling:** If you pass arguments (like Strings or Arrays), the JVM copies the data from the Java heap to the Native stack so C++ can read it.
6. **Return:** When the C++ function returns, the data is copied back (if modified), and the CPU switches back to the ART context to resume your Kotlin code.



## 🚀 Senior Level: The Deep Dive

### 1. JNIEnv and Thunks
When you call a native method, the system passes a `JNIEnv*` pointer. This is effectively a "function table" that contains all the methods needed to interact with the JVM (e.g., creating Java obje[...]
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
> I would use a `Direct ByteBuffer`. Unlike a regular Java array, a Direct ByteBuffer is allocated outside the Java heap. This allows the native C++ code to access the memory directly via a pointe[...]

---

**Q: What is the risk of not calling DeleteGlobalRef in JNI?**

**Answer:**
> It causes a native memory leak. The Java object will be held in memory indefinitely because the JNI global reference acts as a "Strong Root" for the Garbage Collector. If this happens in a loop [...]

**Q: How JNI can be used to store firebase token or sensitive data like tokens?**

**Answer:**
> While JNI itself is not a "storage" location (like SharedPreferences), it is a powerful tool for **obfuscation**. By moving sensitive strings (like API keys or Firebase salts) into the native C+[...]

> **The Security Flow:**
> 1. **Native Implementation:** Define your sensitive strings as a `const char*` or a character array in a `.cpp` file.
> 2. **String Obfuscation:** Instead of storing the plain-text string, store it as an XORed or encrypted byte array in the native code.
> 3. **Native Recovery:** Implement a C++ function that decrypts/de-obfuscates the string only in memory when requested.
> 4. **Native-to-Java Bridge:** Use a JNI function (e.g., `Java_com_myapp_NativeLib_getSecretKey`) to return the de-obfuscated string as a `jstring` to the Java/Kotlin layer.
> 5. **Library Loading:** Call `System.loadLibrary("native-lib")` in a static block in your Kotlin class and declare the function as `external`.
>
> **Senior Tip:** Even with JNI, a determined attacker can use tools like `Ghidra` or `IDA Pro` to reverse-engineer the native `.so` file. For absolute security of user-specific tokens, always pai[...]

