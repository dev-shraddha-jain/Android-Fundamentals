# 🎨 Jetpack Compose Internals: The Under-the-Hood View

Compose is a **declarative** UI toolkit, but its internal engine is a sophisticated state-management and tree-manipulation system.

---

### 1. The Three Phases of Compose
Compose transforms data into UI in three distinct steps:
1.  **Composition:** *What to show.* Executes `@Composable` functions and builds a description of the UI (the Composition Tree).
2.  **Layout:** *Where to show it.* Measures and positions UI elements. Consists of two sub-phases: measurement and placement.
3.  **Drawing:** *How it looks.* Renders the UI elements onto a Canvas.

**Optimization:** Compose can skip phases if the data hasn't changed. For example, if only a color changes, it might skip Composition and Layout and go straight to Drawing.

---

### 2. The SlotTable (The Memory)
Compose doesn't use a traditional View tree. Instead, it uses a **Gap Buffer** called the **SlotTable**.
*   When a `@Composable` function runs, it "writes" information into the SlotTable (parameters, state, etc.).
*   **Gap Buffer Advantage:** It is extremely efficient at inserting/deleting elements at a specific point (the "gap"), which happens frequently during recomposition.
*   The SlotTable allows Compose to remember what was rendered in the previous pass to perform efficient diffing.

---

### 3. Recomposition & The Snapshot System
How does Compose know when to redraw?
*   **Snapshots:** Compose uses a global Snapshot system (similar to Git). When you change a `mutableStateOf` value, it records a "mutation" in the current snapshot.
*   **Tracking:** Any `@Composable` function that reads a state value during Composition is automatically registered as a "listener" for that state.
*   **Trigger:** When the snapshot is "applied," Compose identifies all affected composables and schedules them for recomposition.

---

### 4. Stability & Smart Recomposition
Compose tries to be "smart" to avoid unnecessary work.
*   **Stable Types:** If a type is stable (primitive, String, or marked `@Stable`), Compose knows that if the object instance is the same, the data is the same. It can **skip** recomposition.
*   **Unstable Types:** Classes with `var` properties or those from external libraries are often considered "unstable." Compose will always recompose if an unstable object is passed as a parameter, even if it hasn't changed.
*   **Fix:** Use `@Immutable` or `@Stable` annotations, or use Kotlinx Collections which are treated as stable.

---

### 5. Side-Effects: Bridging to the Imperative World
Composables should be side-effect free. When you need to interact with the outside world (API calls, timers), use Side-Effect APIs:
*   **LaunchedEffect:** Runs a block of code when a specific key changes. It is cancelled when the composable leaves the composition.
*   **SideEffect:** Runs after every successful recomposition. Use it to share Compose state with non-Compose managed objects.
*   **DisposableEffect:** Used for effects that need cleanup (e.g., registering/unregistering a listener).

---

### 🎯 Interview QnA

#### Q: What is "State Hoisting"?
**Answer:**
State hoisting is a pattern of moving state to a composable's caller to make the composable **stateless**. This makes the component more reusable, easier to test, and allows a single source of truth.

#### Q: How does Compose handle "Position Memoization"?
**Answer:**
Compose uses the `key` composable to uniquely identify elements in a list. Without `key`, if you insert an item at the top of a list, Compose might think every item has changed because their "index" changed in the SlotTable. `key` helps Compose track identity across recompositions.

#### Q: What is the `remember` block?
**Answer:**
`remember` is a way to store an object in the **SlotTable**. During recomposition, instead of re-executing the calculation, Compose returns the value stored during the initial composition. If the composable is removed from the tree, the value is forgotten.
