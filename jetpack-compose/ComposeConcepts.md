# Jetpack Compose (Expert Level)

> 🎨 **[How Compose Draws UI — Interactive Visualization](./jetpack-compose/compose_draw_viz.html)**

> 📡 **[Side Effects Animated Walkthrough](./jetpack-compose/side_effects_viz.html)**

---

## 1. Recomposition

**Definition:** Recomposition is the process of Compose re-calling your composable functions whenever the state they read changes. Compose is smart — it only recomposes the composables that **read the changed state**, skipping everything else.

**Example Code:**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    // Only this composable recomposes when count changes
    Text("Count: $count")
    Button(onClick = { count++ }) { Text("Increment") }
}
```

**How it works internally:**
- Compose tracks which state objects are **read** during composition
- When state changes, only composables that **read that state** are marked for recomposition
- The Compose runtime calls those composable functions again with the new state

**Real World Example:** In a news feed screen, updating a like count only recomposes the specific `NewsCard` that was liked — not the toolbar, not the other cards, not the bottom navigation bar.

---

## 2. remember vs rememberSaveable

**Definition:**
- **`remember`**: Stores a value in memory across recompositions. Survives recomposition, but lost on Activity recreation (rotation, process death).
- **`rememberSaveable`**: Same as `remember` but also survives Activity recreation by saving to a Bundle (like `onSaveInstanceState`).

**Example Code:**
```kotlin
// remember — lost on rotation
var searchQuery by remember { mutableStateOf("") }

// rememberSaveable — survives rotation
var userInput by rememberSaveable { mutableStateOf("") }

// rememberSaveable with custom saver for complex types
var selectedUser by rememberSaveable(stateSaver = UserSaver) {
    mutableStateOf<User?>(null)
}
```

**When to use what:**
- `remember` → derived UI state, animations, scroll state within a session
- `rememberSaveable` → user input, selected tab, form data — anything the user expects to survive rotation

**Real World Example:** A search screen uses `rememberSaveable` for the query string (user typed it, expects it to survive rotation) but `remember` for keyboard visibility (transient UI state).

---

## 3. State Hoisting

**Definition:** A pattern where composable state is moved ("hoisted") up to the caller. The composable becomes stateless — it only receives state as a parameter and emits events upward via lambdas. This makes composables reusable and testable.

**Example Code:**
```kotlin
// ❌ Stateful — hard to test, hard to reuse
@Composable
fun SearchBar() {
    var query by remember { mutableStateOf("") }
    TextField(value = query, onValueChange = { query = it })
}

// ✅ Stateless — state hoisted to caller
@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit
) {
    TextField(value = query, onValueChange = onQueryChange)
}

