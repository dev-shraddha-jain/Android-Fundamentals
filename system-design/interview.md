# Android HLD — Example Systems (Interview Ready)

---

## 1. Banking App Architecture

**Overview:** A production-grade banking app requires security at every layer, offline support for balance/history, and strict data integrity. The architecture must be modular, auditable, and resilient.

### Layer Diagram
```
┌──────────────────────────────────────────────────────┐
│  Presentation Layer                                  │
│  Compose UI · ViewModel · MVI State                  │
├──────────────────────────────────────────────────────┤
│  Domain Layer (pure Kotlin)                          │
│  UseCases · Domain Models · Repository Interfaces    │
├──────────────────────────────────────────────────────┤
│  Data Layer                                          │
│  Retrofit (mTLS) · Room (SQLCipher) · DataStore     │
├──────────────────────────────────────────────────────┤
│  Security Layer                                      │
│  Android Keystore · CertificatePinner · BiometricAPI │
└──────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Concern | Solution |
|---|---|
| Auth tokens | Android Keystore + EncryptedSharedPreferences |
| Local database | Room + SQLCipher (full encryption) |
| Network security | SSL Pinning + mTLS |
| Session management | Biometric re-auth after 5 min idle |
| Offline balance | Room cache, synced on reconnect |
| Audit log | Every user action logged with timestamp + device ID |

### Code — Biometric Auth + Keystore Token
```kotlin
// Store token in Keystore-backed encrypted prefs
val securePrefs = EncryptedSharedPreferences.create(
    context, "bank_prefs",
    MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Biometric prompt before every sensitive action
val biometricPrompt = BiometricPrompt(activity, executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: AuthenticationResult) {
            viewModel.sendIntent(BankIntent.ProceedTransaction)
        }
        override fun onAuthenticationFailed() {
            showError("Biometric auth failed")
        }
    }
)
biometricPrompt.authenticate(PromptInfo.Builder()
    .setTitle("Confirm Transaction")
    .setNegativeButtonText("Cancel")
    .build()
)
```

### Interview Answer
**The Architecture:**
*   **Layered Design:** 3-tier Clean Architecture (Presentation, Domain, Data) using MVI for deterministic state transitions.
*   **Data Security:** Room with SQLCipher for local storage; Keystore with EncryptedSharedPreferences for tokens.
*   **Network Security:** Retrofit with CertificatePinner (mTLS) to prevent MITM attacks.

**How to Answer:**
*   Emphasize that biometric authentication gates sensitive operations locally.
*   Mention that offline balances are cached in Room and synced securely via WorkManager when connectivity restores.

---

## 2. UPI Payment Flow

**Overview:** UPI payments involve multiple parties (user, PSP app, NPCI, bank). The Android app's job is to initiate the request, collect the UPI PIN securely, and handle the async response.

### Flow Diagram
```
User enters amount
        ↓
App validates input (local)
        ↓
POST /initiate-payment → PSP Backend
        ↓
Backend → NPCI → Beneficiary Bank
        ↓
Collect UPI PIN (via secure SDK)
        ↓ 
Backend returns txn status (SUCCESS / PENDING / FAILED)
        ↓
App polls or listens via WebSocket for final status
        ↓
Show result + update Room cache
```

### Code — Payment Intent + Polling
```kotlin
// 1. MVI Intent
sealed class PaymentIntent {
    data class InitiateUpi(val amount: Double, val vpa: String) : PaymentIntent()
    object PollStatus : PaymentIntent()
}

// 2. ViewModel with status polling
class PaymentViewModel(private val repo: PaymentRepository) : ViewModel() {
    private val _state = MutableStateFlow(PaymentState())
    val state = _state.asStateFlow()

    fun handleIntent(intent: PaymentIntent) {
        when (intent) {
            is PaymentIntent.InitiateUpi -> initiatePayment(intent.amount, intent.vpa)
            PaymentIntent.PollStatus     -> pollStatus()
        }
    }

    private fun initiatePayment(amount: Double, vpa: String) {
        viewModelScope.launch {
            _state.value = _state.value.copy(status = PaymentStatus.PROCESSING)
            when (val result = repo.initiateUpi(UpiRequest(amount, vpa))) {
                is Result.Success -> pollForFinalStatus(result.data.txnId)
                is Result.Error   -> _state.value = _state.value.copy(status = PaymentStatus.FAILED)
            }
        }
    }

