# ⚡ Android Senior Interview: Quick Glance Summary

A high-density summary of core Android mechanics for the final 10 minutes before an interview.

🔥 **= Highly Important / Frequently Asked**

---

## 🏗️ 1. System Architecture & Boot
| Topic | Definition | Mechanism / Internal |
| :--- | :--- | :--- |
| 🔥 **Linux Kernel** | The core OS layer. | Handles hardware drivers, memory management (Low Memory Killer), and process isolation. |
| 🔥 **Zygote** | The process incubator. | Pre-loads system classes/resources. Uses `fork()` to create new app processes (CoW - Copy on Write) to save memory and speed up launch. |
| **System Server** | Host of system services. | A process containing AMS (Activity Manager), PMS (Package Manager), WMS (Window Manager). Apps talk to it via **Binder IPC**. |

---

## 🚀 2. The Big Four (Components)
| Component | Definition | Lifecycle Key Points | Internal Mechanism |
| :--- | :--- | :--- | :--- |
| 🔥 **Activity** | Single screen with UI. | `onCreate` → `onStart` → `onResume`. **Destroyed on rotation.** | Hosted in `ActivityRecord` in the System Server. |
| 🔥 **Service** | Background process. | `onStartCommand` (Started), `onBind` (Bound). | Runs on **Main Thread** by default. Use Foreground Service to avoid system kill. |
| **Broadcast Receiver**| Event listener. | `onReceive()` (short execution, max 10s). | Registered via `PMS`. System sends intents to matching UID processes. |
| **Content Provider** | Data sharing bridge. | `onCreate` (first access). | Uses `Cursor` and `UriMatcher`. Handles IPC and cross-app security automatically. |

---

## 🛠️ 3. Core Framework Mechanics
*   🔥 **Binder IPC**: The high-performance communication link between processes. Uses a **Shared Memory** buffer (1MB limit).
*   🔥 **Context**: The "God Object" or Interface to global information. 
    *   *App Context*: Singleton, tied to process. 
    *   *Activity Context*: Tied to UI, can be destroyed (memory leak risk).
*   **Handler/Looper**: The message queue for a thread. `Looper` loops, `Handler` posts messages/runnables to the queue.

---

## ⚡ 4. Performance & Memory
*   🔥 **Memory Management**: 
    *   **Low Memory Killer (LMK)**: Kills processes based on `oom_adj` score (Background first, Foreground last).
    *   **Memory Leaks**: Usually caused by outliving references (e.g., Static Context, anonymous inner classes). Causes GC Thrashing and Jank.
*   **UI Rendering (The 16ms Rule)**:
    *   **Choreographer**: Coordinates VSync signals.
    *   **Overdraw**: System drawing the same pixel multiple times. Aim for 0 or 1 overdraw layers.

---

## 💾 5. Storage & Database
*   🔥 **Room**: SQLite abstraction layer. Uses DAOs, Entities, and `TypeConverters`. Always use asynchronous operations (`suspend` functions).
*   **Scoped Storage**: Isolates apps to their own folders for Privacy. Requires `MediaStore` for shared media.
*   **EncryptedSharedPreferences**: Used for storing sensitive, small data like refresh tokens (AES-256 encrypted via Android Keystore).

---

## 🔐 6. Security & Build
*   🔥 **Application Sandbox**: Each app has its own UID. Apps cannot see each other's memory or files without permissions.
*   🔥 **Permissions**: *Normal* (Auto-granted) vs *Dangerous* (Runtime user approval).
*   **Proguard/R8**: **Tree Shaking** (stripping dead code) and **Obfuscation** (renaming classes to `a, b, c`). `mapping.txt` is required to de-obfuscate crash logs.
*   **WebView Security**: Never expose sensitive APIs via Javascript Bridge (`addJavascriptInterface`). Validate origins to prevent XSS privilege escalation.

---

## 💻 7. Programming (Kotlin/Java)
*   🔥 **Coroutines**: Lightweight threads. Uses `suspend` to pause execution without blocking the underlying thread.
*   🔥 **Structured Concurrency**: Ensuring child coroutines are completed before the parent finishes. Managed via `CoroutineScope` and `Job`.
*   **Flow**: Asynchronous stream of data. Cold (emits only on collection) vs. Hot (`StateFlow`/`SharedFlow`, emits regardless of observers).
*   **JNI**: Java Native Interface. Crossing the boundary to C++ is expensive and requires marshaling.

---

## 🧩 8. Architecture, DI & Compose
*   🔥 **MVVM / MVI**: Separation of concerns. ViewModel survives rotation but NOT process death. Repository pattern acts as single source of truth.
*   🔥 **Jetpack Compose**: Declarative UI. 
    *   *Recomposition*: Redrawing UI when State changes.
    *   *State Hoisting*: Moving state up to make stateless components reusable.
*   **Dependency Injection (Hilt/Dagger)**: Compile-time validation. Scopes dictate lifetime (e.g., `@Singleton` vs `@ActivityScoped`).

---

## 🌐 9. System Design (HLD) & Networking
*   🔥 **Offline Sync / Caching**: Use Room as single source of truth. Fetch from API -> Save to DB -> UI observes DB. For uploads, use WorkManager with constraints.
*   🔥 **Pagination**: Load data in chunks. Use Paging 3 library to handle remote mediators and local caching automatically.
*   **Retrofit + OkHttp**: Use Interceptors for adding Auth headers globally. Use Certificate Pinning (`CertificatePinner`) to prevent MITM attacks.

---

## 🧪 10. Testing & Reverse Engineering
*   🔥 **Testing Pyramid**: 70% Unit (JVM, MockK/Fakes), 20% Integration (Robolectric/Room), 10% UI (Espresso/UIAutomator).
*   **Fakes vs Mocks**: Fakes are preferred for Repositories (cleaner state tracking), Mocks for verifying exact interactions (e.g., Analytics).
*   **Reverse Engineering**: Attackers use JADX to read Smali/Java code. Defense involves R8 Obfuscation, Tamper Detection, and Server-Side validation (Play Integrity API).

---

## 🎯 Final Tricky "What If" Checklist
- [ ] 🔥 **What if Activity is killed in background?** UI state is saved in `Bundle` (SavedInstanceState), but non-persistent data is lost.
- [ ] **What if you start a network call in `onStartCommand` of a Service?** App crashes (`NetworkOnMainThreadException`). Services run on Main Thread!
- [ ] 🔥 **What if you rotate the screen?** Activity dies entirely. ViewModel stays alive. `onCreate` is called again.
- [ ] **What if JNI blocks Main Thread?** App will ANR. Native code is NOT magic; it still runs on the thread it was called from.
- [ ] **What if you forget `@ActivityScoped` in Hilt?** You get a new instance every time, which wastes memory and breaks shared state.
