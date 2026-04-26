# WebView JS Injection

## Definition
Allowing a web page inside a WebView to interact with your Android code.

## 💻 Code Example

```kotlin
class WebInterface(val context: Context) {
    @JavascriptInterface
    fun callNative(msg: String) {
        Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
    }
}

webView.addJavascriptInterface(WebInterface(this), "AndroidBridge")
```

## 🔍 Real-World Process: The Communication

```text
  [ Web Page (HTML/JS) ]
          ↓
  [ JS: AndroidBridge.callNative() ]
          ↓
  [ WebView Core ]
          ↓
  [ Native Kotlin Method ]
```

## 🔐 Security Perspective & How to Fix
The main risk is **Cross-Site Scripting (XSS)**. If an attacker can inject JS into your WebView, they can use the `addJavascriptInterface` to execute native code.

### 🛡️ How to Fix:
1.  **Validate URL Origin**: Before adding the interface, check if the URL starts with your trusted domain.
    ```kotlin
    if (url.startsWith("https://trusted.com")) {
        webView.addJavascriptInterface(myBridge, "AndroidBridge")
    }
    ```
2.  **Disable File Access**: Unless required, disable access to the local file system.
    ```kotlin
    webView.settings.allowFileAccess = false
    webView.settings.allowContentAccess = false
    ```
3.  **Use `WebViewAssetLoader`**: Instead of enabling `allowFileAccess`, use this Jetpack library to load local assets via a virtual HTTPS domain (e.g., `https://appassets.androidplatform.net/`).
4.  **Enforce HTTPS**: Never load `http://` content. Use a `WebViewClient` to block non-secure traffic.

## 🎯 Interview-Ready Answer

**Q: How do you secure a WebView that uses JavascriptInterface?**

**Answer:**
> First, ensure the interface is only added for trusted domains. Second, use the `@JavascriptInterface` annotation (required since API 17) to expose only specific methods. Third, use `WebViewAssetLoader` to serve local content securely. Finally, always intercept URL loading in `shouldOverrideUrlLoading` to prevent the user from navigating to malicious third-party sites while the bridge is active.
