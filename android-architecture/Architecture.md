# Android Architecture (HLD)

Android is a sophisticated stack of software designed for performance, security, and battery efficiency.

## 🏗️ The 5-Layer Stack

### 1. Linux Kernel
The foundation. Handles hardware drivers (Camera, WiFi, Audio), memory management, and process scheduling.
*   **Key Concept:** Each app runs in its own Linux process with a unique User ID (UID).

### 2. Hardware Abstraction Layer (HAL)
Provides standard interfaces that expose device hardware capabilities to the higher-level Java API framework.

### 3. Android Runtime (ART) & Native Libraries
*   **ART:** Executes DEX files. Uses AOT and JIT compilation.
*   **Native Libraries:** C/C++ libraries like WebKit, OpenGL, and SQLite.

### 4. Java API Framework
The "Android SDK". Includes Window Manager, Resource Manager, and Activity Manager.

### 5. System Apps
The top layer where your app and system apps live.

---

# 🔍 Process Flow: From App Tap to Screen

```text
User Taps App Icon
       ↓
[ System Server ]
       ↓
[ Zygote Process ]  ← (Warm process waiting to fork)
       ↓
[ Fork New Process ] ← (Creates dedicated PID/UID)
       ↓
[ Load ART & Classes ]
       ↓
[ ActivityThread Main ]
       ↓
[ Attach WindowManager ]
       ↓
[ Render First Frame ]
```

---

# 🎯 Interview-Ready Answer

**Q: Explain the Android Architecture stack.**

**Answer:**
> Android uses a layered architecture. At the bottom is the **Linux Kernel** for hardware management. Above it is the **HAL**, which abstracts hardware for the framework. Then comes the **Native Libraries and ART** which executes the code. The **Java API Framework** provides the services and managers we use to build apps, and the **System Apps** layer sits at the very top.
