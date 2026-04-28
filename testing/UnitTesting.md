# Unit Testing — Android (Expert Level)

Unit tests verify a single class or function in **isolation** — no Android framework, no database, no network. Fast (milliseconds per test), run on the JVM.

---

## 1. JUnit 4 / 5 + Kotlin

**Definition:** The base test runner for JVM unit tests. Annotate test functions with `@Test` and use `assert*` functions or Truth/Hamcrest matchers.

**Example Code:**
```kotlin
class PriceCalculatorTest {

    private lateinit var calculator: PriceCalculator

    @Before
    fun setup() {
        calculator = PriceCalculator(taxRate = 0.18)
    }

    @Test
    fun `total with tax returns correct amount`() {
        val total = calculator.calculateTotal(basePrice = 100.0)
        assertEquals(118.0, total, 0.001)
    }

    @Test
    fun `discount cannot exceed item price`() {
        val result = calculator.applyDiscount(price = 50.0, discount = 100.0)
        assertEquals(0.0, result, 0.001)
    }

    @Test(expected = IllegalArgumentException::class)
    fun `negative price throws exception`() {
        calculator.calculateTotal(basePrice = -10.0)
    }
}
```

---

## 2. Testing ViewModels with Coroutines

**Definition:** ViewModels with `viewModelScope` require a `TestCoroutineScheduler` and `UnconfinedTestDispatcher` to make coroutines run eagerly and synchronously in tests.

**Example Code:**
```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val coroutineRule = MainCoroutineRule()  // replaces Dispatchers.Main with TestDispatcher

    private val fakeRepo = FakeUserRepository()
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        viewModel = UserViewModel(fakeRepo)
    }

    @Test
    fun `loadUser emits success state`() = runTest {
        fakeRepo.userToReturn = User("1", "Alice")

        viewModel.loadUser("1")

        val state = viewModel.uiState.value
        assertThat(state).isInstanceOf(UiState.Success::class.java)
        assertThat((state as UiState.Success).user.name).isEqualTo("Alice")
    }

    @Test
    fun `loadUser emits error on network failure`() = runTest {
        fakeRepo.shouldThrowError = true

        viewModel.loadUser("1")

        assertThat(viewModel.uiState.value).isInstanceOf(UiState.Error::class.java)
    }
}

// MainCoroutineRule helper
@OptIn(ExperimentalCoroutinesApi::class)
class MainCoroutineRule : TestWatcher() {
    val testDispatcher = UnconfinedTestDispatcher()
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

---

## 3. Mockito / MockK

**Definition:** Mocking frameworks that create fake implementations of dependencies so the class under test is truly isolated. **MockK** is the Kotlin-idiomatic choice (supports `object`, `companion object`, `extension functions`).

**Example Code:**
```kotlin
@ExtendWith(MockKExtension::class)
class OrderServiceTest {

    @MockK lateinit var paymentGateway: PaymentGateway
    @MockK lateinit var inventoryService: InventoryService
    @InjectMockKs lateinit var orderService: OrderService

    @Test
    fun `place order deducts inventory on success`() {
        every { paymentGateway.charge(any(), any()) } returns PaymentResult.Success
        every { inventoryService.deduct(any(), any()) } just Runs

        orderService.placeOrder(itemId = "A1", qty = 2, amount = 200.0)

        verify { inventoryService.deduct("A1", 2) }
    }

    @Test
    fun `place order does not deduct inventory on payment failure`() {
        every { paymentGateway.charge(any(), any()) } returns PaymentResult.Failure("Declined")

        orderService.placeOrder(itemId = "A1", qty = 2, amount = 200.0)

        verify(exactly = 0) { inventoryService.deduct(any(), any()) }
    }
}
```

---

## 4. Fake vs Mock

| | **Fake** | **Mock** |
|---|---|---|
| **What** | Real lightweight implementation | Auto-generated stub controlled by the test |
| **Best for** | Repository, DataStore, databases | Single method interaction verification |
| **Code** | You write it | Framework generates it |

```kotlin
// Fake — used for Flow-returning repositories
class FakeUserRepository : UserRepository {
    var userToReturn: User? = null
    var shouldThrowError = false

    override fun getUser(id: String): Flow<User?> = flow {
        if (shouldThrowError) throw IOException("Network error")
        emit(userToReturn)
    }
}
```

---

## 5. Testing Flow with Turbine

**Definition:** Turbine is a small library that makes testing `Flow` emissions simple — `awaitItem()`, `awaitComplete()`, `awaitError()`.

**Example Code:**
```kotlin
@Test
fun `user flow emits cached then fresh`() = runTest {
    val repo = FakeUserRepository()
    repo.userToReturn = User("1", "Alice")

    repo.getUser("1").test {
        val first = awaitItem()
        assertThat(first?.name).isEqualTo("Alice")
        cancelAndIgnoreRemainingEvents()
    }
}
```
