# 🏗️ App Architecture — MVVM vs MVI

> 🎬 **[Open MVVM vs MVI Interactive Visualizer →](./mvvm_mvi_viz.html)**

---

## 1. MVVM — Model · View · ViewModel

**Definition:** MVVM separates an app into three layers:
- **Model** — data layer: repositories, data sources, network/database calls
- **View** — UI layer: Activity, Fragment, or Composable. Only renders state, never holds business logic
- **ViewModel** — logic layer: survives configuration changes, exposes UI state via `StateFlow` / `LiveData`, has no reference to the View

The View **observes** the ViewModel's exposed state. The ViewModel calls the Model. There is no direct dependency from ViewModel → View.

**Example Code:**
```kotlin
// Model (Repository)
class UserRepository(private val api: UserApi) {
    suspend fun getUser(id: String): User = api.getUser(id)
}

// ViewModel
class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                _uiState.value = UiState.Success(repo.getUser(id))
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }
}

// View (Composable)
@Composable
fun UserScreen(vm: UserViewModel = hiltViewModel()) {
    val state by vm.uiState.collectAsStateWithLifecycle()
    when (state) {
        is UiState.Loading -> LoadingSpinner()
        is UiState.Success -> UserCard((state as UiState.Success).user)
        is UiState.Error   -> ErrorMessage((state as UiState.Error).msg)
    }
    Button(onClick = { vm.loadUser("42") }) { Text("Load User") }
}
```

**Real World Example:** A standard news feed app where the ViewModel fetches articles from a repository and exposes them as a `StateFlow<List<Article>>` that the composable collects and renders into a `LazyColumn`.

---

## 2. MVI — Model · View · Intent

**Definition:** MVI enforces **strict unidirectional data flow** inspired by Redux. Every user action is an **Intent** (sealed class), the ViewModel passes it through a **Reducer** that produces a new immutable **State**. The View only renders state and emits intents — it never modifies state directly.

- **Model** — current app state (single immutable data class)
- **View** — renders State, emits Intents
- **Intent** — a sealed class describing every possible user action
- **Reducer** — pure function: `reduce(currentState, intent) → newState`

**Example Code:**
```kotlin
// Intent — all user actions as a sealed class
sealed class UserIntent {
    data class LoadUser(val id: String) : UserIntent()
    object Refresh : UserIntent()
    object ClearError : UserIntent()
}

// State — single source of truth (immutable)
data class UserState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
)

// ViewModel with intent processing
class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val intentChannel = Channel<UserIntent>(Channel.UNLIMITED)

    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            intentChannel.consumeAsFlow().collect { intent ->
                reduce(_state.value, intent)
            }
        }
    }

    private suspend fun reduce(current: UserState, intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUser -> {
                _state.value = current.copy(isLoading = true, error = null)
                try {
                    val user = repo.getUser(intent.id)
                    _state.value = current.copy(isLoading = false, user = user)
                } catch (e: Exception) {
                    _state.value = current.copy(isLoading = false, error = e.message)
                }
            }
            UserIntent.Refresh -> reduce(current.copy(user = null), UserIntent.LoadUser("42"))
            UserIntent.ClearError -> _state.value = current.copy(error = null)
        }
    }

    fun sendIntent(intent: UserIntent) {
        viewModelScope.launch { intentChannel.send(intent) }
    }
}

// View
@Composable
fun UserScreen(vm: UserViewModel = hiltViewModel()) {
    val state by vm.state.collectAsStateWithLifecycle()
    Button(onClick = { vm.sendIntent(UserIntent.LoadUser("42")) }) { Text("Load") }
    Button(onClick = { vm.sendIntent(UserIntent.Refresh) }) { Text("Refresh") }
}
```

**Real World Example:** A multi-step payment checkout screen where every user action (enter card, select address, apply coupon, confirm) is an Intent and the entire checkout state is one `CheckoutState` object — making it trivially debuggable and testable.

---

## 3. MVVM vs MVI — Difference

| Aspect | MVVM | MVI |
|---|---|---|
| **Data Flow** | Bidirectional (View ↔ ViewModel) | Strict Unidirectional (circular) |
| **State** | Multiple StateFlows / LiveData properties | Single immutable State data class |
| **User actions** | Direct ViewModel function calls | Typed Intent sealed class |
| **Reducer** | No explicit reducer | Pure `reduce(state, intent)` function |
| **Predictability** | Good | Excellent — 100% deterministic |
| **Testability** | Good | Excellent (test the pure reducer function) |
| **Boilerplate** | Low | High (Intent + State + Reducer per screen) |
| **Debugging** | Standard | Replay any state from event log |
| **Learning curve** | Low | Steep |

---

## 4. When to Choose Which?

### Choose MVVM when:
- Standard CRUD, list/detail, or settings screens
- Small-to-medium complexity UI with few concurrent actions
- Smaller teams or newer Android developers
- Tight deadlines where boilerplate is a concern
- Using Google Architecture Components natively (Hilt + ViewModel + StateFlow)

### Choose MVI when:
- Complex multi-state screens (payment flows, booking wizards, forms)
- Many concurrent user actions that can modify the same piece of state
- Need for time-travel debugging or strict auditability of state transitions
- High automated test coverage is mandatory (pure reducer is trivially testable)
- Team has background in Redux, Flux, or Elm architecture patterns

---

## 5. Interview Answer (Senior Level)

**Q: What is the key difference between MVVM and MVI?**

> **MVVM** is the Google-recommended pattern where the ViewModel holds mutable state and the View observes it. It's bidirectional — the View can call any function on the ViewModel. This is flexible but can lead to scattered state across multiple StateFlows.
>
> **MVI** enforces a strict unidirectional cycle: the View emits typed **Intents**, the ViewModel processes them through a pure **Reducer** function, and the new **State** flows back to the View. The entire screen's state is one immutable data class. This makes every state transition 100% deterministic and reproducible — critical for complex or regulated flows like payments.
>
> In practice, I default to MVVM for standard screens and reach for MVI when the screen has complex concurrent actions, or when audit trails and testability are a hard requirement.

---

> 🎬 **[Open MVVM vs MVI Interactive Visualizer →](android-architecture/mvvm_mvi_viz.html)**
