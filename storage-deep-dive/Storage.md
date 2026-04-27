# Storage Options

Android provides several ways to save persistent data.

## 💾 Comparison

| Option | Best For |
| :--- | :--- |
| **Shared Preferences** | Small settings (Key-Value) |
| **DataStore** | Modern, Type-safe settings (Proto/Preferences) |
| **Internal Storage** | Private app files |
| **External Storage** | Shared media (Photos) |
| **Room Database** | Structured, searchable data |

---


## 🧠 Core Ideas & Security

### 1. Shared Preferences: `apply()` vs. `commit()`
When saving data, you have two choices:
*   **`apply()` (Preferred):** Asynchronous. It writes to the in-memory cache immediately but saves to disk in the background. It doesn't return a status and won't block the UI thread.
*   **`commit()`:** Synchronous. It writes to disk immediately and returns a boolean (true if successful). **Warning:** This can block the main thread and cause jank.

### 2. EncryptedSharedPreferences
For sensitive data (tokens, PII), use **Jetpack Security**.
*   It encrypts both **keys** and **values**.
*   Uses the **Android Keystore System** to manage encryption keys.
*   Implementation: `EncryptedSharedPreferences.create(...)`.
---


## 📂 Deep Dives
For advanced implementation and senior-level concepts, see the dedicated guides:
*   [**SQLite & Room Deep Dive**](SQLite.md)
*   [**Firebase Cloud Storage**](Firebase.md)
*   [**File Handling & Scoped Storage**](FileHandling.md)


## 🎯 Interview-Ready Answer

**Q: What is Scoped Storage?**

**Answer:**
> Introduced in Android 10, it restricts apps to their own private directories. To access shared files like photos, apps must use the `MediaStore` API or `Storage Access Framework` instead of direct file paths.
