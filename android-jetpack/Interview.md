# Interview QnA: Android Jetpack & DI

### Q1. [How Mechanism] How does Hilt internally handle "Scope" (e.g., @ActivityScoped)?
**The Mechanism:**
*   Hilt generates a custom "Component" for each scope (e.g., `ActivityComponent`).
*   When a dependency is marked as scoped, Hilt creates a single instance of that object and stores it within the corresponding Component instance.
*   This Component is tied to the lifecycle of the owner (the Activity); when the Activity is destroyed, the Component and its scoped objects are cleared.

**How to Answer:**
*   Explain that Hilt is a wrapper around Dagger and uses Dagger's scoping mechanism.
*   Mention that "Scope" is simply about the lifetime of a dependency relative to its container.
*   Highlight that using scopes incorrectly can lead to memory leaks (e.g., providing an Activity context to a Singleton).

---

### Q2. [Tricky] Why does ViewModel survive configuration changes but not process death?
**The Mechanism:**
*   **Rotation:** The `ViewModelStoreOwner` (Activity) persists the `ViewModelStore` during rotation. The system keeps the ViewModel instance in memory.
*   **Process Death:** The entire Linux process is killed. Memory is cleared. The ViewModel is an in-memory object and is lost.

**How to Answer:**
*   Clarify that ViewModels are **not** persistent storage; they are **memory** storage.
*   Mention that to survive process death, you must use `SavedStateHandle` or persistent storage (Room/Prefs).

---

### Q3. [What If] What happens if you try to inject a @FragmentScoped dependency into a @Singleton?
**The Scenario:**
*   The Dagger/Hilt compiler will throw a compile-time error.
*   This is because a Singleton (Long-lived) cannot depend on a FragmentScoped object (Short-lived). It's a "Scope Mismatch".

**How to Answer:**
*   State clearly that dependencies can only go from **Longer-lived to Shorter-lived** containers, or within the same container.
*   Explain that Dagger enforces "Graph Integrity" at compile time to prevent memory leaks and null pointers.
