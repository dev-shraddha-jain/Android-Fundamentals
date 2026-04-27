# Android Manifest

## Definition
The `AndroidManifest.xml` 
- file is the blueprint of your application.
- declares app components, permissions, features, metadata, intent filters.
- Permissions define what sensitive resources or system capabilities app needs.
- App requests permissions using `uses-permission` tag in manifest.


```xml
<uses-permission android:name="android.permission.CAMERA"/>
```


## 🧠 Core Idea: What's inside?

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Permissions: Requests system access -->
    <uses-permission android:name="android.permission.INTERNET" />

    <application 
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name">

        <!-- 1. Activity: The UI screens -->
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- 2. Service: Background processing -->
        <service 
            android:name=".MyBackgroundService" 
            android:exported="false" />

        <!-- 3. Broadcast Receiver: Listening for system events -->
        <receiver android:name=".MyBootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

        <!-- 4. Content Provider: Data sharing between apps -->
        <provider 
            android:name=".MyDataProvider" 
            android:authorities="com.example.myapp.provider" 
            android:exported="false" />

        <!-- 5. Meta-data: Additional configuration -->
        <meta-data 
            android:name="google_maps_key" 
            android:value="AIzaSyA..." />

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

System checks permission before allowing access.

### Permission Types

1. Normal Permissions
- Low-risk permissions.
- Access features with minimal privacy/security impact.
- Automatically granted at install time.
- No runtime prompt shown to user.
- Examples:
    - INTERNET
    - ACCESS_NETWORK_STATE
    - VIBRATE
    - SET_WALLPAPER
    
2. Dangerous Permissions
- High-risk permissions.
- Access user private data or critical device features.
- Need runtime approval from user (Android 6.0+).
- Examples:
    - CAMERA
    - READ_CONTACTS
    - ACCESS_FINE_LOCATION
    - RECORD_AUDIO
    - READ_MEDIA_IMAGES

### Runtime Permission Flow

- Check permission using ContextCompat.checkSelfPermission()
- If denied → request using requestPermissions()
- Handle result in callback / Activity Result API.

### Interview Answer (Short)
- **Normal permissions** are auto-granted because risk is low.
- **Dangerous permissions** require user consent at runtime because they access sensitive data like camera, contacts, location.

### Security Best Practice
- Ask only required permissions.
- Request permission when feature is used (just-in-time).
- Explain why permission is needed.
- Handle denial gracefully.

## 🎯 Interview-Ready Answer

**Q: What is the risk of setting exported="true" for a Service?**

**Answer:**
> It makes the service public. If the service doesn't perform its own permission checks, any malicious app on the device could start or bind to it, potentially leaking data or executing privileged actions. This is a common entry point for "Intent Redirection" attacks.

---

**Q: What happens if you forget to declare an Activity in the Manifest?**

**Answer:**
> The system will throw an `ActivityNotFoundException` when you try to start it. The Android system only recognizes components that are explicitly declared in the Manifest.
