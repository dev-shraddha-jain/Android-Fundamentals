# Firebase for Android (Cloud Storage)

## Definition
Firebase is a platform by Google that provides several cloud-based storage solutions for Android, primarily **Firestore** (NoSQL) and **Realtime Database**.

---

## ☁️ Storage Options
*   **Cloud Firestore:** A flexible, scalable NoSQL cloud database to store and sync data for client- and server-side development. It supports complex queries and offline data persistence.
*   **Realtime Database:** A legacy NoSQL database where data is stored as JSON and synced in realtime across all clients. Best for simple apps with high-frequency updates.
*   **Firebase Storage:** Used for storing large binary files like images, videos, and audio.

## 🔐 Security Rules
One of the most important concepts in Firebase is **Security Rules**. Since the client talks directly to the database, you must define rules to prevent unauthorized access.

```text
allow read, write: if request.auth != null;
```

---

## 🎯 Interview-Ready Answer (Senior)

**Q: Why would you choose Firestore over Realtime Database for a large app?**

**Answer:**
> Firestore offers much better query capabilities, allowing you to filter and sort data across multiple fields. It also scales better globally because it's a distributed database. Realtime Database is a single JSON tree, which makes complex queries and large-scale data management difficult as the app grows.
