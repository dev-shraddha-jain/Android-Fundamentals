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

## 🔐 Security Perspective
> **CRITICAL:** Only use `addJavascriptInterface` if you control the content of the web page. A malicious site could use this bridge to execute code on the user's device.

## 🎯 Interview-Ready Answer

**Q: What is the risk of addJavascriptInterface?**

**Answer:**
> It creates a bridge between the JS environment (untrusted) and the Native environment (trusted). If a malicious script is injected into the web page, it can call native methods and potentially steal user data or perform unauthorized actions.
