# Interview QnA: The Big Four (App Components)

## Part 1: Activity Lifecycle

### Q1. What exactly happens during a Configuration Change (e.g., Rotation)?
**Answer:**
*   The system calls `onPause` → `onStop` → `onDestroy` on the current Activity instance — the instance is completely destroyed.
*   The system looks up resource qualifiers for the new configuration (e.g., finds a `layout-land/` folder).
*   A brand new Activity instance is created. `onCreate` is called with the `Bundle` from `onSaveInstanceState` (if you saved anything).
*   The Activity instance is **never** reused — a new object is always created.
*   `ViewModel` survives this because it's stored in the `ViewModelStore`, which is retained by the system's `NonConfigurationInstance` mechanism and handed to the new Activity.

---

### Q2. Is `onDestroy` always guaranteed to be called?
**Answer:**
*   **No.** If the system kills the app process due to low memory, it sends a `SIGKILL` to the Linux process. The process dies immediately with no callbacks.
*   `onDestroy` is only guaranteed when:
    *   The user presses Back (calls `finish()` implicitly).
    *   You explicitly call `finish()`.
    *   A configuration change occurs (system calls `recreate()`).
*   **Never** use `onDestroy` as a reliable place to save critical data. Use `onPause` or `onStop` instead.

---

### Q3. What if you start a new Activity from `onPause`?
**Answer:**
*   `onPause` is called when the current Activity is losing focus — it's meant to be extremely fast (under 16ms).
*   Calling `startActivity()` from `onPause` immediately queues another state transition. The current Activity moves to `onStop` before the new one becomes visible.
*   This creates a janky, stacked transition that disrupts the user. The new Activity must wait for the current one to fully pause before it can receive focus.
*   Keep `onPause` lightweight: release camera, pause media, commit short writes. Move heavy logic to background threads or `onStop`.

---

### Q4. When you launch an app, what happens under the hood?
**Answer:**
*   The system checks if a process for this app's UID exists. If not, it asks **Zygote** to fork a new process.
*   The forked process starts `ActivityThread.main()`, which creates the main **Looper** and **Handler**.
*   The system's AMS binds to the new process via Binder IPC and instructs it to initialize the app.
*   The `ClassLoader` loads the `Application` class. `Application.onCreate()` fires.
*   AMS then tells `ActivityThread` to create and launch the initial `Activity` — `onCreate` → `onStart` → `onResume`.

---

### Q5. What happens if the Android system kills your app process while it's in the background?
**Answer:**
*   The entire Linux process is `SIGKILL`ed. No callbacks fire. All in-memory data (ViewModel, caches, variables) is gone.
*   When the user returns to your app, the system **re-creates** the back stack from the saved instance state (if any).
*   UI state (e.g., scroll position, text field content) is restored only if you explicitly saved it in `onSaveInstanceState`.
*   Critical business data (form data, pending uploads) is lost unless you persisted it to Room/DataStore before the kill.
*   This is unavoidable in low-memory situations — design for it, not against it.

---

### Q6. When would you use `onPause()` vs `onStop()` for saving data?
**Answer:**
*   **`onPause()`:** Called when the Activity is partially obscured (e.g., a dialog appears) or about to leave the foreground. Use it for **fast, critical saves** — pause video playback, commit a short SharedPreference write.
*   **`onStop()`:** Called when the Activity is fully invisible. Use it for **heavier saves** — writing to Room, uploading pending data. The system gives more CPU time before killing a stopped process vs a paused one.
*   **Rule of thumb:** If the user can still see your UI, use `onPause`. If they can't see it at all, use `onStop`.

---

### Q7. Why do we call `super.onCreate(savedInstanceState)` first?
**Answer:**
*   `super.onCreate()` initializes the Activity's internal framework components: restores the `Window`, initializes `FragmentManager`, sets up the `ViewModelStore`, and restores the `savedInstanceState` Bundle into the Activity's state.
*   If you skip it, the Activity has no valid internal state — `setContentView()`, `startActivity()`, and `finish()` may crash or behave unexpectedly.
*   The `savedInstanceState` Bundle is attached to the Activity object **inside** `super.onCreate()`, before your code runs — so your logic can safely use restored data immediately after.

---

### Q8. How can you prevent your Activity from being killed when it goes into the background?
**Answer:**
*   Start a **Foreground Service** with a persistent system notification. A foreground service has high OS priority and is rarely killed even under memory pressure.
*   Call `startForeground(notificationId, notification)` inside the Service's `onStartCommand`. Without this call, the service is treated as a background service and killed first.
*   Use only when genuinely needed (music playback, navigation, location tracking) — the mandatory notification makes this visible to the user.

---

