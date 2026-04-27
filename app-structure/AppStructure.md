# Application Structure (APK vs AAB)

## Definition
An **APK (Android Package Kit)** is the final executable file used to install an app on an Android device. An **AAB (Android App Bundle)** is a publishing format that includes all your compiled code and resources, but defers APK generation and signing to Google Play.

## 📦 APK Internal Structure

> **💡 Pro Tip:** You can manually inspect the contents of an APK by changing its extension from `.apk` to `.zip` and extracting it. This is the simplest way to see how an Android app is structured under the hood.


If you unzip an APK, you will find these core 
components:

| Component | Description |
| :--- | :--- |
| **classes.dex** | Compiled Java/Kotlin code in Dalvik Executable format. |
| **res/** | Contains resources not compiled into `resources.arsc` (e.g., layouts, drawables). |
| **resources.arsc** | A binary file containing pre-compiled resources (strings, colors, IDs). |
| **AndroidManifest.xml** | Binary version of the manifest file. |
| **lib/** | Native libraries compiled for specific architectures (armeabi-v7a, arm64-v8a, x86). |
| **assets/** | Raw files accessible via `AssetManager` (e.g., fonts, game data). |
| **META-INF/** | Contains the app's signing certificates and manifest signatures. |

## 🔍 Real-World Process: Dynamic Delivery (AAB)

```text
[ Developer Uploads AAB ]
           ↓
   [ Google Play Store ]
           ↓
   [ Generates Optimized APKs ]
    ↙          ↓           ↘
[ Device A ] [ Device B ] [ Device C ]
(English,    (Hindi,      (Spanish,
 xhdpi,       mdpi,        xxhdpi,
 arm64)       x86)         armv7)
```

## 🧠 Core Idea: Resource Compilation
Why is there a `resources.arsc`? 
XML files are slow to parse at runtime. During build, Android:
1.  **Compresses** XML into binary format.
2.  **Generates IDs** (e.g., `0x7f040001`) for every resource.
3.  **Maps** these IDs to values in `resources.arsc` for lightning-fast lookup.

## 🎯 Interview-Ready Answer

**Q: Why should I use AAB instead of APK for publishing?**

**Answer:**
> **AAB (Android App Bundle)** is the modern publishing format that replaces the traditional APK for the Play Store. It is more than just a size reduction tool; it represents a shift in how apps are delivered:
>
> 1. **Dynamic Delivery (Split APKs):** Instead of a single "Fat APK," Google Play uses the bundle to generate a **Base APK** (core logic) and multiple **Configuration APKs** (specific to the user's language, screen density, and CPU architecture). The user only downloads what their device actually uses.
> 2. **Size Optimization:** By stripping out irrelevant resources, apps are typically **20-50% smaller**, leading to higher install conversion rates and fewer uninstalls due to storage issues.
> 3. **Dynamic Feature Modules:** Developers can modularize their apps to deliver specific features **on-demand** (e.g., a heavy "Camera Filter" module that is only downloaded when the user first clicks it) or conditionally (based on device capabilities like AR support).
> 4. **Play App Signing:** To use AAB, you must use Play App Signing. Google manages your app's signing key, protecting you if you lose your local upload key and allowing Google to optimize and re-sign your APKs for delivery.
> 5. **Mandatory Requirement:** As of August 2021, all **new apps** are required to publish using the AAB format.

