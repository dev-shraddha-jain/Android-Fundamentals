# Securing the Android Database

To protect sensitive user data, standard SQLite/Room databases are insufficient because they store data in plain text on the disk. A rooted device or a physical extraction could expose the entire database.

---

## 🔐 1. The Core Engine: SQLCipher
**SQLCipher** is an open-source extension to SQLite that provides transparent 256-bit AES encryption of database files.

- **How it works:** It encrypts every page of the database file. Data is decrypted in memory only when needed and encrypted before being written back to disk.
- **Passphrase:** It requires a password (passphrase) to open the database. If the wrong password is provided, the database appears as garbage data.

## 🔑 2. The Vault: Android Keystore System
Storing the SQLCipher passphrase as a hardcoded string in the code is a major security risk (easily found via reverse engineering). Instead, we use the **Android Keystore**.

### Why Keystore?
- **Hardware Security:** On supported devices, keys are stored in a **Trusted Execution Environment (TEE)** or a **Secure Element (SE)**, making them nearly impossible to extract.
- **Process Isolation:** The key material never enters the application's process memory in its raw form for certain operations.

### The Flow:

1.  **Generate a Key:** Generate a symmetric key (AES) in the Android Keystore when the app first runs.
2.  **Generate a Passphrase:** Create a random, high-entropy string to be the SQLCipher passphrase.
3.  **Encrypt the Passphrase:** Use the Keystore key to encrypt this passphrase.
4.  **Store the Ciphertext:** Save the encrypted passphrase in `SharedPreferences` (or `DataStore`).
5.  **Unlock the DB:** Every time the app starts:
    - Retrieve the ciphertext.
    - Decrypt it using the Keystore.
    - Pass the resulting cleartext passphrase to SQLCipher to open the Room database.

## 🛠️ 3. Implementation Example (Conceptual)

### Room + SQLCipher Integration
Using the `SafeHelperFactory` from the SQLCipher library:

```kotlin
val passphrase = getDecryptedPassphraseFromKeystore()
val factory = SafeHelperFactory(passphrase)

val db = Room.databaseBuilder(context, MyDatabase::class.java, "secure.db")
    .openHelperFactory(factory)
    .build()
```

## 🧠 4. Senior-Level Interview Points

### **Q: Why not just use the Keystore key as the SQLCipher password directly?**
**Answer:**
> While possible, it's better to use the Keystore to wrap (encrypt) a random passphrase. This allows for **Passphrase Rotation** without needing to re-encrypt the entire database. If you change the Keystore key, you only need to re-encrypt the small passphrase string, not the multi-megabyte database file.

### **Q: What is "Key Attestation"?**
**Answer:**
> It's a way for the app to verify that the key it is using truly resides in the device's hardware (TEE/SE) and hasn't been intercepted or emulated by a software-based keystore on a compromised device.

### **Q: Security vs. Performance?**
**Answer:**
> SQLCipher adds a small overhead due to the encryption/decryption of pages. For 99% of apps, this is negligible. However, for extremely large databases with heavy write operations, performance profiling is recommended.

---

## 🚩 Summary Checklist
- [x] Use **SQLCipher** for disk encryption.
- [x] Use **Android Keystore** to store the encryption key.
- [x] Never hardcode passwords.
- [x] Implement a "Clear Data" strategy if the Keystore is invalidated (e.g., user changes lock screen settings).
