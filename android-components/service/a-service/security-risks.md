

# ⚠️ Android Security Risks in Services

This is where most candidates lose depth. Services are a **major attack surface**.

---

## 🔴 1. Exported Service Vulnerability

### Problem

If:

```xml
<service android:exported="true" />
```

👉 Any app can start or bind your service

---

### Attack Scenario

Malicious app:

```kotlin
startService(Intent().setComponent(...))
```

👉 Can:

* Trigger internal logic
* Abuse APIs
* Cause DoS

---

### Fix

```xml
<service android:exported="false" />
```

OR enforce permission:

```xml
android:permission="com.app.SECURE_PERMISSION"
```

---

## 🔴 2. Intent Injection

### Problem

Service trusts incoming intent blindly

```kotlin
val action = intent?.getStringExtra("action")
```

---

### Attack

Attacker sends crafted intent:

* Triggers unintended behavior
* Executes privileged logic

---

### Fix

* Validate:

  * Action
  * Data
  * Caller identity

```kotlin
if (intent?.action != EXPECTED_ACTION) return START_NOT_STICKY
```

---

## 🔴 3. Privilege Escalation via Service

If your service:

* Has permissions (e.g., SMS, storage)
* Is exported

👉 Other apps can **use your service as a proxy**

---

### Example

* Your app has `READ_CONTACTS`
* Malicious app calls your service
* Gets contacts indirectly

---

### Fix

* Never expose privileged services
* Use:

```xml
android:permission="signature"
```

---

## 🔴 4. Bound Service (IBinder) Abuse

### Problem

Improper binder exposure

```kotlin
override fun onBind(): IBinder {
    return myBinder
}
```

---

### Attack

Client calls internal methods:

* Executes restricted operations

---

### Fix

* Validate caller:

```kotlin
val uid = Binder.getCallingUid()
```

* Restrict access
* Avoid exposing sensitive methods

---

## 🔴 5. Denial of Service (DoS)

### Problem

Service does heavy work on main thread

---

### Attack

Attacker repeatedly starts service:

* Causes ANR
* Drains battery

---

### Fix

* Rate limit
* Move work to background thread
* Use WorkManager for heavy work

---

## 🔴 6. Foreground Service Abuse

### Problem

Misuse to run indefinitely

---

### Attack Pattern

* Malware keeps service alive using notification
* Avoids system kill

---

### Fix

* Use foreground only when justified
* Follow Play Store policies

---

## 🔴 7. Data Leakage

### Problem

Service logs sensitive info

```kotlin
Log.d("Service", "Token: $token")
```

---

### Risk

* Logs can be read (root / debug builds)

---

### Fix

* Never log secrets
* Use secure storage

---

## 🔴 8. Insecure IPC (AIDL / Messenger)

### Problem

No authentication in IPC

---

### Attack

* External app sends crafted messages

---

### Fix

* Validate caller identity
* Use permission-based binding

---

# 🧠 Senior-Level Insight

> Service = **Execution primitive**
> WorkManager = **Reliability abstraction**
> JobScheduler = **System optimization layer**

---

# 🚀 Interview Killer Statement

> “In modern Android, Services should be used sparingly—primarily as foreground services for user-visible work. For all guaranteed or deferrable background execution, WorkManager is the recommended abstraction since it internally delegates to JobScheduler and handles process death, retries, and constraints.”

---

If you want next:

* Real **secure Service implementation (production-grade)**
* OR **Top Android security scenarios asked at Google / Amazon level**

