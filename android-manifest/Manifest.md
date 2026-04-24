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

## 🎯 Interview-Ready Answer

**Q: What happens if you forget to declare an Activity in the Manifest?**

**Answer:**
> The system will throw an `ActivityNotFoundException` when you try to start it. The Android system only recognizes components that are explicitly declared in the Manifest.
