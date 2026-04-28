# Performance Optimization — Android (Expert Level)

---

## 1. App Startup Optimization

**Definition:** App startup is measured in three modes:
- **Cold start** — process does not exist, system creates it from scratch (slowest)
- **Warm start** — process exists but Activity was destroyed (re-creates Activity)
- **Hot start** — process and Activity exist in memory, just brought to foreground (fastest)

Target: **Cold start < 500ms** on mid-range devices. The startup critical path is:
`Zygote fork → Application.onCreate() → Activity.onCreate() → First frame rendered`

**Techniques:**

**1. Baseline Profiles** — pre-compile hot code paths into native machine code before the user ever runs them:
```kotlin
// Generate with Macrobenchmark
@ExperimentalBaselineProfilesApi
class BaselineProfileGenerator {
    @get:Rule val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(packageName = "com.example.app") {
        pressHome()
        startActivityAndWait()
        // Walk critical user journeys
        device.findObject(By.text("Dashboard")).click()
    }
}
```

**2. App Startup Library** — defer initialization of heavy SDKs until after the first frame:
```kotlin
// Replace Application.onCreate() SDK init with lazy Initializer
class FirebaseInitializer : Initializer<FirebaseApp> {
    override fun create(context: Context): FirebaseApp {
        return FirebaseApp.initializeApp(context)!!
    }
    override fun dependencies() = emptyList<Class<out Initializer<*>>>()
}

// In AndroidManifest.xml — provider handles ordering automatically
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup">
    <meta-data android:name="com.example.FirebaseInitializer"
               android:value="androidx.startup.Initializer" />
</provider>
```

**3. Defer heavy work from Application.onCreate():**
```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // ✅ Only critical SDK — crash reporter must init early
        FirebaseCrashlytics.getInstance()

        // ✅ Defer everything else to a background thread
        applicationScope.launch(Dispatchers.Default) {
            AnalyticsSDK.init(this@MyApp)
            ImageLoader.init(this@MyApp)
        }
    }
}
```

**4. Splash Screen API** — eliminates the blank white screen during startup:
```kotlin
installSplashScreen().setKeepOnScreenCondition {
    !viewModel.isInitialized.value  // keeps splash until VM is ready
}
```

**Real World Example:** A fintech app reduced cold start from 2.1s to 680ms by generating a Baseline Profile, moving analytics SDK init to a background coroutine, and using the Splash Screen API.

---

## 2. Memory Leaks

**Definition:** A memory leak occurs when an object that is no longer needed is still referenced, preventing the GC from reclaiming its memory. Over time, leaks cause `OutOfMemoryError` and app crashes.

**Common sources in Android:**

| Leak Source | Why |
|---|---|
| Static reference to Context/Activity | Outlives the Activity lifecycle |
| Inner class holding Activity reference | Non-static inner class has implicit `this` reference |
| Unregistered listeners/callbacks | BroadcastReceiver, LocationListener not removed |
| Handler with delayed messages | `Handler.postDelayed` keeps Activity alive |
| Coroutine in wrong scope | `GlobalScope` doesn't cancel on Activity destroy |

**Example Code:**
```kotlin
// ❌ Classic leak — static reference to Activity
class MySingleton {
    companion object {
        var context: Context? = null  // LEAK if Activity is passed
    }
}

// ✅ Fix — use applicationContext, never Activity
MySingleton.context = context.applicationContext

// ❌ Leak via anonymous listener
class MyActivity : AppCompatActivity() {
    override fun onResume() {
        locationManager.requestUpdates(listener)  // listener holds Activity ref
    }
    // Missing onPause() → listener never removed
}

// ✅ Fix
override fun onPause() {
    super.onPause()
    locationManager.removeUpdates(listener)  // always clean up
}

// ❌ Leak via Handler
val handler = Handler(Looper.getMainLooper())
handler.postDelayed({ updateUI() }, 5000)  // Activity may be gone in 5s

// ✅ Fix — cancel in onDestroy
override fun onDestroy() {
    super.onDestroy()
    handler.removeCallbacksAndMessages(null)
}
```

**Detection — LeakCanary:**
```kotlin
// Add to debug dependencies only
debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
// That's it — LeakCanary auto-detects and shows a notification with the leak trace
```

