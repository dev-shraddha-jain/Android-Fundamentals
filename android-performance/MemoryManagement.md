# Memory Management: ART & Low Memory Killer

Understanding how Android manages memory is critical for building apps that don't crash and feel responsive even on low-end devices.

## 🧠 1. The ART Garbage Collector (GC)
Android Runtime (ART) uses a sophisticated GC to reclaim memory. Unlike the old Dalvik, ART is highly optimized for mobile.

- **Generational GC:** ART divides the heap into generations (Young, Old). Most objects die young, so ART scans the "Young" generation frequently.
- **Concurrent Copying (CC):** In modern Android (8.0+), the GC is "concurrent," meaning it does most of its work while your app is running, significantly reducing "Stop-the-World" pauses.
- **Heap Compaction:** ART can move objects in memory to eliminate fragmentation, allowing larger contiguous allocations.

---

## 📉 2. The Low Memory Killer (LMK)
When the entire system runs low on RAM, the Linux Kernel's **Low Memory Killer Daemon (lmkd)** starts killing processes to free up memory for the foreground app.

### How LMK decides who to kill:
It uses an **OOM Score** (Out of Memory score):
1.  **Foreground App (Score 0):** The app the user is currently using. Last to be killed.
2.  **Visible App:** Not in focus but visible (e.g., a dialog or split screen).
3.  **Service App:** Running a background service (Music, Sync).
4.  **Cached App:** In the background, no active components. First to be killed.

> [!TIP]
> This is why `onSaveInstanceState` is so important. Your process *will* eventually be killed by LMK when in the background.

---

## 🛠️ 3. Memory Leaks: The Silent Killer
A memory leak occurs when an object is no longer needed but is still held by a "Root" (like a static variable or a long-running thread).

### Common Leak Patterns:
- **Inner Classes:** A non-static inner class (like a `Handler` or `Thread`) in an Activity holds a reference to the Activity. If the Activity is destroyed but the thread keeps running, the Activity leaks.
- **Static Context:** Storing an `Activity` context in a static variable.
- **Unregistered Listeners:** Forgetting to unregister a BroadcastReceiver or a LocationListener in `onStop()`.

---

## 🎯 Interview-Ready Answer

**Q: How do you detect and fix memory leaks in Android?**

**Answer:**
> I use tools like **LeakCanary** for automatic detection during development and the **Android Profiler** in Android Studio to track heap growth. To fix leaks, I ensure that long-running tasks use `WeakReference` for Contexts or are cancelled in `onDestroy()`. I also avoid non-static inner classes and prefer `ViewModel` for state persistence as it is lifecycle-aware.

---

## 🚀 Performance Checklist
- [ ] Avoid `static` references to `View` or `Activity`.
- [ ] Use `context.applicationContext` for Singleton initializations.
- [ ] Cancel Coroutines/Threads in `onCleared()` or `onDestroy()`.
- [ ] Use the `Memory Profiler` to check if your heap returns to baseline after navigating away from a heavy screen.
