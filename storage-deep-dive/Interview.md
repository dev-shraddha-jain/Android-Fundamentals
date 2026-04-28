# Interview QnA: Android Storage Methods

### Q1. How does Room's `fallbackToDestructiveMigration()` work?
**Answer:**
*   Room stores a **hash of your schema** in the database. On open, it compares the stored hash against the current entity definitions.
*   If the version number changed but no matching `Migration` object is provided, Room normally throws an `IllegalStateException` and crashes.
*   With `fallbackToDestructiveMigration()`, instead of crashing, Room **drops all tables and recreates them** from scratch using the new schema.
*   All existing user data in those tables is permanently lost.
*   Safe for development/prototyping. Dangerous in production — always write explicit migrations instead.

---

### Q2. Why did Android move to "Scoped Storage"?
**Answer:**
*   Before Scoped Storage (pre-Android 10), any app with `READ_EXTERNAL_STORAGE` or `WRITE_EXTERNAL_STORAGE` could read and write **every file on the device's SD card** — including other apps' files.
*   This was a massive **privacy and security risk** — a photo editor could silently read your banking documents.
*   Scoped Storage restricts each app to:
    *   Its **own private directory** (`context.getExternalFilesDir()`) with no permission required.
    *   Shared media (photos, music, video) accessible only via the **`MediaStore` API**.
    *   Other files only via the **Storage Access Framework** (user explicitly picks the file).

---

### Q3. What if you perform a Room database operation on the Main Thread?
**Answer:**
*   By default, Room **throws an `IllegalStateException` immediately** at runtime: *"Cannot access database on the main thread since it may potentially lock the UI."*
*   This is intentional — SQLite I/O can take tens or hundreds of milliseconds, which would block the main thread and cause Jank or ANR.
*   You can bypass it with `allowMainThreadQueries()` — but only in tests, never in production code.
*   **Correct approach:** Declare DAO methods as `suspend fun` and call them from a coroutine on `Dispatchers.IO`, or return `Flow<T>` which Room automatically emits on a background thread.
