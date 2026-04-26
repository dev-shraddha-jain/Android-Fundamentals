# Interview QnA: Android Storage Methods

### Q1. [How Mechanism] How does Room's `fallbackToDestructiveMigration()` work?
**The Mechanism:**
*   If Room detects a version change but no `Migration` path, it checks for this flag.
*   If enabled, it drops all existing tables and recreates them from scratch using the new schema.
*   All user data in those tables is lost.

**How to Answer:**
*   Warn that this is dangerous for production apps.
*   Explain that it is useful for rapid prototyping where data persistence isn't critical.
*   Suggest providing explicit migrations for any app with real user data.

---

### Q2. [Tricky] Why did Android move to "Scoped Storage"?
**The Reason:**
*   Previously, any app with "Storage Permission" could read/write every file on the SD card (Privacy nightmare).
*   Scoped Storage isolates apps to their own folders and requires high-level APIs (`MediaStore`) for shared files.

**How to Answer:**
*   Focus on **Privacy** and **Security**.
*   Mention that it prevents apps from "polluting" the SD card with random folders.

---

### Q3. [What If] What if you try to perform a Room database operation on the Main Thread?
**The Result:**
*   By default, Room will throw an `IllegalStateException` at runtime.
*   This is a safety measure to prevent ANR (Application Not Responding) errors.

**How to Answer:**
*   Explain that database I/O is slow and must be offloaded.
*   Suggest using `suspend` functions in the DAO and calling them via `Dispatchers.IO`.
