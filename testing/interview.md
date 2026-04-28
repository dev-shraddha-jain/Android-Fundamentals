# Testing & Security — Interview Q&A

---

## Testing Interview Questions

### Q1. What is the testing pyramid and why does it matter?

> The testing pyramid has **Unit Tests** at the base (fast, JVM, isolated), **Integration Tests** in the middle (Room + Retrofit, emulator), and **UI/E2E Tests** at the top (slow, full device). The rule is 70/20/10 — most coverage through unit tests, least through UI tests. An inverted pyramid (mostly UI tests) is an anti-pattern: it's slow, flaky, and expensive to maintain.

---

### Q2. How do you test a ViewModel with coroutines?

> You need to replace `Dispatchers.Main` with a `TestCoroutineDispatcher` using a `TestWatcher` rule. Then use `runTest {}` to run the coroutine synchronously. For `StateFlow` emissions, use the Turbine library — `vm.uiState.test { awaitItem() }` — to assert each emitted state in order.

---

### Q3. Fake vs Mock — which do you prefer for repositories?

> I prefer **Fakes** for repositories because repositories often return `Flow`, and mocking a cold flow with Mockito/MockK is verbose and error-prone. A handwritten `FakeUserRepository` with simple state fields (`userToReturn`, `shouldThrowError`) is far more readable and maintainable. I use **Mocks** when I need to verify that a specific method was called exactly N times, like confirming `analyticsService.logEvent()` was invoked on a button click.

---

### Q4. How do you test Room DAOs?

> Use `Room.inMemoryDatabaseBuilder()` in an `AndroidJUnit4` test. An in-memory database is real SQLite — it validates your actual queries. Call `allowMainThreadQueries()` only in tests. Use Turbine to test `Flow<List<T>>` DAOs so you can observe multiple emissions as data changes.

---

## Security Interview Questions

### Q1. Where do you store auth tokens?

> Access tokens (short-lived, 15 min) live in-memory in the ViewModel — they're cleared when the app is killed. Refresh tokens (long-lived) are stored in `EncryptedSharedPreferences` backed by an AES-256-GCM key in the Android Keystore. We never store any token in plain `SharedPreferences`, a file, or `BuildConfig`.

---

### Q2. How does SSL Pinning work and what are its risks?

> SSL Pinning hardcodes the server's certificate public key hash in the app using `CertificatePinner`. On each HTTPS handshake, OkHttp verifies the server's presented certificate matches the pinned hash — rejecting any other certificate, even a valid CA-signed one. The main risk is **certificate rotation**: if the server renews its certificate and the app's pins aren't updated before the old cert expires, the app loses all connectivity. Mitigation: always pin **two hashes** (current + backup), set an expiry, and use Network Security Config XML which can be updated via OTA without a full release.

---

### Q3. What is the Play Integrity API and when do you use it?

> The Play Integrity API provides **server-side attestation** from Google. The client app requests a signed token from Google, then your backend verifies it by calling Google's API. The response gives three verdicts: is the app signed by your key (`APP_INTEGRITY`), is the device genuine Android with Google Play (`DEVICE_INTEGRITY`), and is the user licensed (`ACCOUNT_DETAILS`). I use it before high-value actions like payment confirmation or account creation — it cannot be bypassed client-side since verification happens server-to-server.

---

### Q4. How do you prevent reverse engineering of your APK?

> **R8 obfuscation** renames classes and methods to meaningless single characters. **ProGuard rules** strip debug logs, keep serialization models intact, and protect Hilt-generated classes. For native code, we use NDK with `.so` files which are harder to decompile than DEX. Beyond obfuscation, we use **tamper detection** (checking the APK signature at runtime) and **Play Integrity API** for server-side validation, since obfuscation alone can be defeated by a patient attacker.

---

### Q5. How do you detect a rooted device?

> Client-side: check for `/system/bin/su`, build tags containing `test-keys`, known root manager package names (Magisk, SuperSU), and writable system partitions. However, Magisk Hide can bypass all of these checks. The real solution is **Play Integrity API** — the `MEETS_DEVICE_INTEGRITY` verdict is computed on Google's servers and is significantly harder to spoof. We use both layers: client-side for UX (warn the user early) and server-side for enforcement (block the transaction).