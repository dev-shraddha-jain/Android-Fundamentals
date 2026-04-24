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

## 🧠 Core Idea
> **Security:** Use `LocalBroadcastManager` (deprecated but still seen) or `LiveData/Flow` for internal app events to prevent external apps from intercepting your data.

## 🎯 Interview-Ready Answer

**Q: Static vs Dynamic Broadcast Receivers?**

**Answer:**
> **Static** receivers are declared in the Manifest and can wake up your app even if it's not running. **Dynamic** receivers are registered in code and only work when the component (like an Activity) is active.
