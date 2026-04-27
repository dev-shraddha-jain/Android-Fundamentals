# Interview QnA: Android Activity Lifecycle

### Q1. [How Mechanism] What exactly happens during a Configuration Change (e.g., Rotation)?
**The Mechanism:**
*   The system kills the current Activity instance (`onPause` -> `onStop` -> `onDestroy`).
*   It looks up the resource qualifiers for the new orientation (e.g., `layout-land`).
*   It creates a brand new Activity instance and calls `onCreate` with a `Bundle` containing the saved state.

**How to Answer:**
*   State clearly that the **Instance is NOT reused**.
*   Mention that `ViewModel` is the modern way to keep data alive through this process.
*   Explain that the `Bundle` in `onCreate` is for UI state, not large data.

---

### Q2. [Tricky] Is `onDestroy` always guaranteed to be called?
**The Answer:**
*   **No.** If the system kills the app process due to low memory, it kills the Linux process immediately.
*   `onDestroy` is only guaranteed when the user explicitly finishes the activity (e.g., Back button) or `finish()` is called.

**How to Answer:**
*   Correct the myth that `onDestroy` is a reliable cleanup spot for critical data.
*   Suggest saving critical data in `onPause` or `onStop` instead.

---

### Q3. [What If] What if you start a new Activity from `onPause`?
**The Result:**
*   The system will immediately transition the current activity to `onStop`.
*   This is generally a bad UX practice as it interrupts the user during a transition.

**How to Answer:**
*   Focus on the **Performance** and **UX** impact.
*   Explain that `onPause` should be kept as lightweight as possible.


### Q4. [Process Creation] When you launch the app, what happens under the hood?
**The Answer:**
*   **Zygote Forking:** The system forks a new process from the Zygote process (which preloads the Dalvik/ART VM and common classes).
*   **ActivityThread:** The new process starts its `ActivityThread.main()` which sets up the main Looper.
*   **Binding & Loading:** The system binds to the app and loads the app's classes via the ClassLoader.
*   **Lifecycle Start:** `Application.onCreate()` runs, followed by the new Activity's `onCreate()`, `onStart()`, and `onResume()`.

### Q5. [System Kill] What happens to your app if the Android System kills the process while it is in the background?

**The Answer:**
*   **Instance Destroyed:** The Activity instance is completely destroyed.
*   **No Saved State:** By default, **no state** is saved.
*   **Manual Save:** You must explicitly save UI state in `onSaveInstanceState`.
*   **Data Persistence:** Critical data should be saved to persistent storage (Room/DataStore) in `onStop` or `onPause`.

**How to Answer:**
*   Highlight the difference between **UI State** (`onSaveInstanceState`) and **Business Data** (Room/Repository).
*   Explain that the System Kill is **unavoidable** in low-memory situations.


### Q6. [Lifecycle vs Memory] When would you use `onPause()` vs `onStop()` for saving data?
**The Answer:**
*   **`onPause()`:** For very fast, critical operations (e.g., stopping a video). It is called when the user is **leaving** the screen (even partially).
*   **`onStop()`:** For heavier operations (e.g., saving DB records). It is called when the activity is **not visible** (e.g., backgrounded or behind another full-screen activity).

**How to Answer:**
*   Emphasize that **`onStop()`** is the preferred place for long-running save operations because the system gives the process more time before killing it.


### Q7. [Activity Creation] Why do we call super.onCreate(savedInstanceState) first in Android Activities?

**The Answer:**
*   **Component Setup:** `super.onCreate()` initializes the Activity's internal state and components (e.g., `mComponent` and `ActivityResources`).
*   **Lifecycle Dependency:** If skipped, the system cannot properly manage the Activity's lifecycle, and calls to `startActivity()` or `finish()` later in your `onCreate` might fail.
*   **Safe State Recovery:** It restores the saved Bundle (UI state) to the Activity instance **before** you start executing your custom logic.

**How to Answer:**
*   Explain that it is mandatory for **System Integration**.
*   Mention that it handles the restoration of saved state and initializes the Activity's core components.

