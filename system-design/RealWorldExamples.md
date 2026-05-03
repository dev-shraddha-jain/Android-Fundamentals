# 📐 Real-World System Design (Android Specific)

In senior interviews, you are often asked to design a complex feature or library. These questions test your understanding of architecture, threading, and persistence.

---

### 1. Designing an Image Loading Library (like Glide/Coil)
**Goal:** Efficiently fetch, decode, and display images while maintaining 60 FPS.

**Key Components:**
*   **Request Manager:** Handles the lifecycle (cancelling requests when an Activity is destroyed).
*   **Engine:** Orchestrates the fetching and caching logic.
*   **Memory Cache:** (LruCache) Stores decoded Bitmaps for instant access.
*   **Disk Cache:** (DiskLruCache) Stores original or resized images to avoid network calls.
*   **Fetcher/Decoder:** Handles network (OkHttp) and decoding (`BitmapFactory`).

**Critical Considerations:**
*   **Bitmap Pooling:** Reuse Bitmap objects to avoid frequent GC and `OutOfMemoryError`.
*   **Downsampling:** Never load a 4K image into a 100x100 ImageView. Decode to the required size.
*   **Threading:** Fetching on IO threads, Decoding on Default threads, Displaying on the Main thread.

---

### 2. Designing an Offline-First News App
**Goal:** The app should work seamlessly without a network and sync data when online.

**Key Components:**
*   **Remote Data Source:** Retrofit for API calls.
*   **Local Data Source:** Room Database as the Single Source of Truth.
*   **Repository:** The "brain" that decides whether to fetch from the network or database.
*   **WorkManager:** For background periodic syncing of news.
*   **UI (Compose/XML):** Observes the database (via Flow/LiveData).

**The Flow:**
1.  UI requests data → Repository returns data from Room immediately.
2.  Repository triggers a background network fetch.
3.  Network data arrives → Repository saves it to Room.
4.  Room (via Flow) automatically notifies the UI to update.

---

### 3. Designing a Real-time Chat App
**Goal:** Low latency messaging with delivery status.

**Key Components:**
*   **Connection Layer:** WebSockets (using OkHttp or Ktor) for two-way real-time communication.
*   **Fall-back:** Long polling or FCM (Firebase Cloud Messaging) for background notifications.
*   **Local Storage:** Encrypted Room database to store chat history.
*   **Attachment Handling:** Uploading files to S3/Cloud Storage and sending the URI in the chat message.

**Critical Considerations:**
*   **Message Sequencing:** Handling messages that arrive out of order (using timestamps or sequence IDs).
*   **Connection Resilience:** Automatic reconnection logic with exponential backoff.
*   **Security:** End-to-End Encryption (E2EE) using the Android Keystore.

---

### 🎯 Senior Interview QnA

#### Q: How would you handle a "Search" feature that hits an API as the user types?
**Answer:**
I would use the `debounce` operator in Kotlin Flow.
1.  Collect text changes from the search field.
2.  Apply `debounce(300ms)` to wait until the user stops typing for a brief moment.
3.  Use `distinctUntilChanged()` to avoid duplicate requests for the same query.
4.  Use `flatMapLatest` (or `switchMap`) to cancel any previous search request if a new one is triggered.

#### Q: What is the "Single Source of Truth" (SSOT) pattern?
**Answer:**
It's a principle where all UI data comes from one place (usually the local database). The network is used only to *update* the database. This ensures that the UI is always consistent, works offline, and handles data updates predictably across different screens.
