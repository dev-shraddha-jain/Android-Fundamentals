# Interview QnA: Android App Performance

### Q1. How does the "Choreographer" handle UI rendering?
**Answer:**
*   The display hardware emits a **VSync signal** every 16.6ms (for 60fps) or every 8.3ms (for 120Hz).
*   The **Choreographer** receives this signal and acts as the "beat" coordinator for the UI thread — it signals when to start the next frame's input handling, animation ticks, and measure/layout/draw traversal.
*   If the UI thread is busy (e.g., running a database query), it misses the VSync — this is called a **dropped frame** or "Jank".
*   Systrace and Android Profiler show Choreographer missed frames as red bars in the timeline.

---

### Q2. Does a Memory Leak always lead to an `OutOfMemoryError`?
**Answer:**
*   **No.** If the leak is small and the user closes the app before the heap is exhausted, it may never cause a crash.
*   The real symptom is **GC Thrashing** — the Garbage Collector runs more frequently trying to reclaim space in a fragmented heap. This consumes CPU cycles and causes UI stutters (Jank).
*   A memory leak also delays the LMK (Low Memory Killer) from reclaiming the app's process memory, harming the whole device.
*   Use **LeakCanary** to detect leaks in development. Check for leaked Activity/Fragment references held by static fields or long-lived coroutines.

---

### Q3. What if you perform a Bitmap transformation on the Main Thread?
**Answer:**
*   Bitmap operations (decode, scale, blur) are **CPU and memory intensive**.
*   If the operation takes more than **16ms**, the UI thread misses its VSync signal — the user sees a dropped frame (Jank).
*   If it blocks for more than **5 seconds**, the system displays an **ANR (Application Not Responding)** dialog.
*   **Fix:** Move bitmap work to `Dispatchers.Default` (CPU-bound coroutine) or use Glide/Coil which handle this automatically.
*   Always scale bitmaps down using `BitmapOptions.inSampleSize` before loading into memory to avoid `OutOfMemoryError`.
