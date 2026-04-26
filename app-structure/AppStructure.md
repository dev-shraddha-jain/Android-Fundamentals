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
> AAB (Android App Bundle) reduces the download size for users. Unlike a "Fat APK" that contains all languages, screen densities, and CPU architectures, the App Bundle allows Google Play to serve only the specific resources needed for the user's device, often reducing app size by 20-50%.
