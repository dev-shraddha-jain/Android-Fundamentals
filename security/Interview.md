# Interview QnA: Security, Obfuscation & Permissions

## Part 1: Core Security & Best Practices

### Q1. Where do you store auth tokens?
**Answer:**
*   **Access Tokens (short-lived, ~15 min):** Keep in-memory only — inside the ViewModel. They are automatically cleared when the app is killed.
*   **Refresh Tokens (long-lived):** Store in `EncryptedSharedPreferences` backed by an **AES-256-GCM** key stored in the **Android Keystore** (hardware-backed on most devices).
*   **Never** store any token in plain `SharedPreferences`, a flat file, or `BuildConfig` — all of these are readable without root access.

---

### Q2. How does SSL Pinning work and what are its risks?
**Answer:**
*   SSL Pinning hardcodes the server's **public key certificate hash** inside the app using `CertificatePinner` (OkHttp).
*   On every HTTPS connection, OkHttp compares the server's presented certificate against the pinned hash. If they don't match, the connection is rejected — even if the cert is signed by a trusted CA.
*   This blocks MITM attacks where an attacker installs a fake root CA.
*   **Risk — Certificate Rotation:** If the server renews its cert and the app isn't updated in time, every user loses connectivity.
*   **Mitigation:** Always pin a **primary + backup hash**. Use Network Security Config XML so pins can be pushed without a full app release.

---

### Q3. What is the Play Integrity API and when do you use it?
**Answer:**
*   It provides **server-side device attestation** from Google. The app requests a signed token from Google Play, and your backend calls Google's API to verify it.
*   It returns three verdicts:
    *   `APP_INTEGRITY` — the app binary is signed by your key, not tampered.
    *   `DEVICE_INTEGRITY` — the device runs genuine Android with Google Play certified.
    *   `ACCOUNT_DETAILS` — the user has licensed your app.
*   Use it before high-value actions: **payment confirmation, account creation, admin actions**.
*   Cannot be bypassed client-side because verification is **server-to-server**.

---

### Q4. How do you prevent reverse engineering of your APK?
**Answer:**
*   **R8/ProGuard Obfuscation:** Renames classes and methods to meaningless single characters (`a`, `b`, `c`). Makes decompiled code extremely hard to read.
*   **Native Code (NDK):** Move sensitive logic (e.g., key derivation, license checks) into `.so` C++ files. Native binaries are significantly harder to reverse than DEX bytecode.
*   **Runtime Tamper Detection:** Check the APK's signature at runtime using `PackageManager.getPackageInfo()`. If it doesn't match your release key, refuse to run.
*   **Play Integrity API:** Server-side enforcement that the app hasn't been repackaged.
*   Obfuscation alone is only a speed bump — true security requires multiple layers.

---

### Q5. How do you detect a rooted device?
**Answer:**
*   **Client-side checks (easily bypassable):**
    *   Look for `/system/bin/su` or `/system/xbin/su`.
    *   Check build tags for `test-keys` (indicates non-official ROM).
    *   Look for known root manager packages: `com.topjohnwu.magisk`, `com.koushikdutta.superuser`.
    *   Check if system partitions are writable.
*   **Limitation:** Magisk Hide bypasses all of these by masking root artifacts per-app.
*   **Real solution — Play Integrity API:** The `MEETS_DEVICE_INTEGRITY` verdict is computed on Google's servers and is significantly harder to spoof. Use this for server-side enforcement.

---

## Part 2: Permissions & Manifest Security

