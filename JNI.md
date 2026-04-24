# JNI (Java Native Interface)

## Definition
JNI allows Kotlin/Java code to interact with native C/C++ code.

## 💻 Code Example

```kotlin
// Loading the library
init {
    System.loadLibrary("native-lib")
}

// Declaring the native method
external fun stringFromJNI(): String
```

## 🔍 Real-World Process: The Bridge

```text
  [ Kotlin/Java Code ]
          ↓
  [ JVM / ART ]
          ↓
  [ JNI Environment Interface ]
          ↓
  [ C++ Library (.so file) ]
          ↓
  [ Native Hardware Access ]
```

## 🧠 Core Idea
> **Why use it?** For performance-heavy tasks (video processing, 3D rendering) or using existing C++ libraries.

## 🎯 Interview-Ready Answer

**Q: Does System.loadLibrary find any file?**

**Answer:**
> No, it looks for specific naming conventions. If you load "native-lib", it looks for `libnative-lib.so` in the app's native library directories.
