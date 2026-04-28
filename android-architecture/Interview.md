# Interview QnA: Android Architecture

### Q1. How does the Android "Application Sandbox" work at the Linux level?
**The "How" Mechanism:**
*   Each Android app is assigned a unique Linux User ID (UID).
*   The app runs as a separate process under that UID.
*   The Linux kernel enforces security between apps by preventing one UID from accessing the files or memory of another UID.

**How to Answer:**
*   Start by mentioning that Android is built on top of the Linux kernel.
*   Explain that the sandbox is not just a high-level concept but a kernel-level enforcement using UIDs.
*   Highlight that this is why apps need "Permissions" to talk to each other (IPC).

---

### Q2. [Tricky] What is the difference between a "Cold Start" and "Warm Start" from a system perspective?
**The Mechanism:**
*   **Cold Start:** The system must create a new Linux process, initialize the ART (Android Runtime), and then create the Application object.
*   **Warm Start:** The process already exists, but the Activity was destroyed and needs to be recreated (or the app is brought from background).

**How to Answer:**
*   Emphasize that a Cold Start involves the Zygote process forking a new process.
*   Mention that Warm starts are faster because they skip the process creation and runtime initialization overhead.

---

### Q3. [What If] What happens if the Zygote process crashes?
**The Scenario:**
*   Since Zygote is the parent of all app processes, its crash is catastrophic.
*   The Android System Server will detect the crash.
*   The entire Android runtime will restart (Soft Reboot), causing all running apps to close.

**How to Answer:**
*   Identify Zygote as the "Process Incubator".
*   Explain that it pre-loads system classes and resources to speed up app launches.
*   Conclude that its failure triggers a system-wide reset because the root of the process tree is gone.

---

### Q4. How does the System Server differ from the Kernel?
**The Mechanism:**
*   The **Kernel** handles hardware abstraction, memory management, and process scheduling.
*   The **System Server** is a high-level process that hosts system services like `ActivityManagerService` (AMS), `PackageManagerService` (PMS), and `WindowManagerService` (WMS).

**How to Answer:**
*   Distinguish between "Low-level" (Kernel) and "Framework-level" (System Server) services.
*   Mention that apps communicate with the System Server via Binder IPC.

---

### Q5. [How Mechanism] How does the system choose which DEX file to load first in a multi-DEX APK?
**The Mechanism:**
*   The primary `classes.dex` contains the startup classes (Application, Splash screen, etc.).
*   Secondary DEX files (`classes2.dex`, etc.) are loaded as needed or during app startup if using the `MultiDex` library.
*   The `MainDexList` configuration determines which classes MUST go into the primary DEX.

**How to Answer:**
*   Explain the 65k method limit that led to Multi-DEX.
*   Mention that modern Android (API 21+) handles Multi-DEX natively via the ART runtime.

---

### Q6. [Tricky] Why are resources like strings and layouts compiled into binary XML?
**The Reason:**
*   Parsing plain text XML at runtime is slow and memory-intensive.
*   Binary XML is pre-parsed and optimized for the Android system to read quickly.

**How to Answer:**
*   Focus on **Performance** and **Battery Life**.
*   Mention that compilation happens during the build process so the phone doesn't have to do it.

---

### Q7. [What If] What if you include a 10MB image in the `res/drawable/` folder?
**The Impact:**
*   The APK size will increase significantly.
*   Loading that image into memory will consume a large portion of the app's heap, potentially leading to an `OutOfMemoryError`.

**How to Answer:**
*   Advise against large assets in the APK.
*   Suggest using **Vector Drawables** for icons and **WebP** or optimized JPGs for photos.
*   Mention "Dynamic Delivery" (AAB) to serve specific image sizes to specific devices.

