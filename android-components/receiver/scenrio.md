# Auto Start / Restart App on System Boot (Interview Answer)

### Requirement

* Start app logic automatically when device reboots.
* Common use cases:

  * Reschedule alarms
  * Restart background sync
  * Start foreground service
  * Restore scheduled WorkManager jobs

## Use `BOOT_COMPLETED` BroadcastReceiver

### Manifest Permission

```xml id="6n8w9u"
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
```

### Register Receiver

```xml id="kjf6j9"
<receiver
    android:name=".BootReceiver"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED"/>
    </intent-filter>
</receiver>
```

### Receiver Code

```kotlin id="1g0m0w"
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {

            // restart work
            val serviceIntent = Intent(context, MyService::class.java)
            context.startForegroundService(serviceIntent)
        }
    }
}
```

## Important Modern Android Notes

* Cannot freely launch UI Activity on boot.
* Background execution limits apply.
* Prefer:

  * `WorkManager`
  * `ForegroundService`
  * Re-schedule alarms/jobs

## Best Production Approach

* On boot:

  * Recreate notifications
  * Restart sync scheduler
  * Restore reminders
  * Resume pending uploads

## Security / Play Store Notes

* Auto-starting intrusive UI on boot is bad UX.
* Must have clear user value.
* Avoid hidden background abuse.

## Interview Short Answer

* Use `BOOT_COMPLETED` receiver with `RECEIVE_BOOT_COMPLETED` permission.
* Receiver runs after reboot and restarts required services/jobs.
* On modern Android, prefer WorkManager or foreground service due to background restrictions.

## Senior-Level Answer

* I would not “start the app UI”; instead I would restore essential background tasks and state in a compliant way after boot.


---

# Notify Changes

 **Scenario:** Splash max 2 sec, Config API takes 10 sec, Login screen needs data

## Core Problem

* Splash screen should not block user for 10 sec.
* Login screen depends on config API data.
* Need good UX + non-blocking startup.

---

##  Approach 1: 

### 1. Start Config API in Splash immediately

* Fire config API call as soon as app launches.
* Do not wait entire 10 sec on splash.

### 2. Keep Splash max 2 sec

* Show splash for branding/loading only.
* After 2 sec navigate to Login.

### 3. Continue API in background

* Use:

  * ViewModel
  * Repository
  * Coroutine
  * Singleton cache
  * DataStore / Room

### 4. Login screen observes config state

* Login opens with:

  * loading state
  * disabled login button (if config mandatory)
  * shimmer / progress

* Once config arrives:

  * populate values
  * enable login

---

## Architecture Flow

* App Launch
* Splash starts API
* 2 sec timeout
* Navigate Login
* Login subscribes to config state
* API success after 10 sec
* UI updates automatically

---

## Approach 2 : Using LocalBroadCasReceiver ( Deprecated )

This approach would work , but it is not recommended because LocalBroadCasReceiver is deprecated.

### Example Code

```kotlin
// Create a BroadcastReceiver
private val configReceiver = object : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == "CONFIG_READY") {
            val config = intent.getParcelableExtra<Config>("config")
            // Update Login UI with config
        }
    }
}

// Register receiver in SplashActivity
LocalBroadcastManager.getInstance(this).registerReceiver(
    configReceiver,
    IntentFilter("CONFIG_READY")
)

// Start API and send broadcast when ready
startApiService() // Calls LocalBroadcastManager.sendBroadcast(...) when API completes
```