### Q9. Why is it important to save UI state, and how does `ViewModel` help?
**Answer:**
*   When an Activity is recreated (rotation, system kill + reopen), all UI state is wiped. A user typing in a form or scrolling a list would lose their position — bad UX.
*   **`ViewModel`** survives configuration changes (rotation) because it's stored in `ViewModelStore`, which is retained by the system. The same `ViewModel` instance is returned to the new Activity via `viewModels()`.
*   `ViewModel` does **not** survive process death. For that, use `SavedStateHandle` (serialized to Bundle) for primitive UI state, and Room/DataStore for persistent data.

---

### Q10. How do Launch Modes affect multiple instances of an Activity?
**Answer:**
*   **`standard` (default):** A new instance is created every time the Activity is started. You can have 10 copies on the back stack.
*   **`singleTop`:** If an instance is already at the **top of the back stack**, the system calls `onNewIntent()` on it instead of creating a new one. If it's not at the top, a new one is created. Use for notification deep links.
*   **`singleTask`:** Only one instance ever exists in the task. If it already exists, the back stack is cleared up to it and `onNewIntent()` is called. Use for the app's main/home screen.
*   **`singleInstance`:** Like `singleTask`, but the Activity gets its own dedicated task (back stack) — no other Activities share the task.

---

### Q11. How do you pass data between Activities?
**Answer:**
*   **`Intent` extras:** Use `intent.putExtra(key, value)` for primitive types and `Parcelable` for objects. Parcelable is preferred over Serializable — it's 10x faster (no reflection).
*   **Binder IPC limit:** The total size of Intent extras must stay under **~1MB** (the Binder transaction buffer). Exceeding it causes a `TransactionTooLargeException`.
*   **Large data:** Never pass Bitmaps or large objects through Intents. Save them to a file or Room first, then pass the URI or ID.
*   **Shared ViewModel:** For data that needs to be shared between multiple screens or survive configuration changes, use a shared `ViewModel` scoped to the Activity or Navigation graph.

---

### Q12. Explain the Activity states and "State Preservation".
**Answer:**
*   **Resumed:** Activity is fully visible and interactive (`onResume`).
*   **Paused:** Partially visible, losing focus (dialog on top) — `onPause`.
*   **Stopped:** Fully invisible — `onStop`.
*   **Destroyed:** Killed — `onDestroy`.
*   **State Preservation:** When the system destroys an Activity (low memory or rotation), it first calls `onSaveInstanceState(bundle)`. You write small UI state (scroll position, text) into the Bundle. When the Activity is recreated, this Bundle is passed to `onCreate` and `onRestoreInstanceState`.
*   The Bundle is for **small UI state only** (must be serializable). Large data goes to Room/ViewModel.

---

### Q13. How do you optimize Activity startup time?
**Answer:**
*   **Defer heavy work from `onCreate`:** Don't initialize databases, network clients, or large caches synchronously. Use lazy initialization or background coroutines.
*   **Flat layouts:** Deep view hierarchies multiply measure/layout passes. Use `ConstraintLayout` to keep hierarchies flat.
*   **App Startup library:** Initialize Jetpack libraries and SDKs in parallel using the App Startup library's `Initializer` interface.
*   **Baseline Profiles:** Pre-compile critical code paths using Baseline Profiles — reduces JIT compilation at first run.
*   **Avoid transparent splash screens:** Use the official Jetpack SplashScreen API — the system handles it natively without an extra Activity.

---