    private fun pollForFinalStatus(txnId: String) {
        viewModelScope.launch {
            repeat(10) { // poll up to 10 times
                delay(3000)
                val status = repo.getStatus(txnId)
                if (status != PaymentStatus.PENDING) {
                    _state.value = _state.value.copy(status = status)
                    return@launch
                }
            }
        }
    }
}
```

### Interview Answer
**The Mechanism:**
*   **Async Flow:** The app POSTs to the PSP backend, which talks to NPCI.
*   **Secure Input:** UPI PIN is collected through an isolated, secure SDK, never directly handled by your app code.
*   **Resolution:** Payment settlement is async. The app either polls the status endpoint (with exponential backoff) or listens via WebSockets for the final push.

**How to Answer:**
*   Highlight the importance of the async nature of UPI.
*   Mention that pending transactions are persisted in Room so that the status can be recovered even after an app crash or process death.

---

## 3. Offline Transaction Sync

**Overview:** The app works fully offline and queues transactions locally. When connectivity is restored, a WorkManager job syncs the queue to the server in order.

### Architecture
```
User submits txn (offline)
        ↓
Save to Room with status = PENDING
        ↓
Enqueue SyncWorker (WorkManager, CONNECTED constraint)
        ↓        
Network restored → WorkManager triggers SyncWorker
        ↓
SyncWorker reads PENDING txns → POST each to API
        ↓
On success → update Room status = SYNCED
On failure → Result.retry() with exponential backoff
```

### Code
```kotlin
// Room entity with sync status
@Entity
data class TransactionEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val amount: Double,
    val syncStatus: SyncStatus = SyncStatus.PENDING,
    val createdAt: Long = System.currentTimeMillis()
)

enum class SyncStatus { PENDING, SYNCED, FAILED }

// WorkManager sync worker
class TransactionSyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    @Inject lateinit var dao: TransactionDao
    @Inject lateinit var api: BankApi

    override suspend fun doWork(): Result {
        val pending = dao.getPending()
        for (txn in pending) {
            try {
                api.submitTransaction(txn.toDto())
                dao.updateStatus(txn.id, SyncStatus.SYNCED)
            } catch (e: IOException) {
                return if (runAttemptCount < 5) Result.retry() else Result.failure()
            }
        }
        return Result.success()
    }
}

// Enqueue on app start and on network change
fun scheduleSyncIfNeeded(context: Context) {
    val request = OneTimeWorkRequestBuilder<TransactionSyncWorker>()
        .setConstraints(Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build())
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
        .build()

    WorkManager.getInstance(context).enqueueUniqueWork(
        "txn_sync", ExistingWorkPolicy.KEEP, request
    )
}
```

### Interview Answer
**The Mechanism:**
*   **Local Source of Truth:** All user actions are written locally to Room first, with a `PENDING` status.
*   **Connectivity Trigger:** A WorkManager job with a `CONNECTED` network constraint watches for availability.
*   **Batch Execution:** When restored, the worker reads all `PENDING` records in order, submits them via API, and marks them `SYNCED`.

**How to Answer:**
*   Point out that this design ensures zero data loss, even through process death.
*   Mention that failures should use **Exponential Backoff** with a max retry cap to prevent battery drain.

---

## 4. Notification Architecture

**Overview:** Android push notifications flow through FCM. The app must handle foreground, background, and killed states — and deep link the user to the correct screen.

### Flow
```
Server triggers push event
        ↓
FCM → Firebase → Device
        ↓
FirebaseMessagingService.onMessageReceived()
        ↓
App state check:
  Foreground → in-app banner (SnackBar / custom overlay)
  Background → show system notification
  Killed     → FCM shows notification automatically (data payload)
        ↓
User taps → deep link via Intent / NavController
```

### Code
```kotlin
@AndroidEntryPoint
class AppMessagingService : FirebaseMessagingService() {

    @Inject lateinit var notificationManager: AppNotificationManager
    @Inject lateinit var repository: NotificationRepository

    override fun onMessageReceived(message: RemoteMessage) {
        val data = message.data
        val type = NotificationType.from(data["type"] ?: return)

        // Persist notification for notification center screen
        viewModelScope.launch {
            repository.saveNotification(data.toEntity())
        }

        when (type) {
            NotificationType.PAYMENT_SUCCESS -> showPaymentNotification(data)
            NotificationType.LOGIN_ALERT     -> showSecurityAlert(data)
            NotificationType.PROMO           -> if (userPrefs.promoEnabled) showPromo(data)
        }
    }

