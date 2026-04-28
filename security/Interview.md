# Interview QnA: Security, Obfuscation & Permissions

## Part 1: Core Security & Best Practices


### Q1. Where do you store auth tokens?

> Access tokens (short-lived, 15 min) live in-memory in the ViewModel — they're cleared when the app is killed. Refresh tokens (long-lived) are stored in `EncryptedSharedPreferences` backed by an AES-256-GCM key in the Android Keystore. We never store any token in plain `SharedPreferences`, a file, or `BuildConfig`.

---

### Q2. How does SSL Pinning work and what are its risks?

> SSL Pinning hardcodes the server's certificate public key hash in the app using `CertificatePinner`. On each HTTPS handshake, OkHttp verifies the server's presented certificate matches the pinned hash — rejecting any other certificate, even a valid CA-signed one. The main risk is **certificate rotation**: if the server renews its certificate and the app's pins aren't updated before the old cert expires, the app loses all connectivity. Mitigation: always pin **two hashes** (current + backup), set an expiry, and use Network Security Config XML which can be updated via OTA without a full release.

---

### Q3. What is the Play Integrity API and when do you use it?

> The Play Integrity API provides **server-side attestation** from Google. The client app requests a signed token from Google, then your backend verifies it by calling Google's API. The response gives three verdicts: is the app signed by your key (`APP_INTEGRITY`), is the device genuine Android with Google Play (`DEVICE_INTEGRITY`), and is the user licensed (`ACCOUNT_DETAILS`). I use it before high-value actions like payment confirmation or account creation — it cannot be bypassed client-side since verification happens server-to-server.

---

### Q4. How do you prevent reverse engineering of your APK?

> **R8 obfuscation** renames classes and methods to meaningless single characters. **ProGuard rules** strip debug logs, keep serialization models intact, and protect Hilt-generated classes. For native code, we use NDK with `.so` files which are harder to decompile than DEX. Beyond obfuscation, we use **tamper detection** (checking the APK signature at runtime) and **Play Integrity API** for server-side validation, since obfuscation alone can be defeated by a patient attacker.

---

### Q5. How do you detect a rooted device?

> Client-side: check for `/system/bin/su`, build tags containing `test-keys`, known root manager package names (Magisk, SuperSU), and writable system partitions. However, Magisk Hide can bypass all of these checks. The real solution is **Play Integrity API** — the `MEETS_DEVICE_INTEGRITY` verdict is computed on Google's servers and is significantly harder to spoof. We use both layers: client-side for UX (warn the user early) and server-side for enforcement (block the transaction).
## Part 2: Permissions & Manifest Security


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

## Part 3: Obfuscation (R8 / ProGuard)


### Q1. [How Mechanism] How does R8 differentiate between used and unused code?
**The Mechanism:**
*   R8 starts from "Entry Points" (Classes/Methods defined in your Manifest or keep rules).
*   It builds a "Call Graph" to see which methods and classes are reachable from those entry points.
*   Any code not reachable in the graph is considered "Dead Code" and is stripped away.

**How to Answer:**
*   Describe the process as "Tree Shaking".
*   Explain that this is why "Keep Rules" are necessary for code accessed via Reflection—R8 cannot see those connections in the static call graph.

---

### Q2. [Tricky] If R8 obfuscates your code, why is your `mapping.txt` file sensitive?
**The Reason:**
*   The `mapping.txt` is essentially the "Translation Key".
*   Anyone with the APK and the mapping file can perfectly reconstruct your original class and method names.
*   Leaking this file makes your obfuscation useless for security.

**How to Answer:**
*   Highlight that `mapping.txt` should be treated like a private key.
*   Mention that it should be archived for every release build to debug crashes.

---

### Q3. [What If] What if you use Reflection to call a method that R8 has obfuscated?
**The Result:**
*   A `NoSuchMethodException` will occur at runtime.
*   R8 renamed the method to something like `a()`, but your reflection code is looking for `"myMethod"`.

**How to Answer:**
*   Identify this as a common "Release-only" bug.
*   Explain the fix: Add a `-keep` rule for that specific class or method in your `proguard-rules.pro` file.


### Q4. [Internals] What is the difference between "Shrinking", "Optimization", and "Obfuscation" in R8?

**The Answer:**
*   **Shrinking:** Removes unused code and resources (Tree shaking).
*   **Optimization:** Performs various optimizations like inlining methods and merging classes.
*   **Obfuscation:** Renames classes/methods/fields to short names (e.g., `a`, `b`).

