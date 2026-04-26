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