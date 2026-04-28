# Room Database — Deep Dive (Expert Level)

---

## 1. Room Internals

**Definition:** Room is a Kotlin/Java abstraction layer over SQLite. At compile time, Room's annotation processor (`kapt` / `ksp`) generates concrete implementations for `@Dao` interfaces and validates all SQL queries — catching syntax errors at build time, not runtime.

**Internal layers:**
```
Your Code (DAO interface)
        ↓
Room Annotation Processor (generates *_Impl classes at compile time)
        ↓
SupportSQLiteDatabase (abstraction over SQLite)
        ↓
SQLite (Android's built-in C library)
```

**Key generated classes:**
- `UserDao_Impl` — concrete implementation of your DAO interface
- `AppDatabase_Impl` — manages database creation, version, and migration
- `UserDao_Impl_RxJava` — if RxJava adapter is used

**Example Code:**
```kotlin
@Database(entities = [User::class, Transaction::class], version = 3)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun transactionDao(): TransactionDao

    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                Room.databaseBuilder(context.applicationContext, AppDatabase::class.java, "app.db")
                    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
                    .fallbackToDestructiveMigration() // ⚠️ only in dev — destroys data!
                    .build()
                    .also { INSTANCE = it }
            }
        }
    }
}
```

**Real World Example:** Room catches `SELECT * FROM usres` (typo) at compile time before your app is ever installed — saving a crash in production.

---

## 2. DAO (Data Access Object)

**Definition:** A `@Dao`-annotated interface that defines all database operations for a specific entity. Room generates the full SQL implementation from annotations — no boilerplate SQL code in your business logic.

**Example Code:**
```kotlin
@Dao
interface UserDao {
    // Basic CRUD
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(user: User)

    @Update
    suspend fun update(user: User)

    @Delete
    suspend fun delete(user: User)

    // Reactive query — returns Flow, re-emits on data change automatically
    @Query("SELECT * FROM users ORDER BY createdAt DESC")
    fun getAllUsers(): Flow<List<User>>

    // Single user — nullable for safe fetch
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getById(id: String): User?

    // JOIN query
    @Query("""
        SELECT u.*, COUNT(t.id) as txnCount
        FROM users u
        LEFT JOIN transactions t ON t.userId = u.id
        WHERE u.id = :userId
        GROUP BY u.id
    """)
    fun getUserWithStats(userId: String): Flow<UserWithStats>

    // Partial update — only update specific columns
    @Query("UPDATE users SET lastLoginAt = :timestamp WHERE id = :id")
    suspend fun updateLastLogin(id: String, timestamp: Long)
}
```

**When to use `Flow` vs `suspend`:**
- `Flow<T>` — for queries you want to observe reactively (UI list, live balance)
- `suspend fun` — for one-shot operations (insert, delete, single fetch)

---

## 3. TypeConverters

**Definition:** Room only stores primitive types (String, Int, Long, Double, ByteArray) in SQLite columns. `@TypeConverter` functions tell Room how to convert custom types to/from these primitives.

**When to use:** Storing `Date`, `List<String>`, enums, custom value objects, or any non-primitive type.

**Example Code:**
```kotlin
class Converters {
    // Date ↔ Long
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }

    @TypeConverter
    fun toTimestamp(date: Date?): Long? = date?.time

    // List<String> ↔ String (JSON)
    @TypeConverter
    fun fromStringList(value: String): List<String> =
        Gson().fromJson(value, object : TypeToken<List<String>>() {}.type)

    @TypeConverter
    fun toStringList(list: List<String>): String = Gson().toJson(list)

    // Enum ↔ String
    @TypeConverter
    fun fromStatus(value: String): TransactionStatus =
        TransactionStatus.valueOf(value)

    @TypeConverter
    fun toStatus(status: TransactionStatus): String = status.name
}

// Register at database level (applies to all DAOs)
@Database(entities = [User::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase()
```

---

## 4. Migration

**Definition:** When you change your schema (add/remove a column or table), you must provide a `Migration` object so existing users' data is preserved. Without a migration, Room throws `IllegalStateException` (or destroys data if `fallbackToDestructiveMigration()` is set).

**When to use:** Every schema change in production — adding columns, renaming tables, changing types.

**Example Code:**
```kotlin
// Migration 1 → 2: Add a new column
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE users ADD COLUMN lastLoginAt INTEGER NOT NULL DEFAULT 0")
    }
}

// Migration 2 → 3: Create a new table
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS `notifications` (
                `id` TEXT NOT NULL PRIMARY KEY,
                `title` TEXT NOT NULL,
                `body` TEXT NOT NULL,
                `isRead` INTEGER NOT NULL DEFAULT 0,
                `createdAt` INTEGER NOT NULL
            )
        """)
    }
}

// Register migrations on DB builder
Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
    .build()
```

