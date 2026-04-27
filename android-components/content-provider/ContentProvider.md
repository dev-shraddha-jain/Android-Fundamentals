# Content Providers

## Definition
A standard interface that connects data in one process with code running in another process.

## 💻 Code Example (Querying)

```kotlin
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null, null, null, null
)
```

## 🔍 Real-World Process: Data Sharing

```text
  [ Client App ]
        ↓
  [ ContentResolver ]
        ↓
  [ URI Matching ] (e.g., content://contacts)
        ↓
  [ Target App's ContentProvider ]
        ↓
  [ Database/Files ]
        ↓
  [ Returns Cursor ]
```

### 🎬 Interactive Mechanism Walkthrough

<iframe src="content_provider_mechanism.html" width="100%" height="450px" style="border:none; border-radius: 8px; margin: 1.5rem 0;"></iframe>


For more examples, refer to [example.md](example.md).

## 🧠 Core Idea
> It’s a security layer. Instead of giving another app direct access to your database file, you provide a URI and handle the query yourself.

## 🎯 Interview-Ready Answer

**Q: Why use a Content Provider instead of a direct DB link?**

**Answer:**
> It provides a layer of abstraction and security. It allows data sharing across different processes while enforcing permissions and preventing direct file system access by other apps.
