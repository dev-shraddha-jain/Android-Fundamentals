# Activity

## Definition

A core building block representing a **single screen** with a **user interface**. It acts as the **entry point** for user interaction.

Lifecycle owmer tied to window.

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

**1. You tap the app icon →**

Intent goes to Android system


**2. Android checks →**

"Is this app already running?"


**3. If NO →**

System creates a fresh process (like opening a new app)


**4. If YES →**

System reuses the existing process


**5. Activity starts →**

onCreate → onStart → onResume



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