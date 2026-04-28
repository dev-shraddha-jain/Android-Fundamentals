# Android Security (Expert Level)

---

## 1. Android Keystore

**Definition:** A hardware-backed system facility for generating and storing cryptographic keys. Keys stored in the Keystore can **never be extracted** from the device — cryptographic operations happen inside a secure enclave (TEE / StrongBox), not in app memory.

**When to use:** Generating signing keys, encryption keys for local data, any operation where the key must not leave the device.

**Example Code:**
```kotlin
// Generate an AES key inside the Keystore
val keyGenSpec = KeyGenParameterSpec.Builder(
    "my_key_alias",
    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
).apply {
    setBlockModes(KeyProperties.BLOCK_MODE_GCM)
    setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
    setKeySize(256)
    setUserAuthenticationRequired(false) // set true to require biometric
}.build()

val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
keyGenerator.init(keyGenSpec)
val secretKey = keyGenerator.generateKey()

// Encrypt data using the Keystore-backed key
val cipher = Cipher.getInstance("AES/GCM/NoPadding")
cipher.init(Cipher.ENCRYPT_MODE, secretKey)
val iv = cipher.iv
val encrypted = cipher.doFinal("sensitive_data".toByteArray())

// Decrypt
val keyStore = KeyStore.getInstance("AndroidKeyStore").also { it.load(null) }
val key = keyStore.getKey("my_key_alias", null)
val decryptCipher = Cipher.getInstance("AES/GCM/NoPadding")
decryptCipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, iv))
val decrypted = String(decryptCipher.doFinal(encrypted))
```

**Real World Example:** Banking apps use the Keystore to encrypt the session token. Even if the device is rooted or the APK is extracted, the key cannot be obtained — it lives exclusively in the TEE.

---

## 2. EncryptedSharedPreferences

**Definition:** A Jetpack Security wrapper over `SharedPreferences` that transparently encrypts both **keys** (AES-256-SIV) and **values** (AES-256-GCM). Backed by an Android Keystore master key.

**When to use:** Auth tokens, refresh tokens, user session data, feature flags with sensitive values — any small key-value pair that must not be readable on a rooted device.

**Example Code:**
```kotlin
// Create the master key in the Keystore
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

// Create encrypted prefs
val securePrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Use exactly like regular SharedPreferences
securePrefs.edit()
    .putString("auth_token", token)
    .putLong("token_expiry", expiresAt)
    .apply()

val token = securePrefs.getString("auth_token", null)
```

**Real World Example:** A fintech app stores the JWT access token and refresh token in `EncryptedSharedPreferences` so they remain protected even if the device falls into the wrong hands.

---

## 3. Root Detection

**Definition:** Detecting whether the device has been rooted (superuser access granted). Rooted devices can bypass app sandbox isolation, read app private files, hook methods via Frida, or modify memory. Production banking/payment apps must detect and restrict functionality on rooted devices.

**When to use:** Banking, payments, healthcare — any app handling PII or financial data.

**Example Code:**
```kotlin
object RootDetector {
    fun isDeviceRooted(): Boolean {
        return checkSuBinary() || checkBuildTags() || checkRootPaths() || checkRootApps()
    }

    private fun checkSuBinary(): Boolean {
        val paths = listOf("/system/bin/su", "/system/xbin/su", "/sbin/su", "/su/bin/su")
        return paths.any { File(it).exists() }
    }

    private fun checkBuildTags(): Boolean {
        return Build.TAGS?.contains("test-keys") == true
    }

    private fun checkRootPaths(): Boolean {
        val rootPaths = listOf(
            "/system/app/Superuser.apk",
            "/data/local/tmp/su",
            "/system/bin/.ext/.su"
        )
        return rootPaths.any { File(it).exists() }
    }

    private fun checkRootApps(): Boolean {
        val rootPackages = listOf(
            "com.noshufou.android.su",
            "eu.chainfire.supersu",
            "com.topjohnwu.magisk"
        )
        val pm = context.packageManager
        return rootPackages.any {
            runCatching { pm.getPackageInfo(it, 0); true }.getOrDefault(false)
        }
    }
}

// Usage in Activity
if (RootDetector.isDeviceRooted()) {
    showDialog("Rooted device detected. App functionality is restricted.")
    finish()
}
```

