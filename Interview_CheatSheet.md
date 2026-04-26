# ⚡ Android Senior Interview: Quick Glance Summary

A high-density summary of core Android mechanics for the final 10 minutes before an interview.

---

## 🏗️ 1. System Architecture & Boot
| Topic | Definition | Mechanism / Internal |
| :--- | :--- | :--- |
| **Linux Kernel** | The core OS layer. | Handles hardware drivers, memory management (Low Memory Killer), and process isolation. |
| **Zygote** | The process incubator. | Pre-loads system classes/resources. Uses `fork()` to create new app processes (CoW - Copy on Write) to save memory and speed up launch. |
| **System Server** | Host of system services. | A process containing AMS (Activity Manager), PMS (Package Manager), WMS (Window Manager). Apps talk to it via **Binder IPC**. |

---

## 🚀 2. The Big Four (Components)
| Component | Definition | Lifecycle Key Points | Internal Mechanism |
| :--- | :--- | :--- | :--- |
| **Activity** | Single screen with UI. | `onCreate` → `onStart` → `onResume`. **Destroyed on rotation.** | Hosted in `ActivityRecord` in the System Server. |
| **Service** | Background process. | `onStartCommand` (Started), `onBind` (Bound). | Runs on **Main Thread** by default. Use Foreground Service to avoid system kill. |
| **Broadcast Receiver**| Event listener. | `onReceive()` (short execution, max 10s). | Registered via `PMS`. System sends intents to matching UID processes. |
| **Content Provider** | Data sharing bridge. | `onCreate` (first access). | Uses `Cursor` and `UriMatcher`. Handles IPC and cross-app security automatically. |

---

## 🛠️ 3. Core Framework Mechanics
*   **Binder IPC**: The high-performance communication link between processes. Uses a **Shared Memory** buffer (1MB limit).
*   **Context**: The "God Object" or Interface to global information. 
    *   *App Context*: Singleton, tied to process. 
    *   *Activity Context*: Tied to UI, can be destroyed.
*   **Handler/Looper**: The message queue for a thread. `Looper` loops, `Handler` posts messages/runnables to the queue.

---

## ⚡ 4. Performance & Memory
*   **Memory Management**: 
    *   **Low Memory Killer (LMK)**: Kills processes based on `oom_adj` score (Background first, Foreground last).
    *   **ART vs. JVM**: ART uses AOT (Ahead-of-Time) or JIT with Profile-guided optimization to convert DEX to native machine code.
*   **UI Rendering (The 16ms Rule)**:
    *   **Choreographer**: Coordinates VSync signals.
    *   **Overdraw**: System drawing the same pixel multiple times. Aim for 0 or 1 overdraw layers.

---

## 🔐 5. Security & Build
*   **Application Sandbox**: Each app has its own UID. Apps cannot see each other's memory or files without permissions.
*   **Permissions**: 
    *   *Normal*: Auto-granted. 
    *   *Dangerous*: Runtime user approval.
*   **Proguard/R8**: **Tree Shaking** (stripping dead code) and **Obfuscation** (renaming classes to `a, b, c`).
*   **DEX (Dalvik Executable)**: Optimized bytecode for Android. Multi-DEX is used when the 65k method limit is reached.

---

## 💻 6. Programming (Kotlin/Coroutines)
*   **Coroutines**: Lightweight threads. Uses `suspend` to pause execution without blocking the underlying thread.
*   **Structured Concurrency**: Ensuring child coroutines are completed before the parent finishes. Managed via `CoroutineScope` and `Job`.
*   **Flow**: Asynchronous stream of data. Cold (emits only on collection) vs. Hot (emits regardless of observers).

---

## 🎯 Final Tricky "What If" Checklist
- [ ] **What if Activity is killed in background?** UI state is saved in `Bundle` (SavedInstanceState), but non-persistent data is lost.
- [ ] **What if JNI blocks Main Thread?** App will ANR. Native code is NOT magic; it still runs on the thread it was called from.
- [ ] **What if you forget `@ActivityScoped` in Hilt?** You get a new instance every time, which wastes memory and breaks shared state.
