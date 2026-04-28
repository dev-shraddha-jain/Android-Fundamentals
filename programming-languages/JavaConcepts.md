# JAVA Concepts (Core of Android)

## 🔹 1. OOP Principles (Core of Android)

### Definition

Object-Oriented Programming organizes code using objects and classes.

### Key Concepts

### Encapsulation

- Binding data + methods together
- Use `private` fields + getters/setters
- Prevents unauthorized access

**Android Example**

- ViewModel exposes LiveData but hides mutable state

```
privateMutableLiveData<String>data=newMutableLiveData<>();
publicLiveData<String>getData() {returndata; }
```

---

### Inheritance

- One class acquires properties of another
- Promotes code reuse

**Android Example**

- `MainActivity extends AppCompatActivity`

---

### Polymorphism

- Same method behaves differently
- Method overloading / overriding

**Android Example**

- `onClick()` implemented differently in different classes

---

### Abstraction

- Hiding implementation details
- Using abstract classes/interfaces

**Android Example**

- `RecyclerView.Adapter` defines structure, you implement logic

---

### Interview Q&A

**Q: Why is encapsulation important in Android?**

A: Prevents direct mutation of UI/state → avoids bugs, improves maintainability.

**Q: Difference between abstraction and encapsulation?**

A:

- Encapsulation = data hiding
- Abstraction = hiding complexity

---

## 🔹 2. JVM Memory Model

### Definition

How memory is allocated and managed in Java.

### Components

- Heap → Objects
- Stack → Method calls
- Method Area → Class metadata

---

### Android Relevance

- Memory leaks (Context, Activity references)
- GC pauses → UI jank

---

### Real Example

- Static reference to Activity → leak

```
staticActivityactivity;// ❌ memory leak
```

---

### Interview Q&A

**Q: Why do memory leaks happen in Android?**

A: Long-lived references to short-lived objects (Activity, Context)

---

## 🔹 3. Garbage Collection (GC)

### Definition

Automatic memory cleanup of unused objects.

### Key Points

- Runs on heap
- Non-deterministic
- Can cause UI lag if frequent

---

### Android Example

- Bitmap not recycled → memory pressure

---

### Interview Q&A

**Q: Can we force GC?**

A: `System.gc()` is just a suggestion, not guaranteed.

---

## 🔹 4. Multithreading

### Definition

Running multiple tasks concurrently.

---

### Key Concepts

### Thread

Basic unit of execution

### Runnable

Task to run on thread

### Synchronization

Avoid race conditions

---

### Android Mapping

- Network calls → background thread
- UI updates → main thread

```
runOnUiThread(() ->textView.setText("Updated"));
```

---

### Real Scenario

- API call on main thread → ANR

---

### Interview Q&A

**Q: What is ANR?**

A: App Not Responding when main thread blocked > 5 sec

---

## 🔹 5. Executor Framework

### Definition

Manages thread pools instead of manual threads

---

### Example

```
ExecutorServiceexecutor=Executors.newFixedThreadPool(2);
executor.execute(() ->fetchData());
```

---

### Android Use

- Background tasks
- Better than raw Threads

---

### Interview Q&A

**Q: Why Executors over Threads?**

A: Reuse threads → better performance

---

## 🔹 6. Collections Framework

### Definition

Data structures for storing/managing data

---

### Common Types

### List (ArrayList)

- Ordered
- Allows duplicates

### Set (HashSet)

- No duplicates

### Map (HashMap)

- Key-value pairs

---

### Android Example

- RecyclerView list data

---

### Interview Q&A

**Q: Difference between ArrayList and LinkedList?**

A:

- ArrayList → fast access
- LinkedList → fast insert/delete

---

## 🔹 7. Exception Handling

### Definition

Handling runtime errors gracefully

---

### Types

- Checked → compile-time
- Unchecked → runtime

---

### Example

```
try {
inta=10/0;
}catch (ArithmeticExceptione) {
Log.e("Error",e.getMessage());
}
```

---

### Android Scenario

- API failure handling
- JSON parsing issues

---

### Interview Q&A

**Q: Difference between throw and throws?**

A:

- throw → actually throws exception
- throws → declares exception

---

## 🔹 8. Interfaces vs Abstract Classes

### Interface

- Only method declarations (Java 7)
- Multiple inheritance

### Abstract Class

- Can have implementation
- Single inheritance

---

### Android Example

- Interface → click listeners
- Abstract → BaseActivity

---

### Interview Q&A

**Q: When to use interface?**

A: When multiple classes need same contract

---

## 🔹 9. Static Keyword

### Definition

Belongs to class, not object

---

### Uses

- Constants
- Utility methods

---

### Android Example

```
publicstaticfinalStringTAG="MainActivity";
```

---

### Risk

- Memory leaks if holding context

---

### Interview Q&A

**Q: Can static cause leaks?**

A: Yes, if it holds Activity/Context

---

## 🔹 10. Singleton Pattern

### Definition

Only one instance of a class exists

---

### Example

```
publicclassAppManager {
privatestaticAppManagerinstance;

publicstaticAppManagergetInstance() {
if (instance==null)instance=newAppManager();
returninstance;
    }
}
```

---

### Android Use

- Retrofit client
- Database instance

---

### Interview Q&A

**Q: Is Singleton thread-safe?**

A: Not by default → use synchronized or double-check locking

---

## 🔹 11. Serialization

### Definition

Convert object → byte stream

---

### Android Use

- Passing data (less used now)
- Prefer Parcelable

---

### Interview Q&A

**Q: Serializable vs Parcelable?**

A: Parcelable is faster (Android optimized)

---

## 🔹 12. Annotations

### Definition

Metadata for code

---

### Android Examples

- `@Override`
- `@Nullable`
- `@WorkerThread`

---

### Interview Q&A

**Q: Why annotations?**

A: Compile-time checks + better readability

---

## 🔹 13. Reflection

### Definition

Inspect/modify classes at runtime

---

### Android Use

- Libraries
- Dependency injection

---

### Risk

- Slow
- Security concerns

---

### Interview Q&A

**Q: Why avoid reflection?**

A: Performance overhead + harder to debug

---

## 🔹 14. Volatile & Synchronization

### volatile

- Ensures visibility across threads

### synchronized

- Ensures mutual exclusion

---

### Example

```
volatilebooleanisRunning=true;
```

---

### Interview Q&A

**Q: volatile vs synchronized?**

A:

- volatile → visibility
- synchronized → visibility + atomicity

---

## 🔹 15. Immutable Objects

### Definition

Object state cannot change after creation

---

### Example

```
finalclassUser {
privatefinalStringname;
}
```

---

### Android Benefit

- Thread-safe
- Avoid bugs

---

### Interview Q&A

**Q: Why immutable objects?**

A: Safe in multi-threading

---

# 🔥 FINAL INTERVIEW RAPID FIRE

- Why avoid heavy work on main thread?

> Heavy work on main thread → blocks UI → ANR (App Not Responding)


- Difference between HashMap vs ConcurrentHashMap?

> HashMap → not thread-safe
> ConcurrentHashMap → thread-safe


- What causes memory leaks in Android?

> Static references to Activity/Context
> Non-static inner classes
> Unregistered listeners
> Resources not closed

- Why use WeakReference?

> Allows GC to collect object when no longer needed

- What is Looper & Handler?

> Looper → message pump
> Handler → post/process messages

- Difference between Thread, AsyncTask, Executor?

> Thread → manual thread management
> AsyncTask → deprecated
> Executor → thread pool

- Why Parcelable preferred?

> Android optimized → faster than Serializable


- What is StrictMode?

> Debug tool to detect accidental disk/network access on main thread