### Q8. [Memory] How can you prevent your Activity from being killed by the OS when it goes into the background?

**The Answer:**
*   **Foreground Service:** Start a **Foreground Service** with a persistent notification. This tells the OS that the app is doing important work (e.g., music playback, navigation) and shouldn't be killed.
*   **`startForeground()`:** You must call `startForeground()` with a unique ID.

**How to Answer:**
*   Be specific: Use a **Foreground Service**, not just a "background service".
*   Mention the `startForeground(notificationId, notification)` method.
*   Add a caveat: Users might dislike intrusive notifications; use this only when necessary.

### Q9. [UI/UX] Why is it important to save UI state, and how does `ViewModel` help?

**The Answer:**
*   **Why Important:** Without saving state, user input (like text in a form) and transient UI data (like scroll position) are lost when the Activity is recreated (e.g., during rotation), leading to a poor user experience.
*   **`ViewModel`'s Role:** `ViewModel` objects are scoped to a `ViewModelStoreOwner` (usually the Activity or Fragment). They survive configuration changes. When the Activity is recreated, the **same** `ViewModel` instance is returned, preserving the data.

**How to Answer:**
*   Explain that `ViewModel` lives **longer** than the Activity instance.
*   Differentiate between **UI State** (stored in `ViewModel`) and **Business Data** (stored in Repository/DB).


### Q10. [Multitasking] How do you handle multiple instances of the same Activity (e.g., launching the same app twice)?

**The Answer:**
*   **Default (`standard`):** Creates a new instance every time. If launched twice, you have two instances.
*   **`singleTop`:** Reuses the instance if it's at the top of the stack. If not, it creates a new one.
*   **`singleTask`:** Ensures only one instance exists in its task. Starting it again clears the stack above it.

**How to Answer:**
*   Explain the **Launch Modes** (`standard`, `singleTop`, `singleTask`, `singleInstance`).
*   Give a practical example: `singleTop` is great for notifications to avoid duplicates in the back stack.

### Q11. [Communication] How do you pass data between Activities? (Preferable Way)

**The Answer:**
*   **Primary Method:** Use `Intent` extras. For simple data types, use `intent.putExtra()`. For complex objects, implement `Parcelable` or `Serializable`.
*   **Modern Approach:** Use a shared `ViewModel` (with dependency injection) for data that needs to be shared across multiple screens or survive configuration changes.

**How to Answer:**
*   Distinguish between **One-time data transfer** (Intent) and **Shared state** (ViewModel).
*   Strongly recommend **ViewModel** for architecture and testability.

### Q12. [Lifecycle] Explain the Activity states and the meaning of "State Preservation".

**The Answer:**
*   **States:**
    *   **Alive:** Activity exists, user can interact (onResume).
    *   **Visible:** Activity is on screen but not in foreground (onPause).
    *   **Hidden:** Activity not visible at all (onStop).
*   **State Preservation:** When the system kills an Activity (e.g., low memory), it saves its state in a `Bundle`. This Bundle is passed to the new Activity's `onCreate`.

**How to Answer:**
*   Explain that the `Bundle` is mainly for **UI State** (e.g., text in an EditText), **not** business logic.
*   Emphasize using **ViewModel** to preserve data beyond the Activity's lifecycle.


### Q13. [Performance] How do you optimize Activity startup time?

**The Answer:**
*   **Layout Optimization:** Use `ConstraintLayout` to reduce nesting. Avoid deep view hierarchies.
*   **Lazy Initialization:** Don't initialize heavy objects (e.g., large databases, complex services) in `onCreate`. Initialize them lazily or in a background thread.
*   **App Startup Class:** Use the `App Startup` library to initialize SDKs in parallel.
*   **Splash Screen:** Use a proper Android Splash Screen (Jetpack) instead of a custom Activity with a heavy layout.

**How to Answer:**
*   Focus on **Layout Performance** (`ConstraintLayout`) and **SDK Initialization**.


### Q14. [Best Practices] When should you call `finish()` vs `finishAffinity()`?

