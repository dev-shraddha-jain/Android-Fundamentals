# File Handling & Scoped Storage

## Definition
File handling in Android involves reading/writing to the local filesystem. This has changed significantly with the introduction of **Scoped Storage** in Android 10+.

---

## 📂 Storage Locations
1.  **Internal Storage:** App-private files. No permissions needed. Deleted when the app is uninstalled.
2.  **External Storage (Shared):** Media files (Photos, Downloads). Requires Scoped Storage APIs (MediaStore).

## 🛡️ Scoped Storage
Apps are no longer allowed to access the entire SD card using simple file paths (e.g., `/sdcard/DCIM/`). 
*   **The Fix:** Use the `MediaStore` API to insert/query media, or the `Storage Access Framework (SAF)` to let the user pick a specific file or folder.

---

## 🎯 Interview-Ready Answer (Senior)

**Q: How do you save a private configuration file securely?**

**Answer:**
> I use `context.getFilesDir()` to save the file to the app's internal storage. This directory is private to the app and cannot be accessed by other applications. For added security, I might use **EncryptedSharedPreferences** or the **Jetpack Security** library to encrypt the content before saving it.
