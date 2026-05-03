# ⚙️ ART (Android Runtime) Internals

ART is the "engine" that executes your code. Understanding its evolution from Dalvik to modern ART is key for performance optimization.

---

### 1. Compilation Strategies
Android has used three main ways to run code:
1.  **JIT (Just-In-Time) - Dalvik:** Compiled code to machine code *while* the app was running. Fast installation, but slow app performance and high CPU/Battery usage.
2.  **AOT (Ahead-Of-Time) - ART (Android 5.0):** Compiled the entire app to machine code during *installation*. Fast app performance, but extremely slow installation and high storage usage.
3.  **Modern ART (Android 7.0+):** A hybrid approach.
    *   **Initial:** App runs via JIT/Interpreter.
    *   **Profiling:** ART records which methods are called most frequently (the "hot" code).
    *   **Idle Compilation:** When the phone is charging and idle, ART uses **dex2oat** to compile only the hot code into machine code (AOT).

---

### 2. Profile-Guided Optimization (PGO) & Cloud Profiles
To avoid the "slow first run" of the hybrid approach, Google introduced **Cloud Profiles**:
*   When users run an app, their "hot code profiles" are uploaded to Google Play.
*   New users download these profiles along with the app.
*   ART uses the profile to AOT-compile the most important parts of the app *before* the first launch.

---

### 3. Garbage Collection (GC) in ART
GC is the most common cause of "jank" (skipped frames). ART uses several optimized algorithms:
*   **CMS (Concurrent Mark-Sweep):** Minimizes "Stop-the-World" pauses by doing most of the work while the app threads are still running.
*   **Compacting GC:** Over time, memory gets fragmented. ART can move objects around to consolidate free space (Semi-space or Generational GC).
*   **Generational GC (Android 10+):** Based on the observation that "most objects die young." It focuses on cleaning up newly created objects more frequently, which is much faster.

---

### 4. Memory Regions
*   **Zygote Space:** Contains preloaded classes and resources shared by all apps.
*   **App Heap:** The private memory for your app's objects.
*   **Large Object Space (LOS):** For large allocations like Bitmaps, to prevent fragmentation in the main heap.

---

### 🎯 Interview QnA

#### Q: What is a "Stop-the-World" pause?
**Answer:**
It's a phase during Garbage Collection where all application threads are paused so the GC can safely move objects or update references. If this pause exceeds 16ms, the app will skip a frame, leading to visible stutter (jank). Modern ART reduces these pauses to a few milliseconds.

#### Q: How can you reduce GC pressure in your app?
**Answer:**
1.  **Avoid object churn:** Don't create many short-lived objects inside loops or `onDraw()` methods.
2.  **Use primitives:** Use `IntArray` instead of `Array<Int>` to avoid boxing/unboxing.
3.  **Object Pooling:** For frequently used objects (like database cursor wrappers), reuse instances instead of creating new ones.

#### Q: What is the purpose of the `dex2oat` tool?
**Answer:**
`dex2oat` is the compiler that transforms `.dex` files (Dalvik Executable) into `.oat` files (ELF machine code). It is the core of the AOT compilation process in Android.
