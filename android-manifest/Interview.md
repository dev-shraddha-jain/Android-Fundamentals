# Interview QnA: Android Manifest & Permissions

### Q1. [How Mechanism] What happens internally when you call `requestPermissions()`?
**The Mechanism:**
*   The call is routed to the `PackageManagerService` via Binder IPC.
*   The system displays a modal dialog (which is actually a system-level Activity).
*   The result is passed back to your Activity's `onRequestPermissionsResult()` callback.

**How to Answer:**
*   Mention that permission management is handled by the **System**, not your app's process.
*   Explain that the system tracks "Grant States" in its own database.
*   Highlight that once a user clicks "Don't ask again," the system skips the dialog and returns "Denied" immediately.

---

### Q2. [Tricky] If you change a permission from "Normal" to "Dangerous" in an app update, what happens to existing users?
**The Scenario:**
*   Users who already have the app will NOT be prompted for the new "Dangerous" permission automatically.
*   The next time your app tries to use the feature, it will fail unless you explicitly trigger the runtime permission check.

**How to Answer:**
*   Emphasize that you must **always** check permissions at runtime, regardless of when the app was installed.
*   Explain that the system doesn't "auto-upgrade" permission grants during app updates if they require user consent.

---

### Q3. [What If] What if you set `android:exported="true"` for a Service with no permissions?
**The Risk:**
*   Any app on the device can start or bind to that service.
*   A malicious app could send "Intents" to trigger internal logic or steal data.

**How to Answer:**
*   Identify this as a major **Security Vulnerability**.
*   Explain that `exported="true"` makes the component a "Public Entry Point".
*   Suggest the fix: Use `android:permission` to protect the component or set `exported="false"` if it's internal.
