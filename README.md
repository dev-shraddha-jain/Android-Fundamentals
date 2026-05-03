# 📱 Under-the-Hood Android: The Master Guide

Welcome to the definitive deep dive into Android internals. This repository is a structured knowledge base designed to take you from **Android Basics** to **Senior Architectural Mastery**.

---

## 🧭 Roadmap

### 1. 🏗️ System Architecture & Structure
Understanding the layers beneath the code and how apps are packaged.
- [**⚡ Interview Cheat Sheet (Final Glance)**](Interview_CheatSheet.md) - High-density prep.
- [**Platform Architecture**](android-architecture/PlatformArchitecture.md) - The 5-layer stack and system flow.
- [**Binder IPC Deep Dive**](android-architecture/BinderDeepDive.md) - The OS nervous system.
- [**App Structure (MVVM vs MVI)**](android-architecture/Architecture.md) - Clean architecture principles.
- [**Build & App Structure**](android-architecture/AppStructure.md) - APK vs AAB and compilation process.
- [**Interview QnA (Architecture)**](android-architecture/Interview.md) - Architecture interview prep.

### 2. 📦 Build, Manifest & Resources
- [**Android Manifest**](build-manifest-resources/Manifest.md) - The blueprint and Exported Component security.
- [**Resource Analysis**](build-manifest-resources/Resources.md) - Deep dive into `res/` and `resources.arsc`.
- [**Gradle Deep Dive**](build-manifest-resources/GradleDeepDive.md) - Build lifecycle and optimization.

### 3. 🚀 The Big Four (App Components)
The building blocks of every Android application.
- [**Activity**](android-components/activity/Activity.md) - Lifecycle, Launch Modes, and Task management.
- [**Intents**](intents/Intents.md) - The messaging system and Intent Filters.
- [**Services**](android-components/service/a-service/Service.md) - Background work and Foreground services.
- [**Broadcast Receivers**](android-components/receiver/BroadcastReceiver.md) - Static vs Dynamic receivers.
- [**Content Providers**](android-components/content-provider/ContentProvider.md) - Secure data sharing between apps.
- [**WorkManager**](android-components/service/workmanger/workmanager.md) - Modern deferrable background work.
- [**Service vs WorkManager**](android-components/service/service-workmanager-jobscheduler.md) - Comparison of background task strategies.
- [**Interview QnA (Components)**](android-components/Interview.md) - Merged component QnA.

### 4. 💻 Programming Languages
Mastering the languages that power the framework.
- [**Java & Kotlin Concepts**](programming-languages/) - Deep dives into JVM and Generics.
- [**Coroutines & Flow**](programming-languages/CoroutinesFlow.md) - Concurrency deep dive.
- [**Interoperability**](programming-languages/Interoperability.md) - How Java and Kotlin bridge at the bytecode level.
- [**JNI (Native Interface)**](programming-languages/JNI.md) - Native C++ bridging.
- [**Interview QnA**](programming-languages/Interview.md) - Language internals.

### 5. 💾 Storage
How Android handles persistence.
- [**Storage Methods & File Handling**](storage-deep-dive/) - SharedPrefs, Scoped Storage, Files.
- [**Room & SQLite**](storage-deep-dive/Room-deep-dive.md) - Database deep dives.
- [**Firebase**](storage-deep-dive/Firebase.md) - Cloud storage integration.

### 6. ⚡ Performance & UI
Advanced concepts for senior-level engineering.
- [**Performance Concepts**](performance-optimisation/concepts.md) - Startup times, Baseline profiles, ANRs.
- [**ART Internals**](android-performance/ART_Internals.md) - AOT, JIT, and GC algorithms.
- [**Memory Management**](android-performance/MemoryManagement.md) - Finding Memory Leaks.
- [**Process & LMK**](android-performance/ProcessManagement.md) - How Android kills apps.
- [**UI Rendering**](android-performance/UIRendering.md) - VSync, Choreographer, and RenderThread.
- [**Profiling Guide**](android-performance/Profiling.md) - Using Android Studio Profilers.

### 7. 🛡️ Security & Permissions
Protecting the user and the app.
- [**Android Security**](security/Security.md) - Keystore, Play Integrity, and Encryption.
- [**Permissions Deep-Dive**](security/Permissions.md) - Normal, Dangerous, and Special permissions.
- [**WebView Security**](security/WebView.md) - JS Injection risks and modern fixes.
- [**Code Obfuscation (R8/ProGuard)**](security/ProguardR8.md) - Shrinking and Obfuscation.
- [**Interview QnA (Security)**](security/Interview.md) - Master security interview prep.

### 8. 🧩 Architectural Patterns & Jetpack
- [**Dependency Injection**](android-jetpack/DependencyInjection.md) - Hilt & Dagger internals and code generation.
- [**Jetpack Compose Concepts**](jetpack-compose/ComposeConcepts.md) - Recomposition and State hoisting.
- [**Jetpack Compose Internals**](jetpack-compose/ComposeInternals.md) - SlotTable and Snapshot system.

### 9. 🌐 Networking
- [**Retrofit & Ktor**](networking/) - Modern Android networking stacks.

### 10. 📐 System Design (HLD)
- [**Core Concepts**](system-design/concepts.md) - Scalability, offline sync, caching.
- [**Real-World Examples**](system-design/RealWorldExamples.md) - Designing Image Loaders, Chat apps, etc.

### 11. 🧪 Testing
- [**Unit, Integration, and UI Testing**](testing/) - The testing pyramid.
- [**Interview QnA (Testing)**](testing/interview.md) - Robot Pattern, MockK vs Mockito.

### 12. 🕵️‍♂️ Reverse Engineering
- [**APK Analysis & JADX**](reverse-engg/) - Decompiling and analyzing apps.
- [**Google Play Analysis**](reverse-engg/GooglePlayAnalysis.md) - Store mechanics.

---

### 🎯 Why this guide?

This guide is designed for developers who want to move beyond "building apps" and start understanding the **internal mechanics** of the Android OS. Every section includes consolidated **Interview-Ready Answers** to help you ace senior-level technical rounds.
