# 🔍 Performance Profiling: The Scientific Approach

Don't guess—measure. Android Studio provides a powerful suite of profilers to identify bottlenecks in your app.

---

### 1. Memory Profiler (Finding Leaks)
**The Goal:** Identify memory leaks and reduce "Object Churn."
*   **Heap Dump:** Capture a snapshot of all objects in memory. Use the "Leak Hunter" tool to find Activities that were destroyed but still held in memory.
*   **Common Leak Causes:**
    *   Static references to Context/Activity.
    *   Unregistered Listeners/BroadcastReceivers.
    *   Inner classes in Activities (like a `Handler` or `Thread`) that hold an implicit reference to the outer class.
    *   Coroutines started in a scope that isn't cancelled.

---

### 2. CPU Profiler (Finding Jank)
**The Goal:** Identify why frames are being skipped (jank).
*   **System Trace (Perfetto):** View detailed information about the kernel, system services, and app threads. Look for long "Wall Duration" on the Main thread.
*   **Choreographer:** Look for `doFrame` calls. If they take longer than 16ms, you are dropping frames.
*   **Main Thread Blocking:** Identify tasks like JSON parsing, Database queries, or heavy loops that should be moved to background threads.

---

### 3. Network Profiler
**The Goal:** Optimize data usage and battery consumption.
*   **Payload Size:** Are you downloading too much data? Use Gzip or Brotli compression.
*   **Frequency:** Group multiple small requests into one large request to reduce the time the radio stays in the "High Power" state.
*   **Caching:** Ensure your server returns correct Cache-Control headers so OkHttp can avoid redundant network calls.

---

### 4. Layout Inspector (UI Performance)
**The Goal:** Simplify the View hierarchy.
*   **Overdraw:** Use "Show GPU Overdraw" in Developer Options. Avoid painting the same pixel multiple times (e.g., a background on the Activity, another on the Layout, and another on the View).
*   **Compose Inspector:** Identify which composables are recomposing too frequently. Look for "Unstable" parameters that trigger unnecessary updates.

---

### 🎯 Interview QnA

#### Q: How do you identify a Memory Leak using only code?
**Answer:**
I use **LeakCanary**. It's a library that automatically detects memory leaks in debug builds. It works by monitoring destroyed Activities/Fragments and checking if they are Garbage Collected. If not, it triggers a heap dump and shows a trace of the reference chain keeping the object alive.

#### Q: What is "Baseline Profiles"?
**Answer:**
Baseline Profiles are a way to tell ART which classes and methods should be AOT-compiled *immediately* upon installation. This significantly improves app startup time and reduces "first-run jank" by avoiding JIT compilation for critical code paths.

#### Q: What is the "16ms Rule"?
**Answer:**
To achieve a smooth 60 FPS (Frames Per Second), the system must render a new frame every 16.6 milliseconds. If the Main thread is blocked for longer than this, the system skips a frame, resulting in "jank" or stuttering.