// Parent manages state
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val query by viewModel.query.collectAsStateWithLifecycle()
    SearchBar(query = query, onQueryChange = viewModel::onQueryChange)
}
```

**Real World Example:** A `DatePickerDialog` composable that takes `selectedDate` and `onDateSelected` as parameters — it can be reused across any screen and is trivially unit-testable.

---

## 4. Side Effects

> 📡 **[View Animated Side Effects Walkthrough →](./side_effects_viz.html)**

### LaunchedEffect

**Definition:** Launches a coroutine scoped to the composable's lifetime. Re-launches when the `key` changes. Automatically cancelled when the composable leaves composition.

**Example Code:**
```kotlin
@Composable
fun UserScreen(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }

    LaunchedEffect(userId) {       // re-runs whenever userId changes
        user = repository.getUser(userId)
    }
}
```

**When to use:** API calls, starting animations, playing sounds, one-shot navigation events triggered by state.

---

### DisposableEffect

**Definition:** For effects that need **cleanup**. The `onDispose` block is guaranteed to run when the composable leaves composition or the key changes. Not a coroutine.

**Example Code:**
```kotlin
@Composable
fun LifecycleObserver(onStop: () -> Unit) {
    val lifecycleOwner = LocalLifecycleOwner.current

    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_STOP) onStop()
        }
        lifecycleOwner.lifecycle.addObserver(observer)

        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer) // cleanup
        }
    }
}
```

**When to use:** Registering/unregistering Listeners, BroadcastReceivers, LifecycleObservers, WebSocket connections, sensors.

---

### SideEffect

**Definition:** Runs after **every successful recomposition**. Not a coroutine. Used to sync Compose state to non-Compose objects.

**Example Code:**
```kotlin
@Composable
fun AnalyticsScreen(screenName: String, analytics: FirebaseAnalytics) {
    SideEffect {
        // Runs after every successful recomposition
        analytics.setCurrentScreen(screenName)
    }
}
```

**When to use:** Syncing to analytics SDKs, changing system UI (status bar color), updating third-party non-Compose views.

---

## 5. DerivedStateOf

**Definition:** Used to create state that is computed from other state. The derived value only triggers recomposition when its **result actually changes** — not every time the source state changes. Essential for performance.

**Example Code:**
```kotlin
@Composable
fun ContactsList(contacts: List<Contact>) {
    val listState = rememberLazyListState()

    // ✅ Only recomposes when isScrolled changes (true/false)
    // NOT on every single scroll pixel
    val showScrollToTop by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }

    if (showScrollToTop) {
        ScrollToTopButton()
    }
}
```

**Real World Example:** Showing a "Scroll to Top" FAB only after the list scrolls past item 0. Without `derivedStateOf`, every scroll pixel would trigger a recomposition.

---

## 6. SnapshotFlow

**Definition:** Converts Compose state into a cold Flow. Allows you to use Flow operators (`filter`, `debounce`, `distinctUntilChanged`) on Compose state — bridging the Compose snapshot system with the coroutines world.

**Example Code:**
```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel) {
    val searchState = rememberLazyListState()

    LaunchedEffect(searchState) {
        snapshotFlow { searchState.firstVisibleItemIndex }
            .distinctUntilChanged()
            .filter { it > 5 }
            .collect { viewModel.onScrolledPastFifthItem() }
    }
}
```

**Real World Example:** Debouncing a scroll listener so the ViewModel is only notified when scrolling actually stabilizes — not on every frame.

---

## 7. Navigation Compose

**Definition:** Jetpack Navigation ported for Compose. Uses a `NavController` and `NavHost` with string routes to manage the back stack and navigate between composable screens.

**Example Code:**
```kotlin
@Composable
fun AppNavGraph() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(onNavigate = { navController.navigate("detail/42") })
        }
        composable(
            route = "detail/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.IntType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getInt("userId")
            DetailScreen(userId = userId)
        }
    }
}
```

**Real World Example:** A shopping app with `Home → ProductDetail → Checkout` where tapping Back correctly pops the back stack and the ViewModel scoped to the navigation destination is automatically cleared.

---

## 8. Performance Optimization

**Definition:** Strategies to minimize unnecessary recompositions and improve rendering performance.

**Key techniques:**
- **Stable types:** Mark data classes with `@Stable` or `@Immutable` so Compose can skip recomposition when params haven't changed
- **`remember`:** Cache expensive computations across recompositions
- **`derivedStateOf`:** Prevent over-triggering recomposition from high-frequency state
- **`key()`:** Help Compose correctly identify items in dynamic lists
- **Lambda stability:** Avoid passing non-stable lambdas inline; use `rememberUpdatedState`

**Example Code:**
```kotlin
// ✅ @Immutable tells Compose this type's fields never change
@Immutable
data class User(val id: Int, val name: String)

