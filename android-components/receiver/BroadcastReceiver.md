# Broadcast Receivers

## Definition
A component that allows your app to listen for system-wide events or custom events from other apps.

## 💻 Code Example

```kotlin
// Dynamic Registration
val br: BroadcastReceiver = MyBroadcastReceiver()
val filter = IntentFilter(Intent.ACTION_BATTERY_LOW)
registerReceiver(br, filter)
```

## 🔍 Real-World Process: The Event Model

```text
  [ System Event ] (e.g., Battery Low)
          ↓
  [ Package Manager ]
          ↓
  [ Scans Intent Filters ]
          ↓
  +----------------------+
  | Match Found in App A | → [ Triggers onReceive ]
  +----------------------+
          ↓
  +----------------------+
  | Match Found in App B | → [ Triggers onReceive ]
  +----------------------+
```

### 🎬 Interactive Mechanism Walkthrough

<iframe src="broadcast_receiver_mechanism.html" width="100%" height="450px" style="border:none; border-radius: 8px; margin: 1.5rem 0;"></iframe>


## Local Broadcast Receiver

* `LocalBroadcastManager` was used for sending broadcasts **inside the same app only**.
* Broadcast does **not leave the app process/package**.
* More secure than global broadcasts because other apps cannot receive or send it.
* Used for internal communication between:

  * Activity
  * Fragment
  * Service
  * Other app components

### Why It Was Used

* Notify UI when background task completed.
* Send status updates from Service to Activity.
* Lightweight event communication inside app.


```kotlin
// Sender
val intent = Intent("MY_ACTION")
intent.putExtra("data", "some_data")

LocalBroadcastManager.getInstance(context).sendBroadcast(intent)

// Receiver
val receiver = object : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        val data = intent?.getStringExtra("data")
        // Update UI
    }
}

LocalBroadcastManager.getInstance(context).registerReceiver(receiver,IntentFilter("MY_ACTION"))

```


### Example Use Case

* Download Service finishes file.
* Sends local broadcast.
* Activity receives update and refreshes UI.

For scnerios, refer to [scenerio](scenrio.md).

### Advantages

* Secure (app-internal only)
* Efficient compared to system-wide broadcast
* No inter-app exposure
* Easy decoupled communication

### Important Current Status

* `LocalBroadcastManager` is **deprecated**.
* Google recommends modern alternatives:

  * `LiveData`
  * `StateFlow`
  * `SharedFlow`
  * `ViewModel`
  * Observer pattern / callbacks

### Interview Important Point

* Earlier used for intra-app communication.
* Deprecated because reactive observable patterns are cleaner and lifecycle-aware.

### Security Perspective

* Better than exported/global broadcast because no external app can intercept or spoof events.

### Short Interview Answer

* Local Broadcast Receiver was used to send broadcasts within same app only. It improved security and efficiency, but now deprecated and replaced by LiveData/Flow/ViewModel based communication.



## 🧠 Core Idea
> **Security:** Use `LocalBroadcastManager` (deprecated but still seen) or `LiveData/Flow` for internal app events to prevent external apps from intercepting your data.

## 🎯 Interview-Ready Answer

**Q: Static vs Dynamic Broadcast Receivers?**

**Answer:**
> **Static** receivers are declared in the Manifest and can wake up your app even if it's not running. **Dynamic** receivers are registered in code and only work when the component (like an Activity) is active.
