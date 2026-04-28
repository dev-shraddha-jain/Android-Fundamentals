# Activity

## Definition

A core building block representing a **single screen** with a **user interface**. It acts as the **entry point** for user interaction.

Lifecycle owner tied to window.

## 💻 Code Example

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

## 🔗 Real-World Process: The Lifecycle Flow

```text
[ Activity starts ]
        ↓
onCreate()   → Setup everything (UI, data, init)
        ↓
onStart()    → Screen becomes visible
        ↓
onResume()   → User can interact (active state)
        ↓
[ App is running ]
        ↓
onPause()    → User leaves partially (another screen on top)
        ↓
onStop()     → Screen not visible anymore
        ↓
onDestroy()  → Activity is removed, clean up
        ↓
[ Activity ends ]
```

### 🎬 Interactive Lifecycle Walkthrough

> 🔗 **[Open Activity Lifecycle Visualizer →](./activity_lifecycle.html)**

## One-line memory trick:
**Create → Start → Resume → Pause → Stop → Destroy**

## 🧠 Core Idea
> Activities are managed by the **Activity Manager Service (AMS)**. They live in **Tasks** (a collection of activities the user interacts with).

## ⚠️ Edge Case: Configuration Changes
When you rotate the screen, the system **destroys** and **recreates** the Activity by default.
*   **Solution:** Use `ViewModel` to persist data.

## 🎯 Interview-Ready Answer

**Q: What happens when an Activity is recreated during rotation?**

**Answer:**

 The system calls `onPause`, `onStop`, and `onDestroy`. 

Then it starts fresh with `onCreate`, `onStart`, and `onResume`. To prevent data loss, developers use `ViewModel` or `onSaveInstanceState`.

## Launch Modes

Launch modes control how a new instance of an Activity is associated with the current task.

Declared in `AndroidManifest.xml`:
```xml
<activity
    android:name=".MyActivity"
    android:launchMode="singleTop" />
```

| Mode | Behaviour | Use Case |
|------|-----------|----------|
| **standard** | Always creates a new instance | Default — most Activities |
| **singleTop** | Reuses if already at top of stack (via `onNewIntent()`) | Notification targets, search |
| **singleTask** | Only one instance system-wide; clears stack above it | Home/dashboard screens |
| **singleInstance** | Sole Activity in its own exclusive task | System-wide pickers, call screens |

### 🎬 Interactive Launch Modes Walkthrough (A → B → A)

> 🔗 **[Open Launch Modes Visualizer →](./activity_launch_modes.html)**


## Important Real-World Notes (Interview Gold)

###  onPause()
      * Very short execution time
      * Don’t do heavy work
      * Used for:
          * pause video
          * save small data
### onStop()
      * UI not visible
      * Safe for heavier work:
          * DB writes
          * releasing resources
          
### onDestroy()
      * Not always guaranteed (system kill)
      * Don’t rely on it for critical logic
      
### System Kill Scenario (Low Memory)
      
      * No lifecycle methods guaranteed after:

```text
onStop → (process killed)
```

      * That’s why:
      * Use persistent storage (Room/DataStore)
      * Don’t depend only on lifecycle

-------------------------------------------------------

## 🚀 How an Activity is Launched

The launch process is orchestrated by the **Activity Manager Service (AMS)**.


### 🔍1.  Launch Flowchart

```text
       
User / App triggers Intent
        ↓
Android resolves target Activity (via Manifest)
        ↓
Request goes to ActivityManagerService (AMS)
        ↓
If app process NOT running → Zygote forks new process
        ↓
ActivityThread (main thread) is created
        ↓
Activity instance is created
        ↓
Lifecycle starts:
onCreate → onStart → onResume

```

> Launch Process Simple words (no flow chart) 

- **User taps icon** in Launcher app.
- **Launcher fires an Intent** (ACTION_MAIN + CATEGORY_LAUNCHER) to the system via Binder.
- **AMS/ATMS resolves target**: System identifies the target activity and checks task/back stack state.
- **Zygote Forks**: If no process exists, Zygote forks a new process preloaded from the VM image.
- **ActivityThread.main()**: Child process starts the app’s main thread.
- **Setup Looper**: Main thread sets up Looper, message queue, and Binder plumbing.
- **System Binds**: System sends a bind request; `LoadedApk` loads the app code.
- **Application Created**: `attachBaseContext()` → `Application.onCreate()` runs first.
- **Schedule Activity**: System schedules the target activity launch transaction.
- **Reflection**: Instrumentation creates the Activity instance via reflection.
- **Lifecycle Begins**: `Activity.attach()` runs, then `onCreate()`, `onStart()`, and `onResume()`.



## 2. Ways an Activity Can Be Launched

### ✅ A. From Launcher (App icon tap)
Launcher app sends an implicit intent

```kotlin
<intent-filter>
    <action android:name="android.intent.action.MAIN"/>
    <category android:name="android.intent.category.LAUNCHER"/>
</intent-filter>

```

👉 System finds this as entry point
### ✅ B. From Another Activity (Explicit Intent)

```kotlin
val intent = Intent(this, SecondActivity::class.java)
startActivity(intent)

```

👉 Direct class reference → fastest resolution

### ✅ C. Implicit Intent (System decides)

```kotlin
val intent = Intent(Intent.ACTION_VIEW)
intent.data = Uri.parse("https://google.com")
startActivity(intent)

```

👉 System matches:
action
data
category

### ✅ D. From Notification / PendingIntent

```kotlin
val intent = Intent(this, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(
    this, 0, intent, PendingIntent.FLAG_IMMUTABLE
)

```

👉 Used when launching from:

notifications
alarms

### ✅ E. From ADB (Debugging)

```kotlin
adb shell am start -n com.example/.MainActivity
```

### 3. Deep internal flow 
Launch:
onCreate → onStart → onResume

Background:
onPause → onStop

Return:
onRestart → onStart → onResume

Finish:
onPause → onStop → onDestroy


## 🎯 When Does Zygote Fork?

| Scenario | Process Status | Action |
|----------|----------------|--------|
| Fresh Install | No Process | Fork New |
| Cold Start | No Process | Fork New |
| User Kills App | No Process | Fork New |
| Existing App | Running Process | Use Existing |

## 🧠 Core Idea
> Activities are managed by the **Activity Manager Service (AMS)**. They live in **Tasks** (a collection of activities the user interacts with).