// ✅ Stable lambda reference prevents recomposition
@Composable
fun ItemList(items: List<User>, viewModel: MyViewModel) {
    val onClick = remember { viewModel::onItemClick }
    items.forEach { ItemRow(it, onClick) }
}
```

---

## 9. LazyColumn Optimization

**Definition:** `LazyColumn` only composes and draws visible items. To optimize it, ensure items have stable keys, avoid creating new lambda instances on each call, and use `@Stable` item models.

**Example Code:**
```kotlin
LazyColumn(
    state = rememberLazyListState(),
    contentPadding = PaddingValues(16.dp)
) {
    items(
        items = userList,
        key = { user -> user.id },   // ✅ Stable keys — prevents unnecessary recomposition on list changes
        contentType = { "UserCard" } // ✅ contentType — allows Compose to reuse composition slots
    ) { user ->
        UserCard(user = user)
    }
}
```

**Real World Example:** A chat app with 1000+ messages. `key = { it.messageId }` ensures that when a new message arrives at the bottom, only the new item is composed — not the entire list.

---

## 10. Custom UI Drawing (Canvas)

**Definition:** Compose provides a `Canvas` composable giving direct access to `DrawScope` for custom 2D rendering. Use for charts, graphs, progress indicators, or any non-standard UI that cannot be built with standard components.

**Example Code:**
```kotlin
@Composable
fun CircularProgressBar(progress: Float) {
    Canvas(modifier = Modifier.size(120.dp)) {
        // Draw background track
        drawArc(
            color = Color.LightGray,
            startAngle = -90f,
            sweepAngle = 360f,
            useCenter = false,
            style = Stroke(width = 12.dp.toPx(), cap = StrokeCap.Round)
        )
        // Draw progress arc
        drawArc(
            color = Color(0xFF7C3AED),
            startAngle = -90f,
            sweepAngle = 360f * progress,
            useCenter = false,
            style = Stroke(width = 12.dp.toPx(), cap = StrokeCap.Round)
        )
    }
}
```

**Real World Example:** A fitness app drawing a circular ring progress indicator for daily step goals — impossible to achieve cleanly with standard Material components.

---

## 🎯 Interview Questions

### Q1. How does recomposition work?

**Answer:** When a composable reads a state object, Compose's snapshot system registers it as a **subscriber** to that state. When state changes, Compose marks those composables as **invalid** and schedules recomposition on the next frame. The runtime then re-calls those specific composable functions. Composables whose inputs haven't changed are **skipped** — this is called "smart recomposition". Compose achieves this by comparing previous parameters with new parameters and skipping if they are equal (stable types only).

---

### Q2. How to prevent unnecessary recomposition?

**Answer:**
1. **Use `@Stable` / `@Immutable`** on your data classes so Compose knows it can skip recomposition when parameters are equal
2. **Use `remember`** to cache computed values instead of recomputing on every recomposition
3. **Use `derivedStateOf`** for state derived from other state — avoids triggering recomposition on every intermediate value
4. **Hoist state** so stateless composables only recompose when their direct parameters change
5. **Use stable `key` in `LazyColumn`** to help Compose correctly identify unchanged items

---

### Q3. Compose vs XML?

| Aspect | Jetpack Compose | XML Views |
|---|---|---|
| **Paradigm** | Declarative | Imperative |
| **State management** | Automatic (state → UI) | Manual (`setText`, `setVisibility`) |
| **Recomposition** | Smart partial recomposition | Full view redraw |
| **Interop** | `AndroidView` wraps Views | N/A |
| **Testing** | `ComposeTestRule`, semantic tree | Espresso, robolectric |
| **Performance** | Better for dynamic UIs | Better for static layouts |
| **Animations** | First-class Animate APIs | Animator XML, `ObjectAnimator` |
| **Code** | Kotlin-only, no XML | XML + Kotlin/Java |

**Interview answer:** Compose is **declarative** — you describe *what* the UI should look like for a given state, and Compose figures out *how* to update it. XML is **imperative** — you manually tell the View system *what to do* when state changes. Compose's smart recomposition is more efficient for dynamic UIs because it only updates what changed, while `invalidate()` in the View system redraws entire subtrees.

---

> 🎨 **[Open Compose Draw Mechanism Visualizer →](./compose_draw_viz.html)**
> 📡 **[Open Side Effects Visualizer →](./side_effects_viz.html)**