    private fun showPaymentNotification(data: Map<String, String>) {
        val deepLinkIntent = NavDeepLinkBuilder(this)
            .setGraph(R.navigation.main_nav)
            .setDestination(R.id.transactionDetailFragment)
            .setArguments(bundleOf("txn_id" to data["txn_id"]))
            .createPendingIntent()

        NotificationCompat.Builder(this, PAYMENT_CHANNEL)
            .setSmallIcon(R.drawable.ic_payment)
            .setContentTitle("Payment ${data["status"]}")
            .setContentText("₹${data["amount"]} to ${data["recipient"]}")
            .setContentIntent(deepLinkIntent)
            .setAutoCancel(true)
            .build()
            .also { NotificationManagerCompat.from(this).notify(PAYMENT_NOTIF_ID, it) }
    }

    override fun onNewToken(token: String) {
        // Register new FCM token with backend
        viewModelScope.launch { repository.updateFcmToken(token) }
    }
}
```

### Interview Answer
**The Mechanism:**
*   **Delivery:** FCM delivers push payloads to `FirebaseMessagingService`.
*   **State Handling:** 
    *   *Foreground:* Show an in-app overlay/banner.
    *   *Background/Killed:* Build a `NotificationCompat` and post it to the system tray.
*   **Deep Linking:** Each payload contains a type that drives routing via `NavDeepLinkBuilder`.

**How to Answer:**
*   Explain that FCM tokens must be refreshed via `onNewToken` and synced to your backend.
*   Suggest persisting notifications locally to Room if you need an in-app "Notification Center" history.

---

## 5. Modularized App Architecture

**Overview:** Split the app into Gradle modules by feature and layer. Enforces compile-time boundaries, speeds up incremental builds, enables dynamic delivery.

### Module Structure
```
:app                     ← Navigation graph, DI graph root, thin shell
:feature:login           ← Login/Register screens + VM + DI
:feature:dashboard       ← Home feed + VM + DI
:feature:payment         ← UPI payment flow + VM + DI
:feature:profile         ← Profile/settings + VM + DI
:core:ui                 ← Shared design system (Button, TextField, Theme)
:core:network            ← Retrofit/OkHttp setup, interceptors
:core:database           ← Room database, DAOs
:core:domain             ← UseCases, Repository interfaces, Domain models
:core:testing            ← Shared test fakes and helpers
```

### Dependency Rules
```
:feature:* → :core:domain (interfaces only)
:feature:* → :core:ui (shared components)
:app        → :feature:* (wiring only)
:core:data  → :core:domain (implements interfaces)
:feature:*  ✗ :feature:*  (no cross-feature dependencies!)
```

### Code — Inter-feature navigation via NavGraph
```kotlin
// :app NavGraph — the only place features connect
@Composable
fun RootNavGraph(navController: NavHostController) {
    NavHost(navController, startDestination = "dashboard") {
        dashboardNavGraph(navController)   // :feature:dashboard
        paymentNavGraph(navController)     // :feature:payment
        profileNavGraph(navController)     // :feature:profile
    }
}

// :feature:dashboard — knows nothing about :feature:payment
@Composable
fun DashboardScreen(onPayClick: () -> Unit) {
    Button(onClick = onPayClick) { Text("Pay") }  // callback, not NavController
}

// :app wires it
dashboardNavGraph {
    DashboardScreen(onPayClick = { navController.navigate("payment/enter") })
}
```

### Interview Answer
**The Mechanism:**
*   **Horizontal Split:** Features are split into `:feature:*` modules.
*   **Vertical Split:** Shared infrastructure lives in `:core:*` modules (`:core:domain`, `:core:ui`, `:core:data`).
*   **Strict Dependency Flow:** Feature modules depend only on `:core:domain` and `:core:ui`. They *never* depend on each other.

**How to Answer:**
*   Explain that `:core:domain` contains only pure Kotlin (interfaces, use cases) while `:core:data` implements them.
*   Highlight that cross-feature navigation happens exclusively through the root `:app` module's NavGraph.
*   Mention the primary benefits: strict boundaries, parallel team development, and significantly reduced incremental build times.