**How to Answer:**
*   Explain that Shrinking and Optimization happen **first**, and Obfuscation happens **last**.


### Q5. [Best Practices] When would you use `-keep` vs `-keepnames` vs `-keepclassmembers`?

**Answer:**

* **`-keep`**: Keeps the class and all its members (methods and fields). Use this for entry points like Activity, Service, and BroadcastReceiver.
* **`-keepnames`**: Keeps the class name, but allows its members to be renamed. Use this when reflection relies on class names but not method names.
* **`-keepclassmembers`**: Keeps the members (methods and fields) but allows the class itself to be renamed. Use this for classes that are instantiated via reflection (e.g., custom Views) but whose method names are fixed.


### Q6. [Advanced] How do you handle custom Views (e.g., `MyCustomView`) that are inflated using XML or custom attributes?

**Answer:**
You must use `-keep` to preserve the class name and its constructors.

```
-keep class com.example.myapp.views.** { *; }
-keep class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
}
```

### Q7. [Tricky] What is the difference between `minifyEnabled` and `obfuscate` in `build.gradle`?

**Answer:**
`minifyEnabled true` is the main switch in your `build.gradle` that enables the R8/ProGuard tool. This tool handles three distinct phases: **Shrinking** (removing unused code/resources), **Optimization**, and **Obfuscation**. There is no separate `obfuscate` flag in Gradle; instead, obfuscation is a sub-feature of minification. If you want to shrink code but *not* obfuscate it (common for library debugging), you keep `minifyEnabled true` but add `-dontobfuscate` to your `proguard-rules.pro` file.


### Q8 Your release app crashes only in **release build**, debug works fine. Likely due to R8/ProGuard. Explain full debugging mechanism:

* Why debug works but release crashes
* What shrinking/obfuscation changes
* Reflection issue examples
* How mapping.txt helps
* How to fix systematically



### Why debug works but release crashes

* Debug usually has no shrinking/obfuscation.
* Release enables R8, which may:

  * remove “unused” code
  * rename symbols
  * optimize call paths

### Why it breaks

R8 uses static reachability analysis. Dynamic usages are hard to infer:

* reflection
* JNI native bindings
* JSON serialization
* XML-instantiated classes
* annotation processors / generated code
* JavaScript bridges

### mapping.txt use

* Convert obfuscated stacktrace:

  * `a.a.a(Unknown Source)` → real class/method
* Essential for crash tools (Crashlytics, Play Console)

### Fix systematically

1. Reproduce on release locally
2. Get stacktrace + deobfuscate with mapping
3. Identify dynamic access path
4. Add narrow keep rules
5. Rebuild + retest
6. Avoid blanket keep-all rules

```pro
-keep class com.example.model.** { *; }
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}
-keepclasseswithmembers class * {
    native <methods>;
}
```


## Part 4: WebView Security

## Q1 — WebView JavaScript Injection / JS Bridge Exploitation

## Senior Interview Answer (Mechanism + Security)

When app exposes:

```kotlin
webView.addJavascriptInterface(AppBridge(), "Android")
```

JavaScript running inside the WebView can call native Android methods exposed through that bridge.

---

# How an Attacker Exploits This

## 1. Malicious Web Content Loads

If attacker controls page content (or injects script through XSS), page JS can run:

```javascript
Android.getToken()
Android.openCamera()
Android.readData()
```

If bridge methods expose sensitive actions, attacker gains access.

---

## 2. XSS → Native Bridge Abuse

Even trusted domain can be compromised via:

* reflected XSS
* stored XSS
* third-party script compromise
* ad SDK script injection

Then malicious JS calls native bridge methods.

This turns a normal XSS into **device-level privilege escalation inside app sandbox**.

---

## 3. Pre-API 17 Major Risk

Before Android 4.2 (API 17):

* `addJavascriptInterface()` exposed public methods broadly.
* Attackers could use reflection tricks.
* Could potentially reach arbitrary Java methods.

This was historically severe RCE risk.

After API 17:

* Only methods marked with `@JavascriptInterface` are exposed.

---

# evaluateJavascript() vs loadUrl("javascript:")

## `loadUrl("javascript:...")`

Old method.

Problems:

* slower
* string injection risk
* awkward escaping
* no direct return value

## `evaluateJavascript()`

Preferred modern API.

Benefits:

* async callback result
* cleaner execution
* better performance