**Real World Example:** A chat app had memory growing with every message — caused by a `MessageAdapter` holding a strong reference to the Activity through a non-static anonymous click listener. Fixed by making the listener a `WeakReference` and removing it in `onDetachedFromRecyclerView`.

---

## 3. ANR Debugging

**Definition:** Application Not Responding (ANR) occurs when the main thread is blocked for more than **5 seconds** (for user input) or **10 seconds** (for `BroadcastReceiver`). The system shows the "App isn't responding" dialog.

**Common causes:**
- Network/database call on main thread
- Acquiring a lock held by a background thread
- Long `BroadcastReceiver.onReceive()` 
- Heavy computation on main thread (bitmap decoding, JSON parsing)

**Example Code:**
```kotlin
// ❌ ANR cause — database call on main thread
val user = db.userDao().getUser("1")  // blocks main thread!

// ✅ Fix — move to coroutine
lifecycleScope.launch {
    val user = withContext(Dispatchers.IO) {
        db.userDao().getUser("1")
    }
    updateUI(user)
}

// ❌ ANR in BroadcastReceiver — long work in onReceive()
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        processHeavyData()  // ❌ blocks — receiver has 10s limit
    }
}

// ✅ Fix — delegate to a Service or WorkManager
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        WorkManager.getInstance(context).enqueue(
            OneTimeWorkRequestBuilder<DataProcessingWorker>().build()
        )
    }
}
```

**Reading ANR traces:**
```bash
# ANR trace file location
adb pull /data/anr/anr_YYYY-MM-DD-HH-MM-SS.txt

# Look for the main thread stack:
# "main" prio=5 tid=1 MONITOR  ← blocked on a lock
#   at com.example.UserRepository.getUser(UserRepository.kt:45)
#   waiting to lock <0x12345678> (held by thread 12)
```

---

## 4. StrictMode

**Definition:** A developer tool that detects accidental disk/network operations on the main thread and other policy violations at runtime. Logs or crashes the app with a detailed stack trace.

**When to use:** During development only — never in production.

**Example Code:**
```kotlin
class MyApp : Application() {
    override fun onCreate() {
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectDiskReads()
                    .detectDiskWrites()
                    .detectNetwork()        // catches all network on main thread
                    .detectCustomSlowCalls()
                    .penaltyLog()           // logcat warning
                    // .penaltyDeath()      // crash immediately (strictest)
                    .build()
            )
            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectLeakedSqlLiteObjects()
                    .detectLeakedClosableObjects()
                    .detectActivityLeaks()
                    .penaltyLog()
                    .build()
            )
        }
        super.onCreate()
    }
}
```

**Real World Example:** StrictMode revealed that a legacy `SharedPreferences.edit().commit()` call (synchronous disk write) was happening on the main thread during Activity launch — causing a 40ms jank spike. Fixed by switching to `apply()` (asynchronous).

---

## 5. Systrace / Perfetto

**Definition:** System-level tracing tool that records CPU scheduling, thread activity, and method timings across the entire Android system — not just your app. Replaced by **Perfetto** in Android 10+. Identifies jank, scheduling delays, and lock contention.

**How to capture:**
```bash
# Capture a 10-second Perfetto trace
adb shell perfetto -o /data/misc/perfetto-traces/trace.perfetto-trace \
    -t 10s \
    sched freq idle am wm gfx view binder_driver hal dalvik camera res

adb pull /data/misc/perfetto-traces/trace.perfetto-trace

# View at: https://ui.perfetto.dev
```

**Custom trace events in your code:**
```kotlin
// Add custom events visible in the trace
fun loadFeed() {
    Trace.beginSection("FeedViewModel.loadFeed")
    try {
        // work here
    } finally {
        Trace.endSection()
    }
}

// Or with the AndroidX tracing library
trace("FeedViewModel.loadFeed") {
    // work here
}
```

**What to look for:**
- **Janky frames** — frames taking > 16ms (60fps budget)
- **Main thread blocked** — long stretches with no work (waiting for lock/IO)
- **Binder calls** — excessive IPC to system services

---

## 6. Android Profiler

