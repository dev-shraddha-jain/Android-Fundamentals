# Interview QnA: Android Architecture

### Q1. How does the Android "Application Sandbox" work at the Linux level?
**Answer:**
*   Every Android app is assigned a **unique Linux User ID (UID)** at install time by the PackageManagerService.
*   The app runs as a separate Linux process under that UID.
*   The **Linux kernel** enforces isolation — one UID cannot read the memory, files, or sockets of another UID.
*   This is not a high-level software concept — it is enforced at the OS kernel level.
*   Apps communicate across sandbox boundaries only via explicit IPC mechanisms (Binder, ContentProvider, Intents) with explicit permission grants.

---

### Q2. What is the difference between a "Cold Start" and "Warm Start"?
**Answer:**
*   **Cold Start:** No process exists. The system forks a new process from **Zygote**, initializes the **ART runtime**, creates the `Application` object, then starts the first Activity. This is the slowest path.
*   **Warm Start:** The process exists in memory. The system recreates the Activity (because it was destroyed) but skips process creation and runtime init. Faster than cold.
*   **Hot Start:** The process and Activity both exist in memory (user just navigated away briefly). The system just brings the Activity back to the foreground. Fastest path.

---

### Q3. What happens if the Zygote process crashes?
**Answer:**
*   Zygote is the **parent of all app processes**. Its crash is catastrophic.
*   The Android System Server detects the crash via a process death signal.
*   The entire Android runtime performs a **soft reboot** — all running apps are killed.
*   Zygote pre-loads Android framework classes and resources at boot so that `fork()` is fast — without it, no new app process can be spawned.

---

### Q4. How does the System Server differ from the Kernel?
**Answer:**
*   The **Kernel** handles low-level OS duties: hardware drivers, memory management, process scheduling, and the **Low Memory Killer**.
*   The **System Server** is a managed Java/Kotlin process that hosts Android framework services: `ActivityManagerService` (AMS), `PackageManagerService` (PMS), `WindowManagerService` (WMS).
*   Apps communicate with System Server services via **Binder IPC** — not direct function calls.
*   The kernel doesn't know what an "Activity" is; that concept lives entirely in the System Server.

---

### Q5. How does the system choose which DEX file to load first in a multi-DEX APK?
**Answer:**
*   The **primary `classes.dex`** must contain all startup-critical classes: `Application`, the first `Activity`, the `MultiDex` installer itself.
*   Secondary files (`classes2.dex`, `classes3.dex`) are loaded either lazily or during startup via the `MultiDex` library.
*   The **`MainDexList`** Gradle configuration determines which classes are forced into the primary DEX.
*   Multi-DEX exists because the **Dalvik/ART method reference limit is 65,536** (the 65k method limit). Modern Android (API 21+) handles it natively via ART.

---

### Q6. Why are Android resources compiled into binary XML?
**Answer:**
*   Parsing plain text XML at runtime requires a full tokenizer, string allocation, and DOM construction — it is slow and memory-intensive.
*   Binary XML is **pre-parsed at build time** into a compact binary format (`resources.arsc` and binary `.xml` files) that the system reads directly with minimal allocation.
*   This improves **app startup time** and reduces **battery usage** because the CPU does less work per frame.

---

### Q7. What if you include a 10MB image in `res/drawable/`?
**Answer:**
*   The **APK size increases** by ~10MB, impacting download and install rates.
*   At runtime, loading the image decodes it into a Bitmap in RAM. A 10MB PNG can expand to **40-100MB of heap memory** (width × height × 4 bytes per pixel), easily triggering an `OutOfMemoryError`.
*   **Fix:** Use **Vector Drawables** for icons (scale perfectly, tiny file size). Use **WebP** for photos (30-40% smaller than JPEG at same quality). Use Android App Bundle + **Density Splits** so the system serves the correctly sized drawable to each device.
