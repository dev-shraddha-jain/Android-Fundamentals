# Interview QnA: Android Services

### Q1. [How Mechanism] What is the difference between `onStartCommand` and `onBind`?
**The Mechanism:**
*   **`onStartCommand`**: Triggered by `startService()`. The service runs independently of the caller until it is explicitly stopped.
*   **`onBind`**: Triggered by `bindService()`. It provides a client-server interface (IBinder) allowing the caller to interact with the service. The service dies when all clients unbind.

**How to Answer:**
*   Define `startService` as "Fire and Forget".
*   Define `bindService` as a "Conversation".
*   Mention that a service can be both started AND bound at the same time.

---

### Q2. [Tricky] What happens if you perform a network request inside `onStartCommand`?
**The Answer:**
*   The app will likely crash with a `NetworkOnMainThreadException`.
*   A Service runs on the **Main Thread** by default.

**How to Answer:**
*   Correct the common misconception that Services are automatically background threads.
*   Suggest the fix: Use an `IntentService` (deprecated) or a regular `Service` with **Coroutines** or a separate thread.

---

### Q3. [What If] What if the system kills a Foreground Service due to extreme memory pressure?
**The Scenario:**
*   The system will try to restart the service once memory is freed, but ONLY if it returned `START_STICKY` or `START_REDELIVER_INTENT` in `onStartCommand`.

**How to Answer:**
*   Mention that Foreground Services have high priority and are rarely killed.
*   Explain the importance of the return value in `onStartCommand` for reliability.