**Definition:** Android Studio's built-in profiler suite with four specialized profilers — **CPU**, **Memory**, **Network**, and **Energy**. The primary tool for identifying performance bottlenecks without needing command-line tools.

**CPU Profiler — finding jank:**
```kotlin
// Trigger method tracing programmatically
Debug.startMethodTracing("my_trace")
// ... code to profile
Debug.stopMethodTracing()
// Pull: adb pull /sdcard/my_trace.trace
```

**Memory Profiler — spotting leaks:**
1. Run the app, navigate to the suspected screen
2. Click **Force GC** in the profiler
3. If heap size doesn't drop → leak
4. Take a heap dump → find objects with unexpected retention path

**Network Profiler:**
- Visualizes all HTTP requests with timing, size, and payload
- Identifies redundant API calls or large uncompressed payloads

**Energy Profiler:**
- Shows CPU, network, and GPS wakelock usage
- Identifies battery drain from background work

---

## 7. Battery Optimization

**Definition:** Mobile apps must minimize battery consumption by batching work, avoiding unnecessary wakeups, and respecting system power-saving modes (Doze, App Standby).

**Key rules:**
- Never hold a `WakeLock` longer than necessary
- Use `WorkManager` instead of foreground services for deferrable work
- Batch network requests — avoid polling, prefer push (FCM)
- Use `JobScheduler` constraints to run work only when charging

**Example Code:**
```kotlin
// ✅ WorkManager with battery-friendly constraints
val syncRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
            .setRequiresBatteryNotLow(true)                // skip when battery < 20%
            .setRequiresCharging(false)                    // don't require charging
            .build()
    )
    .build()

// ❌ Avoid polling — use FCM push instead
handler.postDelayed({ checkForUpdates() }, 60_000)  // every minute drains battery

// ✅ FCM — server pushes when there's actually data
// FirebaseMessagingService.onMessageReceived() handles it
```

**Battery Historian:**
```bash
# Reset battery stats, use app, then pull
adb shell dumpsys batterystats --reset
# ... use the app ...
adb bugreport bugreport.zip
# Upload bugreport.zip to: https://bathist.ef.lc/
```

---

## 8. Lazy Loading

**Definition:** Deferring the initialization or loading of objects and data until they are actually needed — reducing startup time and memory footprint.

**Android lazy loading patterns:**

**1. Kotlin `by lazy` — single-instance lazy init:**
```kotlin
// Initialized on first access, not at class instantiation
val heavyHelper: ImageProcessor by lazy {
    ImageProcessor(context)  // allocated only when first accessed
}
```

**2. `LazyColumn` / `LazyRow` — lazy UI:**
```kotlin
// Only composes and draws visible items
LazyColumn {
    items(1000) { index ->
        ListItem(index)  // items off-screen are never composed
    }
}
```

**3. Lazy image loading with Coil:**
```kotlin
// Image is loaded only when the composable enters the visible viewport
AsyncImage(
    model = ImageRequest.Builder(context)
        .data(imageUrl)
        .crossfade(true)
        .diskCachePolicy(CachePolicy.ENABLED)
        .memoryCachePolicy(CachePolicy.ENABLED)
        .build(),
    contentDescription = "User avatar"
)
```

**4. Fragment lazy loading:**
```kotlin
// Load fragment only when tab is first selected — not on ViewPager creation
viewPager.offscreenPageLimit = 1  // only keep 1 adjacent page in memory
```

**5. Pagination as a form of lazy loading:**
```kotlin
// Load 20 items at a time — not all 10,000 at startup
Pager(PagingConfig(pageSize = 20)) { MyPagingSource() }
    .flow.collectAsLazyPagingItems()
```

---

## 🎯 Interview Quick Reference

| Tool / Concept | What it catches |
|---|---|
| **LeakCanary** | Memory leaks with retention path |
| **StrictMode** | Main thread IO/network violations |
| **Profiler (Memory)** | Heap growth, leak candidates |
| **Profiler (CPU)** | Method hotspots, jank frames |
| **Perfetto/Systrace** | System-wide scheduling, Binder IPC |
| **Battery Historian** | Wakelocks, alarm abuse, drain cause |
| **Baseline Profile** | Reduces cold start via AOT compilation |
| **WorkManager constraints** | Defers work to battery/network-friendly windows |