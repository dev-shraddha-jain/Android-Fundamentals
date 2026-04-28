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
> A banking app follows Clean Architecture with 3 layers. The data layer uses Room with SQLCipher for encrypted local storage, Retrofit with CertificatePinner + mTLS for network calls, and Android Keystore for token management. Biometric authentication gates sensitive operations. Offline balance is cached in Room and synced via WorkManager when connectivity is restored. The architecture uses MVI to ensure every state transition is deterministic and auditable.

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
> UPI payment on Android follows an async flow. The app initiates via a POST to the PSP backend, which communicates with NPCI. The UPI PIN is collected through a secure SDK (never handled by app code directly). Since payment settlement is async, the app either polls the status endpoint with exponential backoff, or uses a WebSocket for push updates. All pending transactions are persisted in Room so status can be recovered after app kill or crash.

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
> The offline sync architecture uses Room as the local source of truth. All user actions are written locally first with status PENDING. A WorkManager job with a CONNECTED constraint watches for network availability. When restored, the worker reads all PENDING records in order, submits them to the API, and marks each SYNCED. Failures use exponential backoff with a max retry cap. This ensures no data loss even through process death.

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
> FCM delivers the push to `FirebaseMessagingService`. If the app is foreground we show an in-app overlay; if background or killed, we build a `NotificationCompat` and post it to the system tray. Each notification carries a type and payload that drives deep linking via `NavDeepLinkBuilder`. Notifications are also persisted to Room for a notification center screen. FCM tokens are refreshed via `onNewToken` and synced to the backend.

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
> We split the app into `:feature:*` modules for each product feature and `:core:*` modules for shared infrastructure. The `:core:domain` module contains only pure Kotlin — interfaces, use cases, and domain models. The `:core:data` module implements those interfaces. Feature modules depend only on `:core:domain` and `:core:ui` — never on each other. Cross-feature navigation happens exclusively through the `:app` module's NavGraph using callbacks or shared navigation events. This enforces strict boundaries, enables parallel team development, and reduces incremental build times significantly.