> ⚠️ **Note:** Root detection alone can be bypassed by advanced attackers using Magisk Hide. Combine with the **Play Integrity API** for server-side attestation.

---

## 4. SSL Pinning

**Definition:** Validating the server's TLS certificate against a known public key hash hardcoded in the app. Prevents MITM attacks even when the device's CA store is compromised (rogue CA, corporate proxy).

**When to use:** Banking, fintech, healthcare — required by OWASP MASVS L2.

**Example Code:**
```kotlin
// Get the hash: openssl s_client -connect api.example.com:443 | openssl x509 -pubkey -noout | openssl rsa -pubin -outform der | openssl dgst -sha256 -binary | base64

val pinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=") // current cert
    .add("api.example.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=") // backup cert
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(pinner)
    .build()

// Using Network Security Config (XML alternative — no code change needed for updates)
// res/xml/network_security_config.xml:
// <network-security-config>
//   <domain-config>
//     <domain includeSubdomains="true">api.example.com</domain>
//     <pin-set>
//       <pin digest="SHA-256">AAAAAAA...</pin>
//       <pin digest="SHA-256">BBBBBBB...</pin>  <!-- backup -->
//     </pin-set>
//   </domain-config>
// </network-security-config>
```

> ⚠️ **Always include a backup pin** and a pin rotation plan before shipping. A broken pin with no backup = users cannot reach your server.

---

## 5. Obfuscation — ProGuard / R8

