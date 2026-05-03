# 📉 Process Management & Low Memory Killer (LMK)

Android is designed to keep apps in memory as long as possible. However, when the system runs out of RAM, it must decide which apps to kill. This is the job of the **Low Memory Killer**.

---

### 1. Process Priority Levels (OOM Scores)
The kernel assigns an `oom_score_adj` to every process. The lower the score, the more "important" the process is.

1.  **Foreground Process (Score: 0):** The app the user is currently interacting with, or a foreground service with a notification.
2.  **Visible Process (Score: 100):** An activity that is visible but not in focus (e.g., behind a dialog) or a service bound to a visible activity.
3.  **Service Process (Score: 500):** A background service (e.g., music playback, data sync) that has been running for a while.
4.  **Cached Process (Score: 900+):** An activity that is in `onStop()` (the user pressed Home). These are the first to be killed.

---

### 2. How LMK Works
Unlike the standard Linux OOM killer (which only acts when memory is completely exhausted), Android's **LMK** has multiple thresholds.
*   It monitors the free memory. When free RAM drops below "Threshold A," it kills the least important Cached processes.
*   If memory is still low and drops below "Threshold B," it starts killing Service processes.
*   **LMKd:** In modern Android, this is a user-space daemon (`lmkd`) that communicates with the kernel to perform these kills more efficiently.

---

### 3. Handling Process Death: `onSaveInstanceState`
When your app is in the "Cached" state and gets killed by LMK, the system remembers the Activity stack.
*   When the user returns, the system restarts the process and recreates the activities.
*   **The Trap:** Static variables and singleton states are **LOST**.
*   **The Fix:** Use `onSaveInstanceState()` or `SavedStateHandle` in ViewModels to persist small amounts of UI state (IDs, search queries, scroll positions).

---

### 4. Background Restrictions
To save battery and RAM, Android has increasingly restricted background work:
*   **Doze Mode:** Limits network and CPU access when the phone is stationary and the screen is off.
*   **App Standby Buckets:** Categorizes apps based on how often they are used (Active, Working Set, Frequent, Rare). "Rare" apps have the most restrictions.

---

### 🎯 Interview QnA

#### Q: What is the difference between `onStop()` and `onDestroy()`?
**Answer:**
`onStop()` means the activity is no longer visible. The process is still alive and the state is in memory. `onDestroy()` means the activity is being removed from the stack (e.g., user pressed Back) or the system is finishing it. **Crucially**, a process can be killed after `onStop()` without `onDestroy()` ever being called.

#### Q: How can you prevent your Service from being killed?
**Answer:**
Promote it to a **Foreground Service** using `startForeground()`. This requires showing a persistent notification to the user, which raises the process priority to "Foreground" (OOM score 0).

#### Q: What is "Battery Optimization" and how does it affect apps?
**Answer:**
It's part of Doze mode. If an app is "Optimized," the system will defer its background tasks and network requests into "Maintenance Windows." If an app needs to perform critical work (like an alarm or a VoIP call), it must be added to the "Not Optimized" list or use special APIs like `AlarmManager.setExactAndAllowWhileIdle()`.
