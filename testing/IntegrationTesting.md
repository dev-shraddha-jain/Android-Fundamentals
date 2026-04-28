# Integration Testing — Android (Expert Level)

Integration tests verify that multiple components work correctly **together** — e.g., ViewModel + Repository + Room, or Repository + Retrofit. Run on device/emulator or with Robolectric.

---

## 1. Room Database Integration Tests

**Definition:** Test DAOs against a real in-memory Room database — verifying actual SQL queries, migrations, and transactions.

**Example Code:**
```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {

    private lateinit var db: AppDatabase
    private lateinit var dao: UserDao

    @Before
    fun setup() {
        db = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).allowMainThreadQueries().build()
        dao = db.userDao()
    }

    @After
    fun teardown() = db.close()

    @Test
    fun insertAndRetrieveUser() = runTest {
        val user = User(id = "1", name = "Alice", email = "alice@example.com")
        dao.upsert(user)

        val retrieved = dao.getById("1")
        assertThat(retrieved).isEqualTo(user)
    }

    @Test
    fun getUserFlow_emitsOnUpdate() = runTest {
        val user = User(id = "1", name = "Alice", email = "alice@example.com")
        dao.upsert(user)

        dao.getUserById("1").test {
            val first = awaitItem()
            assertThat(first?.name).isEqualTo("Alice")

            dao.upsert(user.copy(name = "Alice Updated"))
            val updated = awaitItem()
            assertThat(updated?.name).isEqualTo("Alice Updated")

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

## 2. Repository Integration Tests (with MockWebServer)

**Definition:** Testing the Repository layer against a real HTTP client using `MockWebServer` (OkHttp) to serve fake JSON responses — no real network needed.

**Example Code:**
```kotlin
@RunWith(AndroidJUnit4::class)
class UserRepositoryTest {

    private lateinit var server: MockWebServer
    private lateinit var api: UserApi
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        server = MockWebServer()
        server.start()

        api = Retrofit.Builder()
            .baseUrl(server.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(UserApi::class.java)

        repository = UserRepositoryImpl(api, FakeUserDao())
    }

    @After
    fun teardown() = server.shutdown()

    @Test
    fun `getUser returns parsed user on 200`() = runTest {
        server.enqueue(MockResponse()
            .setResponseCode(200)
            .setBody("""{"id":"1","name":"Alice","email":"alice@example.com"}""")
        )

        val result = repository.getUser("1")
        assertThat(result).isInstanceOf(ApiResult.Success::class.java)
        assertThat((result as ApiResult.Success).data.name).isEqualTo("Alice")
    }

    @Test
    fun `getUser returns error on 404`() = runTest {
        server.enqueue(MockResponse().setResponseCode(404))

        val result = repository.getUser("999")
        assertThat(result).isInstanceOf(ApiResult.Error::class.java)
    }
}
```

---

## 3. ViewModel + Repository Integration

**Definition:** Test the ViewModel with a real (fake) Repository to verify the full presentation logic — state transitions, error handling, loading states — without mocking individual methods.

**Example Code:**
```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelIntegrationTest {

    @get:Rule val coroutineRule = MainCoroutineRule()

    @Test
    fun `loading → success state transition`() = runTest {
        val fakeRepo = FakeUserRepository(userToReturn = User("1", "Alice"))
        val vm = UserViewModel(fakeRepo)

        vm.uiState.test {
            assertThat(awaitItem()).isEqualTo(UiState.Loading)
            vm.loadUser("1")
            assertThat(awaitItem()).isInstanceOf(UiState.Success::class.java)
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

## 4. Migration Tests

**Definition:** Verify that database migrations execute correctly and preserve data integrity using `MigrationTestHelper`.

**Example Code:**
```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {

    private val TEST_DB = "migration_test"

    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To2_addsLastLoginColumn() {
        // Create DB at version 1
        helper.createDatabase(TEST_DB, 1).apply {
            execSQL("INSERT INTO users VALUES ('1', 'Alice', 'alice@example.com')")
            close()
        }

        // Run migration to version 2
        val db = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)

        // Verify new column exists and has default value
        val cursor = db.query("SELECT lastLoginAt FROM users WHERE id = '1'")
        cursor.moveToFirst()
        assertThat(cursor.getLong(0)).isEqualTo(0L)
        cursor.close()
    }
}
```