### Q6. What happens internally when you call `requestPermissions()`?
**Answer:**
*   Your call is routed via **Binder IPC** to the `PackageManagerService` (PMS) running in the System Server.
*   The system — not your app — displays a modal dialog (it's a system-level Activity in a separate process).
*   The result is delivered back to your Activity via `onRequestPermissionsResult()`.
*   The system tracks each permission's grant state in its own protected database.
*   Once a user clicks "Don't ask again," the system skips the dialog and returns `PERMISSION_DENIED` immediately on all future calls.

---

### Q7. If you change a permission from "Normal" to "Dangerous" in an update, what happens to existing users?
**Answer:**
*   Existing users are **NOT** automatically prompted. The system does not re-evaluate or re-request permissions during app updates.
*   The next time your app calls an API protected by that permission, it will fail silently or throw a `SecurityException`.
*   You must always call `checkSelfPermission()` at runtime before using any dangerous permission — even if you "know" it was granted before.

---

### Q8. What if you set `android:exported="true"` for a Service with no `android:permission`?
**Answer:**
*   Any app on the device can start or bind to your Service by sending an explicit Intent.
*   A malicious app can trigger your internal business logic, spoof actions, or attempt to extract data.
*   This is a well-known vulnerability — Android 12+ now **requires** you to explicitly declare `exported` for components with intent filters.
*   **Fix:** Set `exported="false"` if it's only used internally, OR add `android:permission="com.yourapp.CUSTOM_PERMISSION"` to gate external access.

---

## Part 3: Obfuscation (R8 / ProGuard)

### Q9. How does R8 differentiate between used and unused code?
**Answer:**
*   R8 starts from "entry points" — components declared in the Manifest and explicit `-keep` rules.
*   It performs **static reachability analysis**, building a call graph of every method transitively reachable from those entry points.
*   Any class or method **not reachable** in the graph is classified as dead code and stripped out.
*   This is called **Tree Shaking**.
*   Dynamic usages via **Reflection**, JNI, or serialization are invisible to the static graph — you must add `-keep` rules for them manually.

---

### Q10. Why is your `mapping.txt` file sensitive?
**Answer:**
*   `mapping.txt` is the **reverse translation key** between obfuscated names and your original source code symbols.
*   Anyone with both the APK and `mapping.txt` can fully reconstruct your original class and method names, making obfuscation pointless.
*   Treat it like a private key — never commit it to public repos.
*   You **must** archive it per release build — crash tools like **Crashlytics** and **Play Console** use it to de-obfuscate stack traces automatically.

---

### Q11. What if you use Reflection to call a method that R8 has obfuscated?
**Answer:**
*   At runtime you get a `NoSuchMethodException` or `ClassNotFoundException`.
*   R8 renamed `"myMethod"` to `"a"`, but your reflection string `"myMethod"` still refers to the original name.
*   This only happens in the **release build** (debug has no obfuscation), making it a hard-to-catch bug.
*   **Fix:** Add a `-keep` rule in `proguard-rules.pro` for the specific class/method accessed via reflection.

---

### Q12. What is the difference between Shrinking, Optimization, and Obfuscation in R8?
**Answer:**
*   **Shrinking (Tree Shaking):** Removes unreachable classes, methods, and resources. Runs first.
*   **Optimization:** Inlines methods, merges classes, removes redundant code paths. Runs second.
*   **Obfuscation:** Renames remaining classes/methods/fields to short meaningless characters. Runs last.
*   All three are enabled by `minifyEnabled true`. Disable obfuscation alone with `-dontobfuscate` in your rules file.

---

## Part 4: WebView Security

### Q13. How can a WebView's JavaScript Bridge be exploited?
**Answer:**
*   `addJavascriptInterface(myBridge, "Android")` exposes your native methods to any JavaScript running inside the WebView.
*   If the loaded page has an **XSS vulnerability** — even on a trusted domain — an attacker's injected script can call `Android.getToken()`, `Android.readContacts()`, etc.
*   This escalates a standard web-level XSS into **device-level privilege abuse inside your app sandbox**.
*   Pre-API 17: any public method was accessible via reflection (severe RCE risk). Post-API 17: only `@JavascriptInterface` annotated methods are exposed.
*   **URL trust ≠ Content trust.** The page URL can be `https://trusted.com` while a compromised 3rd-party ad script executes hostile code inside it.

---

### Q14. Why is `evaluateJavascript()` better than `loadUrl("javascript:")`?
**Answer:**
*   `evaluateJavascript()` executes asynchronously and returns the result via a callback — no result is possible with `loadUrl()`.
*   `evaluateJavascript()` is significantly faster and avoids awkward string escaping.
*   `loadUrl("javascript:...")` is deprecated for this use — it forces a full URL navigation step internally.
*   Both are dangerous if you inject untrusted user input directly into the JS string (string injection attack).

---

### Q15. How do you secure a production WebView?
**Answer:**
*   **Minimize the bridge:** Only expose tiny, specific commands (`fun pickImage()`). Never expose `getToken()`, `readContacts()`, or DB access.
*   **Validate origin:** Inside `WebViewClient.shouldOverrideUrlLoading()`, check `url.host` against a strict allowlist before allowing the page to interact with the bridge.
*   **Disable dangerous settings:** `allowFileAccess = false`, `allowContentAccess = false`, `allowUniversalAccessFromFileURLs = false`.
*   **Block external schemes:** Intercept `intent://` and `market://` URIs in `WebViewClient` and open them in the external browser instead.
*   **Enforce HTTPS:** Use Network Security Config to block cleartext traffic entirely.
*   **Disable remote debugging in release:** `WebView.setWebContentsDebuggingEnabled(false)`.