**Definition:** R8 (Google's replacement for ProGuard) performs code shrinking, optimization, and name obfuscation during APK release build. Class names, method names, and field names are renamed to meaningless single characters, making reverse engineering much harder.

**When to use:** Every production release build.

**Example Code:**
```proguard
# proguard-rules.pro

# Keep data classes used for serialization (Gson/Moshi)
-keep class com.example.app.data.model.** { *; }

# Keep Retrofit API interfaces
-keep interface com.example.app.data.api.** { *; }

# Keep Hilt-generated classes
-keep class * extends dagger.hilt.android.internal.** { *; }

# Remove logging in release builds
-assumenosideeffects class android.util.Log {
    public static boolean isLoggable(java.lang.String, int);
    public static int d(...);
    public static int v(...);
    public static int i(...);
}
```

**In `build.gradle`:**
```kotlin
buildTypes {
    release {
        isMinifyEnabled = true      // enables R8 shrinking + obfuscation
        isShrinkResources = true    // removes unused resources
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
```

---

## 6. Tamper Detection

**Definition:** Detecting if the APK's signature has been modified — indicating a repackaged or cracked version of the app. Repackaged apps are common attack vectors to inject malware or remove security checks.

**When to use:** Any production app, especially those with in-app purchases or licence checks.

**Example Code:**
```kotlin
object TamperDetector {
    // Compute at build time and hardcode:
    // keytool -printcert -jarfile app-release.apk | grep SHA256
    private const val EXPECTED_SIGNATURE = "YOUR_RELEASE_SIGNATURE_SHA256"

    fun isAppTampered(context: Context): Boolean {
        return try {
            val packageInfo = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                context.packageManager.getPackageInfo(
                    context.packageName,
                    PackageManager.GET_SIGNING_CERTIFICATES
                )
            } else {
                @Suppress("DEPRECATION")
                context.packageManager.getPackageInfo(context.packageName, PackageManager.GET_SIGNATURES)
            }

            val signatures = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                packageInfo.signingInfo.apkContentsSigners
            } else {
                @Suppress("DEPRECATION")
                packageInfo.signatures
            }

            val md = MessageDigest.getInstance("SHA-256")
            val actualSignature = Base64.encodeToString(
                md.digest(signatures[0].toByteArray()), Base64.DEFAULT
            ).trim()

            actualSignature != EXPECTED_SIGNATURE
        } catch (e: Exception) {
            true // assume tampered on error
        }
    }
}
```

---

## 7. Secure Logging

**Definition:** Preventing sensitive data (tokens, PII, card numbers) from appearing in logs. Android's `logcat` is readable by other apps with `READ_LOGS` permission on older devices. In release builds, all debug logs must be stripped.

**When to use:** Every app — especially those handling financial or health data.

**Example Code:**
```kotlin
// Timber — automatically strips debug logs in release
class ReleaseTree : Timber.Tree() {
    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
        if (priority == Log.VERBOSE || priority == Log.DEBUG) return // stripped in release
        // Route WARN/ERROR to crash reporter only
        if (priority >= Log.WARN) {
            FirebaseCrashlytics.getInstance().log("$tag: $message")
            t?.let { FirebaseCrashlytics.getInstance().recordException(it) }
        }
    }
}

// App.onCreate()
if (BuildConfig.DEBUG) {
    Timber.plant(Timber.DebugTree())
} else {
    Timber.plant(ReleaseTree()) // safe in production
}

// Never log sensitive values:
Timber.d("User logged in: ${user.name}")  // ✅ OK
Timber.d("Token: ${user.token}")          // ❌ NEVER LOG TOKENS
Timber.d("Card: ${card.number}")          // ❌ NEVER LOG CARD NUMBERS
```

---

## 8. Token Storage

**Definition:** Securely storing auth tokens (JWT access token, refresh token) so they cannot be extracted from device storage or memory.

**Storage strategy by sensitivity:**

| Token | Storage | Why |
|---|---|---|
| Access Token (short-lived) | In-memory (`ViewModel`) | Fastest, cleared on kill |
| Refresh Token (long-lived) | `EncryptedSharedPreferences` | Persists across restarts, encrypted |
| Client Secret / API Key | Should NOT be on device | Use backend proxy instead |

**Example Code:**
```kotlin
class TokenManager(private val securePrefs: EncryptedSharedPreferences) {
    companion object {
        private const val KEY_ACCESS = "access_token"
        private const val KEY_REFRESH = "refresh_token"
        private const val KEY_EXPIRY = "token_expiry"
    }

    fun saveTokens(access: String, refresh: String, expiresIn: Long) {
        securePrefs.edit()
            .putString(KEY_ACCESS, access)
            .putString(KEY_REFRESH, refresh)
            .putLong(KEY_EXPIRY, System.currentTimeMillis() + expiresIn * 1000)
            .apply()
    }

    fun getAccessToken(): String? = securePrefs.getString(KEY_ACCESS, null)

    fun isTokenExpired(): Boolean {
        val expiry = securePrefs.getLong(KEY_EXPIRY, 0)
        return System.currentTimeMillis() >= expiry
    }

    fun clearTokens() {
        securePrefs.edit().clear().apply()
    }
}
```

---

## 9. Play Integrity API

**Definition:** Google's server-side attestation system. The app requests an integrity token from Google's servers, then sends it to **your backend** for verification. Google's response tells your backend: is this a genuine Android device? Is the app unmodified? Has the user's account been compromised?

**When to use:** Payment confirmation, account registration, any high-value action requiring server-side trust verification.

**Verdict contains:**
- `APP_INTEGRITY` — is the app genuine and signed by your key?
- `DEVICE_INTEGRITY` — is this a real Android device with Google Play?
- `ACCOUNT_DETAILS` — is this a licensed user?

**Example Code:**
```kotlin
// 1. Client: request integrity token
val integrityManager = IntegrityManagerFactory.create(context)

val nonce = Base64.encodeToString(
    SecureRandom().generateSeed(16), Base64.NO_WRAP
)

val integrityTokenRequest = IntegrityTokenRequest.builder()
    .setNonce(nonce)
    .build()

integrityManager.requestIntegrityToken(integrityTokenRequest)
    .addOnSuccessListener { response ->
        val token = response.token()
        // 2. Send token + nonce to YOUR backend for verification
        viewModel.verifyIntegrity(token, nonce)
    }
    .addOnFailureListener { e ->
        // Handle gracefully — do not block legitimate users
        Timber.e(e, "Integrity check failed")
    }

// 3. Backend (server-side) calls Google's API to decrypt and verify the token
// POST https://playintegrity.googleapis.com/v1/{packageName}:decodeIntegrityToken
// Response contains: appIntegrity, deviceIntegrity, accountDetails verdict
```

**Real World Example:** Before confirming a UPI payment, the backend requests an integrity token from the client and validates it with Google. If `MEETS_DEVICE_INTEGRITY` is false (emulator/rooted device), the payment is blocked server-side — even if the client-side root detection was bypassed.
