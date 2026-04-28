# Android HLD — Core Concepts

---

## 1. Scalability

**Definition:** Designing the app so new features, users, or data volumes can be handled without rewriting the core. On Android this means: modular code, stateless ViewModels, reactive data streams, and a layered architecture that lets each layer scale independently.

**Key principles:**
- Separate concerns: Presentation → Domain → Data
- Use repositories to abstract data sources — swap API for cache/DB transparently
- Prefer reactive streams (Flow) over one-shot calls so the UI scales to any data source

**Example Code:**
```kotlin
// Repository pattern — scalable data layer
class UserRepository(
    private val api: UserApi,          // remote source
    private val db: UserDao,           // local cache
    private val networkMonitor: NetworkMonitor
) {
    fun getUser(id: String): Flow<User> = flow {
        // 1. Emit cached data immediately
        emit(db.getUser(id))
        // 2. Refresh from network if online
        if (networkMonitor.isConnected) {
            val fresh = api.getUser(id)
            db.upsert(fresh)
            emit(fresh)
        }
    }
}
```

---

## 2. Caching

**Definition:** Storing data locally (memory or disk) to reduce network calls, improve speed, and support offline usage. Android caching layers:
- **Memory** — `LruCache`, in-process Map (fast, lost on kill)
- **Disk** — Room database (persists across restarts)
- **HTTP** — OkHttp `Cache` (caches raw HTTP responses)

**When to use:** Frequently read, rarely changing data (user profile, config, lookup tables).

**Example Code:**
```kotlin
// 1. OkHttp HTTP Cache
val cacheDir = File(context.cacheDir, "http_cache")
val cache = Cache(cacheDir, 10 * 1024 * 1024) // 10MB
val client = OkHttpClient.Builder().cache(cache).build()

// 2. Room as persistent cache (Single Source of Truth)
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(user: User)
}

// 3. Memory cache for images (Coil does this automatically)
// For custom objects:
val memCache = LruCache<String, User>(50) // max 50 users in memory
```

**Cache invalidation strategy:**
```kotlin
// Time-based: invalidate if data is older than N minutes
val isFresh = (System.currentTimeMillis() - cached.updatedAt) < 5 * 60 * 1000
if (!isFresh) refresh()
```

---

## 3. Pagination

**Definition:** Loading data in pages to avoid fetching thousands of records. Jetpack Paging 3 is the standard — it integrates with Room, Retrofit, and Compose.

**When to use:** Feeds, search results, transaction history, chat messages.

**Example Code:**
```kotlin
// PagingSource — bridges Retrofit and Paging 3
class TransactionPagingSource(private val api: BankApi) : PagingSource<Int, Transaction>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Transaction> {
        val page = params.key ?: 1
        return try {
            val response = api.getTransactions(page, params.loadSize)
            LoadResult.Page(
                data = response.items,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.items.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }
    override fun getRefreshKey(state: PagingState<Int, Transaction>) = state.anchorPosition
}

// ViewModel
val transactions: Flow<PagingData<Transaction>> = Pager(
    config = PagingConfig(pageSize = 20, prefetchDistance = 5),
    pagingSourceFactory = { TransactionPagingSource(api) }
).flow.cachedIn(viewModelScope)

// Compose UI
val txns = vm.transactions.collectAsLazyPagingItems()
LazyColumn {
    items(txns, key = { it.id }) { txn -> TransactionRow(txn) }
    txns.apply {
        when {
            loadState.append is LoadState.Loading -> item { LoadingSpinner() }
            loadState.append is LoadState.Error   -> item { RetryButton(::retry) }
        }
    }
}
```

---

## 4. Retry Queue

**Definition:** A persistent queue of failed operations that are retried when conditions improve (network restored, server recovers). Critical for offline-first apps.

**When to use:** Payment submissions, data sync, critical POST operations that must not be lost.

**Example Code:**
```kotlin
// WorkManager — persistent retry queue
class SyncTransactionWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        val txnId = inputData.getString("txn_id") ?: return Result.failure()
        return try {
            val txn = db.getPendingTransaction(txnId)
            api.submitTransaction(txn)
            db.markSynced(txnId)
            Result.success()
        } catch (e: IOException) {
            if (runAttemptCount < 3) Result.retry() // WorkManager retries automatically
            else Result.failure()
        }
    }
}

// Enqueue with exponential backoff
fun enqueueSync(txnId: String) {
    val request = OneTimeWorkRequestBuilder<SyncTransactionWorker>()
        .setInputData(workDataOf("txn_id" to txnId))
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
        .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
        .build()
    WorkManager.getInstance(context).enqueueUniqueWork(
        "sync_$txnId",
        ExistingWorkPolicy.KEEP,
        request
    )
}
```

