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
