# 🔍 APK Analysis — Step-by-Step Procedure

## 1. 📦 Understand the APK Structure (Static Entry Point)

**APK = ZIP file**, so first inspect its contents:

- Rename `.apk → .zip` or open with tools
- Key folders:
    - `AndroidManifest.xml` → entry points, permissions
    - `classes.dex` → compiled Java/Kotlin bytecode (Dalvik)
    - `lib/` → native `.so` files (C/C++)
    - `res/`, `assets/` → UI + hidden data
    - `META-INF/` → signing info

👉 Goal: Identify **attack surface quickly**

---

## 2. 🔓 Decode the APK (Decompilation)

Use tools:

- **JADX** → Java/Kotlin readable code
- **APKTool** → Smali + resources

### What to extract:

- Business logic
- Hardcoded secrets
- API endpoints
- Obfuscation level

👉 Example findings:

- API keys in plain text
- Debug flags enabled
- Hidden features

---

## 3. 📜 Analyze AndroidManifest.xml (Critical Step)

This is your **security blueprint**.

### Focus areas:

### 🔐 Permissions

- Dangerous:
    - `READ_SMS`, `SEND_SMS`
    - `READ_CONTACTS`
    - `READ_EXTERNAL_STORAGE`
- Over-permissioning = red flag

### 🚪 Exported Components

Check:

```xml
android:exported="true"
```

- Activities
- Services
- Broadcast Receivers
- Content Providers

👉 Risk:

- Unauthorized access via intents

---

### 🎯 Intent Filters

- Look for:

```xml
<action android:name="android.intent.action.VIEW" />
```

👉 Deep link hijacking possible

---

## 4. 🧠 Reverse Engineer Code (JADX Deep Dive)

### What to search:

- 🔑 Hardcoded secrets:
    - API keys
    - Tokens
    - Encryption keys
- 🌐 Network calls:
    - HTTP vs HTTPS
    - Certificate pinning presence
- 🔓 Authentication logic:
    - Is validation client-side?
- ⚠️ Insecure coding:
    - `WebView.addJavascriptInterface`
    - `setAllowFileAccess(true)`

---

## 5. 🧬 Smali Analysis (Low-Level Inspection)

When code is obfuscated:

- Use APKTool output
- Look for:
    - Method calls
    - Reflection usage
    - Hidden logic

👉 Important for:

- Malware
- Packed apps

---

## 6. 🧪 Dynamic Analysis (Runtime Behavior)

Run the app in:

- Emulator or real device
- Rooted device preferred

### Tools:

- Frida
- Burp Suite
- Logcat

### What to observe:

- 📡 Network traffic
- 🔐 Encryption behavior
- 📁 File access
- 📩 SMS/Call activity

---

## 7. 🌐 Network Traffic Analysis

Using **Burp Suite / MITM Proxy**:

### Check:

- Is HTTPS used?
- Is SSL pinning enabled?
- Sensitive data exposure?

👉 Red flags:

- Tokens in plain text
- No certificate validation

---

## 8. 🔒 Check for Security Protections

### Verify:

- ProGuard / R8 obfuscation
- Root detection
- Emulator detection
- Tamper detection
- SSL pinning

👉 Weak protection = easy to hack

---

## 9. 🧨 Native Code Analysis (lib/*.so)

If present:

- Reverse using:
    - Ghidra / IDA

### Look for:

- Crypto logic
- Hidden payloads
- Anti-debugging

👉 Common in:

- Banking apps
- Malware

---

## 10. 🧾 Signature & Integrity Check

- Check `META-INF/`
- Verify:
    - Certificate validity
    - Debug vs release key

👉 Debug builds in production = 🚨

---

## 11. 🚨 Common Vulnerabilities Checklist

- Exported components without protection
- Hardcoded secrets
- Insecure storage (SharedPreferences)
- WebView vulnerabilities
- No SSL pinning
- Weak crypto (MD5, SHA1)
- Improper auth validation

---

## 12. 🧠 Malware-Specific Checks

If analyzing suspicious APK:

- SMS sending logic
- Background services abuse
- Hidden receivers
- Dynamic code loading
- Obfuscated payloads

---

# 🧩 Real-World Flow (Quick Summary)

1. Extract APK
2. Decode (JADX + APKTool)
3. Analyze Manifest
4. Review code (secrets, APIs)
5. Check exported components
6. Run app (dynamic analysis)
7. Intercept network
8. Inspect native libs
9. Validate protections
10. Document vulnerabilities

---

# 🎯 Interview Tip (Important)

If asked this in interview, say:

> “I follow a layered approach: static analysis (manifest + code), then dynamic analysis (runtime + network), and finally validate protections like obfuscation, SSL pinning, and root detection.”
> 

---

If you want, I can go deeper into:

- 🔥 Real APK hacking demo flow (step-by-step)
- ⚔️ Exploiting exported components
- 🧬 Frida scripts for bypassing SSL pinning

Just tell me what level you want next.