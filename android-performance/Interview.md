# Interview QnA: Android App Performance

### Q1. [How Mechanism] How does the "Choreographer" handle UI rendering?
**The Mechanism:**
*   The Choreographer receives a VSync signal (usually every 16.6ms for 60fps).
*   It coordinates the timing of animations, input events, and layout/draw traversals.
*   It ensures that the UI thread only starts working on the next frame when the hardware is ready.

**How to Answer:**
*   Define the Choreographer as the "Drummer" of the UI thread.
*   Explain that "Skipped Frames" happen when the UI thread is too busy to respond to the Choreographer's signal.
*   Mention that 120Hz displays give the Choreographer only 8.3ms per frame.

---

### Q2. [Tricky] Does a Memory Leak always lead to an `OutOfMemoryError` (OOM)?
**The Answer:**
*   No. A small memory leak might never trigger an OOM if the user closes the app before the heap is full.
*   However, it causes the Garbage Collector to run more frequently (**GC Thrashing**), which leads to UI stutters (Jank).

**How to Answer:**
*   Clarify that the primary symptom of a leak isn't always a crash; it's often poor **performance** and battery drain.
*   Explain that the GC has to work harder to find space in a fragmented heap.

---

### Q3. [What If] What if you perform a Bitmap transformation on the Main Thread?
**The Scenario:**
*   Bitmaps are memory-intensive. Processing them involves heavy CPU work.
*   If this takes >16ms, the UI thread misses the VSync signal.
*   The user sees "Jank" or an "ANR" (Application Not Responding) dialog if the block lasts >5 seconds.

**How to Answer:**
*   State the "Main Thread is for UI only" rule.
*   Suggest moving the work to a Background Thread (Coroutines/Dispatchers.Default).
*   Mention that Bitmaps should be scaled down using `inSampleSize` before loading to save memory.
