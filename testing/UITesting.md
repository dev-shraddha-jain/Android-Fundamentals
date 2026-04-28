# UI Testing — Android (Expert Level)

UI tests verify the complete user-facing behavior on a real device or emulator. Android has two UI testing frameworks: **Espresso** (View-based) and **Compose Testing** (Jetpack Compose).

---

## 1. Espresso (View-based UI Testing)

**Definition:** Google's UI testing library for View-based apps. Uses `onView()` matchers to find views, `perform()` to interact, and `check()` to verify.

**Example Code:**
```kotlin
@RunWith(AndroidJUnit4::class)
class LoginActivityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun validLogin_navigatesToDashboard() {
        onView(withId(R.id.etEmail))
            .perform(typeText("alice@example.com"), closeSoftKeyboard())

        onView(withId(R.id.etPassword))
            .perform(typeText("password123"), closeSoftKeyboard())

        onView(withId(R.id.btnLogin))
            .perform(click())

        onView(withId(R.id.dashboardTitle))
            .check(matches(isDisplayed()))
    }

    @Test
    fun emptyEmail_showsError() {
        onView(withId(R.id.btnLogin)).perform(click())

        onView(withText("Email is required"))
            .check(matches(isDisplayed()))
    }

    @Test
    fun recyclerViewItem_click() {
        onView(withId(R.id.recyclerView))
            .perform(RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(0, click()))

        onView(withId(R.id.detailTitle))
            .check(matches(isDisplayed()))
    }
}
```

---

## 2. Compose UI Testing

**Definition:** Jetpack Compose's built-in test APIs. Uses a semantic tree (accessibility tree) to find composables by content description, text, or test tag.

**Example Code:**
```kotlin
@RunWith(AndroidJUnit4::class)
class UserScreenTest {

    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun loadButton_showsUserCard_onSuccess() {
        val fakeRepo = FakeUserRepository(User("1", "Alice"))

        composeRule.setContent {
            UserScreen(viewModel = UserViewModel(fakeRepo))
        }

        // Click the load button
        composeRule.onNodeWithText("Load User").performClick()

        // Verify user name is displayed
        composeRule.onNodeWithText("Alice").assertIsDisplayed()
    }

    @Test
    fun loadingState_showsProgressIndicator() {
        composeRule.setContent {
            UserScreen(state = UiState.Loading)
        }

        composeRule.onNodeWithTag("loading_indicator").assertIsDisplayed()
        composeRule.onNodeWithText("Load User").assertIsNotEnabled()
    }

    @Test
    fun errorState_showsRetryButton() {
        composeRule.setContent {
            UserScreen(state = UiState.Error("Network error"))
        }

        composeRule.onNodeWithText("Network error").assertIsDisplayed()
        composeRule.onNodeWithText("Retry").assertIsDisplayed()
    }
}

// Add test tag in composable
@Composable
fun UserScreen(...) {
    if (state is UiState.Loading) {
        CircularProgressIndicator(modifier = Modifier.testTag("loading_indicator"))
    }
}
```

---

## 3. UI Test with Hilt (Dependency Injection)

**Definition:** When using Hilt DI, UI tests need `HiltAndroidRule` to inject fakes/mocks into the app's DI graph.

**Example Code:**
```kotlin
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class DashboardScreenTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeRule = createAndroidComposeRule<MainActivity>()

    @BindValue @JvmField
    val fakeRepo: UserRepository = FakeUserRepository() // replaces real implementation

    @Test
    fun dashboard_displaysUserName() {
        composeRule.onNodeWithText("Alice").assertIsDisplayed()
    }
}
```

---

## 4. Testing Navigation

**Definition:** Verifying that clicking UI elements triggers the correct navigation destination using `TestNavHostController`.

**Example Code:**
```kotlin
@RunWith(AndroidJUnit4::class)
class NavigationTest {

    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun clickingItem_navigatesToDetail() {
        val navController = TestNavHostController(ApplicationProvider.getApplicationContext())

        composeRule.setContent {
            navController.setGraph(R.navigation.main_nav)
            DashboardScreen(onItemClick = { navController.navigate("detail/$it") })
        }

        composeRule.onNodeWithText("Item 1").performClick()

        assertThat(navController.currentDestination?.route).isEqualTo("detail/{id}")
    }
}
```

---

## 5. Key Testing Pyramid

```
        ┌────────────────────┐
        │     UI Tests       │  ← slow, run on device, test full flows
        │  (Espresso/Compose)│
        ├────────────────────┤
        │ Integration Tests  │  ← medium, test component interactions
        │ (Room, MockWebServer│
        ├────────────────────┤
        │    Unit Tests      │  ← fast, isolated, run on JVM
        │  (JUnit + MockK)   │
        └────────────────────┘
```

**Rule of thumb:** 70% unit · 20% integration · 10% UI tests — not the inverse.
