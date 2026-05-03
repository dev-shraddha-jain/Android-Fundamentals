# Testing — Interview Q&A

---

## Testing Interview Questions

### Q1. [How Mechanism] What is the testing pyramid and why does it matter?
**The Mechanism:**
*   **Unit Tests (Base):** Fast, isolated, run on the JVM (70% of tests).
*   **Integration Tests (Middle):** Room + Retrofit, often require an emulator (20% of tests).
*   **UI/E2E Tests (Top):** Slow, full device execution, flaky (10% of tests).

**How to Answer:**
*   Explain the 70/20/10 ratio rule.
*   Mention that an "inverted pyramid" (mostly UI tests) is an anti-pattern because it's slow and expensive to maintain.

---

### Q2. [Tricky] How do you test a ViewModel with coroutines?
**The Mechanism:**
*   You must replace the Main dispatcher because `Dispatchers.Main` relies on the Android Looper which isn't available in standard JVM tests.
*   Use a `TestWatcher` rule to inject a `StandardTestDispatcher` or `UnconfinedTestDispatcher`.
*   Wrap your test execution in `runTest {}` to advance virtual time and skip `delay()` calls.

**How to Answer:**
*   Mention the `TestDispatcher` replacement.
*   Highlight the use of the **Turbine** library (`vm.uiState.test { awaitItem() }`) for cleanly testing `StateFlow` and `SharedFlow` emissions.

---

### Q3. [Architecture] Fake vs Mock — which do you prefer for repositories?
**The Answer:**
*   **Fakes:** Hand-written classes with simple state fields (`userToReturn`, `shouldThrowError`).
*   **Mocks:** Framework-generated objects (Mockito/MockK) that verify exact method calls.

**How to Answer:**
*   Strongly prefer **Fakes** for Repositories because they return `Flow`. Mocking cold flows is verbose and error-prone.
*   Reserve **Mocks** for verifying exact interactions (e.g., verifying `analyticsService.logEvent()` was called N times).

---

### Q4. [Database] How do you test Room DAOs?
**The Mechanism:**
*   Use `Room.inMemoryDatabaseBuilder()` in an `AndroidJUnit4` (instrumented or Robolectric) test.
*   This uses real SQLite to validate your actual queries, but disappears when the test ends.

**How to Answer:**
*   Mention that `allowMainThreadQueries()` is acceptable **only** in tests.
*   Advise using the **Turbine** library to test `Flow<List<T>>` DAOs so you can insert a row and assert the next emission immediately.

---

### Q5. [UI Testing] What is the "Robot Pattern" and why use it?
**The Mechanism:**
*   It separates the **what** (the test scenario) from the **how** (the UI interaction logic).
*   A "Robot" class defines high-level methods like `typeEmail(email)`, `clickLogin()`, and `assertErrorIsVisible()`.
*   The test class then uses these robots in a readable DSL style: `loginRobot { typeEmail("test@me.com"); clickLogin() }`.

**How to Answer:**
*   It makes tests **readable** (even for non-developers).
*   It improves **maintainability**: if a button ID changes, you only update the Robot class, not 50 different test files.

---

### Q6. [Frameworks] MockK vs. Mockito?
**The Answer:**
*   **Mockito:** The industry standard for Java. Works in Kotlin but requires `argumentCaptor` and `whenever` (from Mockito-Kotlin).
*   **MockK:** Built specifically for Kotlin. Supports **Coroutines** natively (`coEvery`, `coVerify`), **Static Mocks**, and **Final Classes** without extra configuration.

**How to Answer:**
*   Choose **MockK** for pure Kotlin projects due to its cleaner syntax and first-class coroutine support.
*   Mention that MockK can be slightly slower in build times compared to Mockito but the developer experience is significantly better.