### Q14. When should you call `finish()` vs `finishAffinity()`?
**Answer:**
*   **`finish()`:** Pops only the **current Activity** from the back stack. The user returns to the previous Activity.
*   **`finishAffinity()`:** Pops the current Activity **and all other Activities in the same task with the same affinity**. On most apps this clears the entire back stack.
*   Use `finishAffinity()` after a logout flow (you don't want the user to press Back and return to authenticated screens) or after completing a linear wizard flow.

---

### Q15. What is the difference between `Activity` and `Context`?
**Answer:**
*   `Context` is an abstract class providing access to application resources, system services, and global state.
*   `Activity` extends `ContextThemeWrapper` (which extends `ContextWrapper`, which extends `Context`). So an Activity **is** a Context.
*   Use **Application Context** for long-lived operations (singleton, global caches) — it doesn't carry UI lifecycle.
*   Use **Activity Context** for UI-related operations (inflating layouts, starting Activities, showing Dialogs) — it's tied to the Activity lifecycle and must never be stored in a longer-lived object (causes memory leak).

---

### Q16. How do you handle results from launched activities (e.g., picking an image)?
**Answer:**
*   **Old way (`onActivityResult`):** Deprecated. Had no type safety and poor separation of concerns — the caller and result handler were tightly coupled inside the Activity.
*   **Modern way (Activity Result APIs):** Register a launcher before the Activity starts using `registerForActivityResult(contract, callback)`. When the result arrives, the callback fires.
*   Example: `val launcher = registerForActivityResult(ActivityResultContracts.GetContent()) { uri -> loadImage(uri) }`. Call `launcher.launch("image/*")` to trigger it.
*   **Why better:** Type-safe contracts, testable, works correctly across configuration changes, decoupled from Activity lifecycle.

---

### Q17. How do you implement MVVM with Activities and ViewModels?
**Answer:**
*   **View (Activity):** Observes `StateFlow`/`LiveData` from the ViewModel using `repeatOnLifecycle(STARTED)`. Only contains UI logic — no business rules. Gets ViewModel via `viewModels()`.
*   **ViewModel:** Holds and manages UI state. Communicates with the Repository. Exposes immutable state (`val uiState: StateFlow<UiState>`). Never holds a reference to `Context` or `View` — this prevents memory leaks.
*   **Repository:** Single source of truth. Decides whether to fetch from network or return cached Room data. The ViewModel calls use cases or the repository directly.
*   **Key invariant:** The Activity is "dumb" — it only renders what the ViewModel tells it to. All state decisions live in the ViewModel.

---

### Q18. Why does Android use Zygote instead of creating every app process from scratch?
**Answer:**
*   **Speed:** Creating a JVM/ART from scratch takes hundreds of milliseconds. Zygote pre-initializes the ART runtime and loads all Android framework classes at boot. A `fork()` of Zygote takes ~1ms.
*   **Memory Efficiency:** All forked processes share the same read-only memory pages for framework classes via **Copy-on-Write (COW)**. Pages are only copied to the child when modified — saving tens of MBs of RAM.
*   **ART Preloading:** Zygote preloads common classes, resources, and fonts so every new app process has them instantly without re-reading from disk.
*   **Security:** Despite sharing the parent, each forked process immediately gets its own unique UID, sandbox, and isolated memory space — the kernel enforces this.

---

## Part 2: Services

### Q1. What is the difference between `onStartCommand` and `onBind`?
**Answer:**
*   **`onStartCommand`:** Called when another component calls `startService()`. The service is started independently and keeps running until `stopSelf()` or `stopService()` is called — the caller doesn't stay connected.
*   **`onBind`:** Called when another component calls `bindService()`. The service returns an `IBinder` interface. The caller communicates with the service directly via that interface. The service is destroyed when all clients unbind.
*   A service can be both started AND bound simultaneously — it only stops when it's both stopped and all clients unbound.

---

### Q2. What happens if you perform a network request inside `onStartCommand`?
**Answer:**
*   The app crashes immediately with `NetworkOnMainThreadException`.
*   A `Service` runs on the **Main Thread** (the UI thread) by default — it is NOT a background thread.
*   This is one of the most common misconceptions about Services.
*   **Fix:** Launch a coroutine with `lifecycleScope.launch(Dispatchers.IO)` inside the Service (use `LifecycleService`), or use `IntentService` (deprecated) which ran on a worker thread automatically.

---

### Q3. What if the system kills a Foreground Service due to extreme memory pressure?
**Answer:**
*   Foreground Services have high priority and are among the last to be killed, but in extreme memory situations they can be.
*   Whether the system restarts it depends on the return value of `onStartCommand`:
    *   `START_STICKY`: The system restarts the service with a null Intent — good for music players that should resume.
    *   `START_REDELIVER_INTENT`: The system restarts the service and redelivers the last Intent — good for download tasks that must resume.
    *   `START_NOT_STICKY`: The system does NOT restart the service.

---

## Part 3: Intents

### Q1. How does "Intent Resolution" work for Implicit Intents?
**Answer:**
*   When you fire an implicit Intent (e.g., `ACTION_VIEW` with a URL), the system asks the `PackageManager` to find all components with a matching `<intent-filter>`.
*   The filter is matched on three criteria: **Action** (e.g., `ACTION_VIEW`), **Data/MIME type** (e.g., `text/html`), and **Category** (e.g., `CATEGORY_DEFAULT`).
*   If exactly one match: system launches it directly.
*   If multiple matches: system shows the "App Chooser" dialog.
*   If no match: `ActivityNotFoundException` is thrown — always call `resolveActivity()` first to check.

---

### Q2. Can you pass a 10MB Bitmap through an Intent?
**Answer:**
*   **Technically yes, practically no.** The Binder transaction buffer is shared across the entire system and is approximately **1MB**.
*   Attempting to pass a Bitmap exceeding this limit throws a `TransactionTooLargeException` which crashes the app.
*   **Correct approach:** Write the Bitmap to a file (app's cache dir) or to `MediaStore`, then pass the **file URI** in the Intent. The receiving Activity reads the file from disk.

---

### Q3. What if you use a PendingIntent with `FLAG_IMMUTABLE`?
**Answer:**
*   `FLAG_IMMUTABLE` means no other component (not even your own code) can modify the Intent extras inside this PendingIntent after it's created.
*   This prevents **Intent Redirection attacks** — a malicious app that receives your PendingIntent cannot add extra data to it to abuse your app's permissions.
*   Required by default for most PendingIntent use cases since Android 12 (API 31).
*   Use `FLAG_MUTABLE` **only** when the receiving component needs to fill in values (e.g., the notification system needs to add `EXTRA_NOTIFICATION_ID`, or a geofence needs to add location data).