**The Answer:**
*   **`finish()`:** Removes the **current** Activity from the stack.
*   **`finishAffinity()`:** Removes **all** activities in the current task that share the same affinity (usually all activities in the same app).

**When to Use:**
*   **`finish()`:** When you want to go back to the previous screen.
*   **`finishAffinity()`:** When you want to clear the entire task (e.g., after a logout or completing a wizard).


### Q15. [Internals] What is the difference between `Activity` and `Context`? Can an Activity be a `Context`?

**The Answer:**
*   **Context:** An abstract class that provides access to application-specific resources and classes. It is the base for all `ContextWrapper` classes.
*   **Activity:** A specific implementation of `Context` that represents a screen with a UI.
*   **Yes, an Activity is a Context.** In fact, it is one of the most common types of Context.

**How to Answer:**
*   Clarify that `Activity` **extends** `ContextThemeWrapper` (which extends `Context`).
*   Explain that when you need a context *tied to a specific UI lifecycle* (e.g., for animations), you use the Activity Context. When you need a *global application context*, you use `ApplicationContext`.


### Q16. [Activity Results] How do you handle results from launched activities (e.g., getting an image from the camera)?

**The Answer:**
*   **Old Way:** Override `onActivityResult()` in the calling Activity.
*   **Modern Way:** Use the **Activity Result APIs** (e.g., `registerForActivityResult`). This separates the result handling logic into a reusable component.

**How to Answer:**
*   Strongly recommend the **Activity Result APIs**.
*   Show the pattern: `val launcher = registerForActivityResult(ActivityResultContracts.GetContent()) { uri -> ... }`.
*   Explain that it's safer and decouples the logic from the lifecycle.


### Q17. [Architecture] How do you implement MVVM with Activities and ViewModels?

**Answer:**
In a standard MVVM implementation:
1. **The View (Activity):** Responsible only for UI logic and observing data. It gets a reference to the `ViewModel` using `viewModels()` or `ViewModelProvider`. It uses `repeatOnLifecycle` or `observe()` to listen to data streams.
2. **The ViewModel:** Holds the UI state and handles user interactions. It communicates with the Repository and exposes data through observable types like `StateFlow`, `SharedFlow`, or `LiveData`. It **never** holds a reference to the Activity/Context to avoid memory leaks.
3. **The Data Layer (Repository):** A single source of truth for data, coordinating between local (Room) and remote (Retrofit) data sources.

**Key Benefit:** This ensures that the Activity remains "dumb" and lifecycle-aware, while the business logic and state are preserved during configuration changes by the ViewModel.


### Q18.Explain why Android uses Zygote process instead of creating every app process from scratch.
Include:
- memory benefits
- startup speed
- copy-on-write
- ART/Dalvik preload
- security isolation
Answer briefly but technically.

**The Answer**
Android uses **Zygote** as a pre-warmed parent process from which app processes are forked.

### Key Reasons

* **Faster App Startup**

  * Core Android runtime and common classes are already loaded in Zygote.
  * New app process is created using `fork()` instead of bootstrapping JVM/runtime from zero.

* **Memory Efficiency**

  * Shared read-only memory pages can be reused across many apps.
  * Common framework classes/resources don’t need duplicate copies in each process.

* **Copy-On-Write (COW)**

  * After `fork()`, child initially shares parent memory pages.
  * Only modified pages are copied, reducing RAM usage.

* **Preloaded ART Runtime / Framework**

  * Zygote preloads:

    * framework classes
    * resources
    * fonts
    * common libraries
  * This avoids repeating heavy initialization for every app.

* **Security Isolation**

  * Even though forked from same parent, each app runs:

    * separate Linux process
    * unique UID
    * sandboxed storage
    * isolated memory space

* **Lower CPU / Battery Cost**

  * Reusing initialized runtime reduces repeated work and CPU cycles.

---

## One-Line Interview Summary

“Android uses Zygote to fork pre-initialized app processes, giving faster launch times, lower memory usage through copy-on-write, and still preserving per-app sandbox isolation.”

---