---

## 5. Encryption

**Definition:** Protecting sensitive data at rest (stored on device) and in transit (network). Android provides the Jetpack Security library (`EncryptedSharedPreferences`, `EncryptedFile`) backed by the Android Keystore.

**When to use:** Auth tokens, PII, financial data, session data — anything that must not be readable if the device is stolen or rooted.

**Example Code:**
```kotlin
// 1. Encrypted SharedPreferences (for small key-value data)
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val securePrefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
securePrefs.edit().putString("auth_token", token).apply()

// 2. Encrypted File (for larger blobs)
val encryptedFile = EncryptedFile.Builder(
    context,
    File(context.filesDir, "sensitive.dat"),
    masterKey,
    EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
).build()

// Write
encryptedFile.openFileOutput().use { it.write(sensitiveData) }

// 3. Room with SQLCipher (full database encryption)
val passphrase = SQLiteDatabase.getBytes(keyFromKeystore)
val factory = SupportFactory(passphrase)
Room.databaseBuilder(context, AppDatabase::class.java, "bank.db")
    .openHelperFactory(factory)
    .build()
```

---

## 6. Clean Architecture

**Definition:** Separation of code into concentric layers with strict dependency rules: **Presentation → Domain → Data**. Inner layers have no knowledge of outer layers. Dependencies point inward only.

```
┌─────────────────────────────┐
│  Presentation Layer         │  ViewModel, UI State, Composables
├─────────────────────────────┤
│  Domain Layer (pure Kotlin) │  UseCases, Domain Models, Repository interfaces
├─────────────────────────────┤
│  Data Layer                 │  Repository Impl, API, Room, DataStore
└─────────────────────────────┘
```

**Example Code:**
```kotlin
// Domain Layer — pure Kotlin, no Android imports
data class Transaction(val id: String, val amount: Double, val status: Status)

interface TransactionRepository {          // interface in Domain
    fun getTransactions(): Flow<List<Transaction>>
    suspend fun submit(txn: Transaction): Result<Unit>
}

class GetTransactionsUseCase(private val repo: TransactionRepository) {
    operator fun invoke(): Flow<List<Transaction>> = repo.getTransactions()
}

// Data Layer — implements Domain interfaces
class TransactionRepositoryImpl(
    private val api: BankApi,
    private val dao: TransactionDao
) : TransactionRepository {
    override fun getTransactions(): Flow<List<Transaction>> =
        dao.getAll().map { it.toDomain() }   // map DB entity → domain model

    override suspend fun submit(txn: Transaction): Result<Unit> = runCatching {
        api.submit(txn.toDto())
    }
}

// Presentation Layer — ViewModel depends on UseCase, not Repo directly
class TransactionViewModel(
    private val getTransactions: GetTransactionsUseCase
) : ViewModel() {
    val transactions = getTransactions().stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}
```

---

## 7. Feature Modules

**Definition:** Splitting an app into Gradle modules by feature (`:feature:login`, `:feature:dashboard`, `:feature:payment`). Each module is independently compilable and has its own ViewModel, UI, and DI graph.

**Benefits:** Faster build times, enforced boundary isolation, parallel development, optional Play Feature Delivery (dynamic delivery).

**Module structure:**
```
app/
├── :app                    ← thin shell, navigation graph
├── :feature:login          ← login screens, VM, DI
├── :feature:dashboard      ← dashboard screens, VM
├── :feature:payment        ← payment flow, VM
├── :core:network           ← Retrofit/Ktor setup (shared)
├── :core:database          ← Room setup (shared)
├── :core:ui                ← shared design system components
└── :core:domain            ← shared UseCases, interfaces
```

**Example Code:**
```kotlin
// :core:domain — shared interface
interface PaymentRepository {
    suspend fun initiateUpi(request: UpiRequest): Result<UpiResponse>
}

// :feature:payment — depends on :core:domain only
@HiltViewModel
class PaymentViewModel @Inject constructor(
    private val repo: PaymentRepository   // injected — no knowledge of impl
) : ViewModel() { /* ... */ }

// :app — wires everything via NavGraph
NavHost(navController, startDestination = "dashboard") {
    navigation(route = "payment", startDestination = "payment/enter") {
        composable("payment/enter") { PaymentEntryScreen() }
        composable("payment/confirm") { PaymentConfirmScreen() }
    }
}
```

**Dependency rules:**
- `:feature:*` modules depend on `:core:*` only — never on each other
- Communication between features goes through `:app`'s NavController or shared events in `:core:domain`
