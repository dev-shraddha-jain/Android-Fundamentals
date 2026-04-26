# Interview QnA: Android Intents

### Q1. [How Mechanism] How does "Intent Resolution" work for Implicit Intents?
**The Mechanism:**
*   When an Implicit Intent is fired, the `PackageManager` queries all installed apps for matching `<intent-filter>` declarations.
*   It filters based on three criteria: **Action**, **Data (URI/MIME Type)**, and **Category**.
*   If multiple apps match, the system shows the "App Chooser".

**How to Answer:**
*   Distinguish between Explicit (target class known) and Implicit (target action known).
*   Mention that the `DEFAULT` category is required for almost all implicit intents to be resolved.
*   Explain that this is a form of late-binding in the Android OS.

---

### Q2. [Tricky] Can you pass a 10MB Bitmap through an Intent?
**The Answer:**
*   Technically, yes, but you **should not**.
*   Intents have a shared buffer limit (TransactionTooLargeException) across the whole system, usually around **1MB**.
*   Trying to pass a large object will cause the app to crash during the transaction.

**How to Answer:**
*   Identify the `TransactionTooLargeException` as the main bottleneck.
*   Suggest the senior-level solution: Save the bitmap to a file or a shared cache and pass the **URI** instead.

---

### Q3. [What If] What if you use a PendingIntent with `FLAG_IMMUTABLE`?
**The Scenario:**
*   The system or another app that receives the PendingIntent cannot modify the underlying Intent's extra data.
*   This is a security best practice introduced in Android 12 to prevent "Intent Redirection" attacks.

**How to Answer:**
*   Explain that `FLAG_IMMUTABLE` is now the default/required flag for most cases.
*   Mention that you only use `FLAG_MUTABLE` if the target app (like a Notification or Geofence) needs to fill in specific details (like a timestamp or location).
