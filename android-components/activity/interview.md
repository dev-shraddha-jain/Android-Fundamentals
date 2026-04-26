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