**Testing migrations:**
```kotlin
// Use Room's MigrationTestHelper in androidTest
@RunWith(AndroidJUnit4::class)
class MigrationTest {
    @get:Rule val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To2() {
        helper.createDatabase("test.db", 1).close()
        val db = helper.runMigrationsAndValidate("test.db", 2, true, MIGRATION_1_2)
        // Validate columns exist
    }
}
```

---

## 5. Indexing

**Definition:** Indexes allow SQLite to look up rows by a column without scanning the entire table. Critical for performance on large datasets (10k+ rows). Defined on `@Entity` annotations.

**When to use:** Columns you frequently query with `WHERE`, `ORDER BY`, or `JOIN` conditions.

**Example Code:**
```kotlin
@Entity(
    tableName = "transactions",
    indices = [
        Index(value = ["userId"]),              // single column index — fast WHERE userId = ?
        Index(value = ["userId", "createdAt"]), // composite index — fast WHERE userId = ? ORDER BY createdAt
        Index(value = ["txnRef"], unique = true) // unique index — prevents duplicate txn refs
    ]
)
data class TransactionEntity(
    @PrimaryKey val id: String,
    val userId: String,     // indexed — frequently queried
    val txnRef: String,     // unique indexed — idempotency key
    val amount: Double,
    val createdAt: Long     // part of composite index — sorted queries
)
```

**Performance impact:**
- `SELECT * FROM transactions WHERE userId = '123'` → **O(log n)** with index vs **O(n)** without
- Indexes cost extra storage and slow down `INSERT`/`UPDATE` — only index what you actually query

---

## 6. Transactions

**Definition:** A `@Transaction` block groups multiple SQL operations atomically — either all succeed or all fail together. Essential for data integrity across multiple DAO calls.

**When to use:** Any time you update more than one table together (e.g., creating a user AND their initial profile row), or need to ensure read-modify-write atomicity.

**Example Code:**
```kotlin
// DAO-level transaction
@Dao
interface TransactionDao {
    @Transaction
    suspend fun transferFunds(fromId: String, toId: String, amount: Double) {
        debit(fromId, amount)
        credit(toId, amount)
        insertLog(TransferLog(fromId, toId, amount))
        // If any of these fail → ALL are rolled back automatically
    }

    @Query("UPDATE accounts SET balance = balance - :amount WHERE id = :id")
    suspend fun debit(id: String, amount: Double)

    @Query("UPDATE accounts SET balance = balance + :amount WHERE id = :id")
    suspend fun credit(id: String, amount: Double)

    @Insert
    suspend fun insertLog(log: TransferLog)
}

// Database-level explicit transaction
suspend fun complexOperation() {
    db.withTransaction {
        userDao.upsert(user)
        profileDao.upsert(profile)
        settingsDao.createDefaults(user.id)
    }
}
```

**`@Transaction` for relations (prevents inconsistent reads):**
```kotlin
@Transaction
@Query("SELECT * FROM users WHERE id = :userId")
fun getUserWithTransactions(userId: String): Flow<UserWithTransactions>

data class UserWithTransactions(
    @Embedded val user: User,
    @Relation(parentColumn = "id", entityColumn = "userId")
    val transactions: List<TransactionEntity>
)
```

---

## 7. Database Encryption

**Definition:** SQLCipher encrypts the entire SQLite database file using AES-256. Without the key, the `.db` file is unreadable — even on rooted devices or by extracting the APK's data folder.

**When to use:** Banking, healthcare, fintech — any app storing PII, financial data, or session tokens locally.

**Example Code:**
```kotlin
// 1. Add SQLCipher dependency
// implementation "net.zetetic:android-database-sqlcipher:4.5.4"

// 2. Generate and securely store the key in Android Keystore
fun getDatabaseKey(): ByteArray {
    val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()

    val securePrefs = EncryptedSharedPreferences.create(
        context, "db_prefs", masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    val existingKey = securePrefs.getString("db_key", null)
    if (existingKey != null) return Base64.decode(existingKey, Base64.DEFAULT)

    // Generate new key
    val key = ByteArray(32).also { SecureRandom().nextBytes(it) }
    securePrefs.edit().putString("db_key", Base64.encodeToString(key, Base64.DEFAULT)).apply()
    return key
}

// 3. Build Room with SQLCipher factory
val passphrase = SQLiteDatabase.getBytes(getDatabaseKey().toCharArray())
val factory = SupportFactory(passphrase)

val db = Room.databaseBuilder(context, AppDatabase::class.java, "secure.db")
    .openHelperFactory(factory)
    .build()
```

