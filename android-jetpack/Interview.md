# Interview QnA: Android Jetpack & DI

### Q1. How does Hilt internally handle Scope (e.g., `@ActivityScoped`)?
**Answer:**
*   Hilt is built on **Dagger 2**. At compile time, Hilt generates a **Component** for each lifecycle scope (e.g., `SingletonComponent`, `ActivityComponent`, `ViewModelComponent`).
*   When you annotate a dependency with `@ActivityScoped`, Hilt stores a single instance of it **inside the `ActivityComponent`** for that Activity instance.
*   When the Activity is destroyed, the `ActivityComponent` is garbage collected — along with all its scoped dependencies.
*   Using the wrong scope causes leaks: e.g., if you inject an `Activity` context into a `@Singleton`, the Activity is never garbage collected because the Singleton lives for the entire app lifetime.

---

### Q2. Why does ViewModel survive configuration changes but NOT process death?
**Answer:**
*   **Configuration Change (Rotation):** The Activity is destroyed and recreated, but the `ViewModelStore` is retained by the system's `NonConfigurationInstance` mechanism. The ViewModel instance in memory is handed to the new Activity.
*   **Process Death:** The entire Linux process is killed by the OS. All heap memory — including the `ViewModelStore` and the ViewModel object — is wiped out.
*   ViewModel is **in-memory storage only**, not persistence.
*   To survive process death, use `SavedStateHandle` (serialized to `Bundle`) for small UI state, or persist critical data to **Room or DataStore**.

---

### Q3. What happens if you try to inject a `@FragmentScoped` dependency into a `@Singleton`?
**Answer:**
*   The **Dagger/Hilt compiler throws a compile-time error** — the app won't build.
*   This is called a **Scope Mismatch**. A `@Singleton` lives for the entire app lifetime. A `@FragmentScoped` object only lives for a Fragment's lifetime.
*   A long-lived container cannot hold a reference to a short-lived object because the short-lived object can be destroyed while the Singleton still holds a reference to it — causing a memory leak or null reference.
*   Dagger enforces "graph integrity" at compile time so this class of bug is impossible to ship.
