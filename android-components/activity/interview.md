# 🧪 Tricky Android Activity Lifecycle Questions

This is where most candidates slip. Answer these **without guessing**; each targets a real-world edge case.


### Q1. Rotation Trap

You rotate the device while an Activity is visible.

**Question:**
What exact lifecycle sequence is called?

Also:

* Is the same Activity instance reused?
* How do you persist UI state correctly?


```text
onPause → onStop → onDestroy → onCreate → onStart → onResume
```

**Answer:**

**Instance reused?:** **No** → New Activity instance is created

**State handling:** Used viewmodel, savedstatehandle, onSaveInstanceState also expected

---

### Q2. onPause vs onStop (Execution Risk)

You are saving critical user data.

**Question:**
Where should you save it: `onPause()` or `onStop()`?
What happens if the process is killed right after `onPause()`?

**Answer:**

**Save in**: onPause() (for critical, quick data)
**Heavy work**: onStop()

**if process is killed right after onpause then:** onSaveInstanceState not called

```text
onPause → (process killed)
```
---

### Q3. onDestroy Myth

**Statement:**

> “onDestroy is always called before an Activity is killed.”

**Question:**
Is this true or false? Justify with a real scenario.

**Answer:** 

False

**Explanation:**
System kill (low memory)
Process death skips onDestroy

---

### Q4. Home vs Back Button

User presses:

### Case A: Home

### Case B: Back

**Question:**
What lifecycle methods are called in each case?
What is the key difference in system behavior?

**Answer:**

Case A: Home

```text
onPause → onStop
```
Case B: Back

```text
onPause → onStop → onDestroy
```

👉 **Difference:** ❌ No onResume/onStart on back press

---

### Q5. App in Background → Killed → Reopened

Flow:

1. User opens app
2. Presses Home
3. System kills process (low memory)
4. User opens app again

**Question:**
Which lifecycle methods are called when reopening?
Will `onRestart()` be called?

**Answer:**

```text
onCreate → onStart → onResume
```

👉 **onRestart:** ❌ Not called (because old process is gone)

---

### Q6. Multiple Activities Stack

You have:

* `ActivityA → ActivityB`

User presses Back from B.

**Question:**
What lifecycle methods are called on:

* ActivityB
* ActivityA


**Answer:**


ActivityB (finishing)
```text
onPause → onStop → onDestroy
```
ActivityA (coming back)
```text
onRestart → onStart → onResume
```

👉 **Order matters:** Resume always last

---

### Q7. Dialog / Transparent Activity

You open a **dialog-themed Activity** on top of another Activity.

**Question:**
Will underlying Activity get:

* `onPause()`?
* `onStop()`?

Explain why.


**Answer:**

`onPause()`? → YES
`onStop()`? → NO

**Reason:**
Activity is partially visible but not interactive

---

### Q8. Long Operation Mistake

You run a **network call in onResume()**.

**Question:**
What lifecycle issue can this cause?
What is the better architectural approach?


**Answer:**

Problem:
`onResume()` called multiple times → duplicate API calls

Better approach:

Use `ViewModel + Repository`
Trigger once using:

`init {}`  in ViewModel

or lifecycle-aware observer

---

## Q9. Launch Mode Twist

Activity launchMode = `singleTop`

You call `startActivity()` again for same Activity already on top.

**Question:**
Which method is called instead of creating a new instance?

**Answer:**

`onNewIntent()`

👉 Existing instance reused

---

### Q10. Process Death Recovery

App is killed in background.

**Question:**
Which method is used to restore UI state?

* `onSaveInstanceState()` OR `onDestroy()`?

Explain flow clearly.

**Answer:**

`onSaveInstanceState()`
Used to save the UI state before process death.

```text
onPause → onStop → process killed
→ onCreate(savedInstanceState) → onStart → onResume
```

👉 Restore from Bundle

---

### Q11. Cold vs Warm vs Hot Start

Define:

* Cold start
* Warm start
* Hot start

And map lifecycle methods involved in each.

**Answer:**


| Type       | Meaning                | Lifecycle                      |
| ---------- | ---------------------- | ------------------------------ |
| Cold Start | App not in memory      | onCreate → onStart → onResume  |
| Warm Start | In memory, not visible | onRestart → onStart → onResume |
| Hot Start  | Already visible        | onResume                       |


---

### Q12. Lifecycle + ViewModel

Why does **ViewModel survive rotation but not process death**?

**Answer:**

ViewModel survives rotation because it is tied to the Activity's lifecycle, but not the process's lifecycle.
When the Activity is recreated (due to rotation), the ViewModel is not recreated.
When the process is killed (due to low memory), the ViewModel is also killed.