---

## 8. DataStore vs SharedPreferences

**Definition:**
- **SharedPreferences** — legacy XML-based key-value store. Synchronous, not safe for main thread, no type safety, no coroutine support.
- **DataStore (Preferences)** — modern replacement backed by a protobuf/file. Fully asynchronous via Flow, type-safe (Proto DataStore), safe for concurrent access.

| | SharedPreferences | DataStore (Preferences) | DataStore (Proto) |
|---|---|---|---|
| **API** | Synchronous | `Flow<T>` | `Flow<T>` |
| **Main thread safe** | ❌ (ANR risk) | ✅ | ✅ |
| **Type safety** | ❌ (String keys) | Partial | ✅ (schema) |
| **Coroutine support** | ❌ | ✅ | ✅ |
| **Atomic writes** | ❌ | ✅ | ✅ |

**Example Code:**
```kotlin
// 1. Preferences DataStore
val Context.dataStore by preferencesDataStore(name = "settings")

val DARK_MODE_KEY = booleanPreferencesKey("dark_mode")

// Write
suspend fun setDarkMode(enabled: Boolean) {
    context.dataStore.edit { prefs ->
        prefs[DARK_MODE_KEY] = enabled
    }
}

// Read — returns Flow, re-emits on change
val isDarkMode: Flow<Boolean> = context.dataStore.data.map { prefs ->
    prefs[DARK_MODE_KEY] ?: false
}

// 2. Proto DataStore (fully typed schema)
// Define .proto schema → generates type-safe Settings class
val settings: Flow<UserSettings> = context.settingsDataStore.data
// Update atomically
context.settingsDataStore.updateData { current ->
    current.toBuilder().setNotificationsEnabled(true).build()
}
```

**When to use what:**
- `SharedPreferences` → legacy code only, never in new development
- `Preferences DataStore` → simple key-value settings, user preferences
- `Proto DataStore` → complex settings objects requiring strict schema
- `Room` → structured, queryable, relational data

---

## 9. Offline-First Architecture

**Definition:** Design where the local database (Room) is the **Single Source of Truth**. The UI always reads from Room, never directly from the network. Network data is written to Room, which triggers UI updates automatically via `Flow`.

**Pattern:**
```
UI ← Room (Flow) ← Repository
                          ↑
                    Network (API)
                    writes to Room
                    on success
```

**Example Code:**
```kotlin
class UserRepository(
    private val dao: UserDao,
    private val api: UserApi,
    private val networkMonitor: NetworkMonitor
) {
    // UI collects this — always fresh, always reactive
    fun getUser(id: String): Flow<User?> = flow {
        // 1. Emit local cache immediately (instant UI)
        emitAll(dao.getUserById(id))

        // 2. Refresh from network if online
        if (networkMonitor.isConnected) {
            try {
                val fresh = api.getUser(id)
                dao.upsert(fresh.toEntity())
                // Room Flow auto-emits the new value ↑ — no manual emit needed
            } catch (e: IOException) {
                // Ignore — UI shows cached data
            }
        }
    }
}
```

---

## 🎯 Interview Questions

### Q1. How does Room migration work?

> Room stores the current schema version in the SQLite `user_version` pragma. On startup, Room compares this against the `version` declared in `@Database`. If they differ, it runs `Migration` objects in order (e.g., 1→2, 2→3). Each migration runs raw SQL DDL to alter the schema. If no migration path is found, Room throws `IllegalStateException` — unless `fallbackToDestructiveMigration()` is set, which drops and recreates the database. Migrations should always be tested using `MigrationTestHelper` in `androidTest`.

---

### Q2. How do you prevent DB corruption?

> **1. Use `@Transaction`** for multi-step operations — SQLite's ACID guarantees that partial writes are rolled back on failure.  
> **2. Use `WAL (Write-Ahead Logging)`** mode — Room enables this by default, which allows concurrent reads during writes and is more corruption-resistant than the default journal mode.  
> **3. Never access the database on the main thread** — Room enforces this (`allowMainThreadQueries()` should never be called in production).  
> **4. Use `fallbackToDestructiveMigration` only in dev** — in production always provide explicit migrations.  
> **5. Encrypt with SQLCipher** — prevents corruption from unauthorized access.  
> **6. Handle `SQLiteException`** in the data layer — wrap DAO calls in try/catch and emit error states rather than crashing.