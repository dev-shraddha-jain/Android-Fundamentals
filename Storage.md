# Storage Options

Android provides several ways to save persistent data.

## 💾 Comparison

| Option | Best For |
| :--- | :--- |
| **Shared Preferences** | Small settings (Key-Value) |
| **Internal Storage** | Private app files |
| **External Storage** | Shared media (Photos) |
| **Room Database** | Structured, searchable data |

## 🔗 Real-World Process: Scoped Storage

```text
[ App Requests File Access ]
             ↓
     Is it App-Private?
     ↙               ↘
  [ YES ]          [ NO ]
    ↓                ↓
[ Access Granted ] [ System Check ]
(No permission     (Scoped Storage)
 needed)             ↓
               [ MediaStore API ]
                     ↓
               [ User Approval ]
```

## 🧠 Core Idea
> **Shared Preferences:** Use `apply()` for asynchronous saves (better performance) and `commit()` for synchronous saves (rarely needed).

## 🎯 Interview-Ready Answer

**Q: What is Scoped Storage?**

**Answer:**
> Introduced in Android 10, it restricts apps to their own private directories. To access shared files like photos, apps must use the `MediaStore` API or `Storage Access Framework` instead of direct file paths.