Still dangerous if untrusted input inserted into JS string.

---

# Origin Validation

Never trust every loaded page.

Before exposing bridge, verify:

* exact domain
* HTTPS
* certificate trust
* redirect destination
* current URL in `WebViewClient`

Example:

```kotlin
if (url.host == "example.com")
```

Better: strict allowlist.

---

# File Access Risks

Dangerous settings:

```kotlin
setAllowFileAccess(true)
setAllowFileAccessFromFileURLs(true)
setAllowUniversalAccessFromFileURLs(true)
```

Risks:

* local file reading
* file:// origin abuse
* cross-origin access
* token leakage

Usually disable unless absolutely required.

---

# Secure Production Design

## Best Practice Architecture

### Instead of exposing broad bridge:

Expose tiny permissioned commands only.

```kotlin
@JavascriptInterface
fun pickImage()
```

Not:

```kotlin
getUserToken()
readContacts()
executeSql()
```

---

# Hardened WebView Checklist

## Settings

```kotlin
javaScriptEnabled = true only if needed
domStorageEnabled = minimal need
allowFileAccess = false
allowContentAccess = false
```

## Navigation Controls

* Use `WebViewClient`
* Block unknown redirects
* Block intent:// abuse
* Open external unknown URLs outside app

## Bridge Controls

* Add bridge only on trusted pages
* Remove bridge when not needed
* Minimal methods
* Validate all input

## Transport Security

* HTTPS only
* Certificate pinning if sensitive

## Data Protection

* No auth token directly exposed to JS
* Use short-lived session patterns

## Debugging

Disable:

```kotlin
WebView.setWebContentsDebuggingEnabled(false)
```

for release builds.

---

# One-Line Interview Summary

“WebView JS bridge can convert XSS into native privilege abuse, so production apps must strictly limit bridge methods, validate origins, harden settings, and avoid exposing sensitive APIs.”

---


## Q2 — Why Malicious JavaScript Can Run Even Though URL Is `https://trusted.com`

Because **URL trust does not equal content trust**. A page can remain on the trusted domain while hostile JavaScript executes inside it.

---

# Main Mechanisms

## 1. XSS (Cross-Site Scripting)

The page on `trusted.com` has a vulnerability that reflects or stores attacker-controlled input.

Examples:

* comment fields
* search parameters
* profile names
* CMS content
* query params inserted into HTML

Then browser/WebView loads:

```text id="6bq5py"
https://trusted.com
```

But inside DOM, attacker script executes.

URL never changes.

---

## 2. Third-Party Script Compromise

Trusted site includes:

```html id="4j51a6"
<script src="https://cdn.vendor.com/sdk.js">
```

If vendor CDN is compromised, malicious JS runs inside `trusted.com` page context.

Still same visible URL.

---

## 3. DOM-Based XSS

JavaScript on trusted site reads attacker-controlled values:

```javascript id="j4xb5r"
location.hash
document.referrer
postMessage()
```

Then injects into DOM unsafely:

```javascript id="j50m5e"
innerHTML = userInput
```

Attacker code runs without page navigation.

---

## 4. Ad / Analytics Script Injection

Ads or analytics SDKs may load dynamic scripts. If abused, malicious JS runs in trusted page context.

---

## 5. MITM on Weak Transport (if no HTTPS integrity)

If mixed content / insecure subresources allowed, network attacker may inject scripts.

---

# Why This Is Dangerous in WebView

If app exposes:

```kotlin id="m0hjj0"
addJavascriptInterface(...)
```

Then malicious JS on same trusted page can call native bridge methods.

So visible URL = trusted, but runtime code = hostile.

---

# How to Defend

## Web Side

* CSP (Content Security Policy)
* sanitize output
* encode HTML/JS contexts
* avoid `innerHTML`
* dependency integrity (SRI)
* patch third-party libraries

## Android Side

* Do not trust URL alone
* Expose minimal JS bridge
* Require signed messages / tokens
* Validate commands server-side
* Remove bridge when unnecessary

---

# One-Line Interview Answer

“A trusted URL can still execute malicious JavaScript through XSS, compromised third-party scripts, or unsafe DOM operations; origin remains same while runtime content becomes hostile.”

---

# Final Senior Interview Verdict So Far

You have solid practical Android exposure.
You need stronger **OS internals + security exploitation mechanics + exact terminology** for senior interviews.

## Current Estimated Level

**Strong Mid-level / Emerging Senior**

---