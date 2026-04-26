# Android Manifest

## Definition
The `AndroidManifest.xml` file is the blueprint of your application.

## 🧠 Core Idea: What's inside?

```xml
<manifest ...>
    <uses-permission android:name="android.permission.INTERNET" />

    <application ...>
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

## 🔍 Real-World Process: Installation

```text
  [ User Downloads APK ]
            ↓
  [ Package Manager ]
            ↓
  [ Reads AndroidManifest.xml ]
            ↓
  [ Registers Components ]
            ↓
  [ App is Ready to Launch ]
```

## 🔐 Security: Exported Components
The `android:exported` attribute determines whether a component (Activity, Service, Receiver) can be started by other applications.

*   **`android:exported="true"`**: Any app can launch this component.
*   **`android:exported="false"`**: Only your app or apps with the same User ID can launch it.

> **Note:** Since Android 12, if a component has an `<intent-filter>`, you MUST explicitly set `android:exported`.

## 🎯 Interview-Ready Answer

**Q: What is the risk of setting exported="true" for a Service?**

**Answer:**
> It makes the service public. If the service doesn't perform its own permission checks, any malicious app on the device could start or bind to it, potentially leaking data or executing privileged actions. This is a common entry point for "Intent Redirection" attacks.

---

**Q: What happens if you forget to declare an Activity in the Manifest?**

**Answer:**
> The system will throw an `ActivityNotFoundException` when you try to start it. The Android system only recognizes components that are explicitly declared in the Manifest.
