# 📱 Under-the-Hood Android: The Master Guide

Welcome to the definitive deep dive into Android internals. This repository is a structured knowledge base designed to take you from **Android Basics** to **Senior Architectural Mastery**.

---

## 🧭 Roadmap

### 1. 🏗️ System Architecture & Structure

Understanding the layers beneath the code and how apps are packaged.

- [**Platform Architecture**](android-architecture/Architecture.md) - The 5-layer stack and system flow.
- [**Build & App Structure**](app-structure/AppStructure.md) - APK vs AAB, DEX files, and Resource compilation.
- [**Resource Analysis**](android-manifest/resources/Resources.md) - Deep dive into `res/` and `resources.arsc`.
- [**Android Manifest**](android-manifest/Manifest.md) - The blueprint and Exported Component security.

### 2. 🚀 The Big Four (App Components)

The building blocks of every Android application.

- [**Activity**](android-components/activity/Activity.md) - Lifecycle, Launch Modes, and Task management.
- [**Intents**](intents/Intents.md) - The messaging system and Intent Filters.
- [**Services**](android-components/service/a-service/Service.md) - Background work and Foreground services.
- [**Broadcast Receivers**](android-components/receiver/BroadcastReceiver.md) - Static vs Dynamic receivers.
- [**Content Providers**](android-components/content-provider/ContentProvider.md) - Secure data sharing between apps.
- [**WorkManager**](android-components/service/workmanger/workmanager.md) - Modern deferrable background work.
- [**App Without An Activity?**](android-components/service/serviceApp.md) - Pure background process logic.
- [**Service vs WorkManager**](android-components/service/service-workmanager-jobscheduler.md) - Comparison of background task strategies.
- [**Service Security Risks**](android-components/service/a-service/security-risks.md) - Exported components and vulnerability fixes.

### 3. 💻 Programming Languages

Mastering the languages that power the framework.

- [**Java Concepts**](programming-languages/JavaConcepts.md) - JVM, GC, and Reference Types.
- [**Kotlin Concepts**](programming-languages/KotlinConcepts.md) - Coroutines, Extensions, and Generics Variance.
- [**Interoperability**](programming-languages/Interoperability.md) - How Java and Kotlin bridge at the bytecode level.

### 4. 💾 Storage & Permissions

How Android handles persistence and user privacy.

- [**Storage Methods**](storage-deep-dive/Storage.md) - SharedPrefs, Room, and the Scoped Storage model.
- [**Permissions Deep-Dive**](android-manifest/permissions/Permissions.md) - Normal, Dangerous, and Special permissions.

### 5. 🛠️ Performance & Security

Advanced concepts for senior-level engineering.

- [**Memory Management**](android-performance/MemoryManagement.md) - ART GC, Heap/Stack, and finding Memory Leaks.
- [**UI Rendering**](android-performance/UIRendering.md) - VSync, Choreographer, and RenderThread.
- [**JNI & NDK**](programming-languages/JNI.md) - Native C++ bridging and Direct ByteBuffers.
- [**Code Obfuscation**](obfuscate/ProguardR8.md) - R8 internals, Mapping files, and Keep rules.
- [**WebView Security**](android-components/activity/WebView.md) - JS Injection risks and modern fixes.

### 🧩 Architectural Patterns

- [**Dependency Injection**](android-jetpack/DependencyInjection.md) - Hilt & Dagger internals.

---

### 🎯 Why this guide?

This guide is designed for developers who want to move beyond "building apps" and start understanding the **internal mechanics** of the Android OS. Every section includes **Interview-Ready Answers** (Interview.md) to help you ace senior-level technical rounds.
