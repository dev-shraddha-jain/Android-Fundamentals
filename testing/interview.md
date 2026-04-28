# Testing — Interview Q&A

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
