# Senior Java Developer Notes (Deep Mechanism Revision)

Concise, interview-grade notes focused on **internals + senior-level understanding**.

---

# 1. JVM Architecture

## Components

* **Class Loader** → loads `.class`
* **Runtime Data Areas**

  * Heap
  * Stack
  * Metaspace
  * PC Register
  * Native Method Stack
* **Execution Engine**

  * Interpreter
  * JIT Compiler
* **GC**

## Flow

```text
.java -> javac -> .class -> JVM loads -> verifies -> executes
```

---

# 2. Class Loading Mechanism

## Phases

1. Loading
2. Linking

   * Verification
   * Preparation
   * Resolution
3. Initialization

## ClassLoaders

* Bootstrap
* Platform
* Application

## Parent Delegation

When class requested:

```text
AppLoader asks Parent
Parent asks Bootstrap
If found stop
Else child loads
```

Prevents fake core classes.

---

# 3. Memory Areas

## Heap

Stores objects.

## Stack

Stores:

* method frames
* local variables
* references

## Metaspace

Stores class metadata.

## PC Register

Current instruction pointer.

---

# 4. Object Creation Mechanism

```java
User u = new User();
```

## Internally

1. Class loaded if not loaded
2. Memory allocated in heap
3. Default values assigned
4. Constructor runs
5. Reference stored in stack

---

# 5. Stack vs Heap

| Stack          | Heap          |
| -------------- | ------------- |
| Thread private | Shared        |
| Method calls   | Objects       |
| Fast access    | Larger memory |
| Auto cleanup   | GC cleanup    |

---

# 6. Garbage Collection

## Removes unreachable objects.

```java
obj = null;
```

If no reference remains → eligible.

## Generations

* Young Gen
* Old Gen

## GC Types

* Minor GC
* Major GC
* Full GC

## Common Collectors

* G1GC
* ZGC
* ParallelGC

---

# 7. Why Memory Leak in Java?

Java has GC, but leaks happen when references remain.

Example:

```java
static List list = new ArrayList();
list.add(bigObject);
```

Static ref prevents cleanup.

---

# 8. String Internals

## Why Immutable?

* Security
* Thread-safe
* String pool
* HashMap key safe

## Pool

```java
String a = "abc";
String b = "abc";
```

Same pooled object.

---

# 9. == vs equals()

```java
==        -> reference compare
equals()  -> value compare
```

---

# 10. StringBuilder vs StringBuffer

| Builder          | Buffer       |
| ---------------- | ------------ |
| Fast             | Thread-safe  |
| Not synchronized | synchronized |

---

# 11. OOP Core

## Encapsulation

Hide data via private fields.

## Inheritance

Reuse parent features.

## Polymorphism

Same method different behavior.

## Abstraction

Expose needed details only.

---

# 12. Overloading vs Overriding

| Overloading      | Overriding     |
| ---------------- | -------------- |
| Same method name | Parent-child   |
| Different params | Same signature |
| Compile time     | Runtime        |

---

# 13. Runtime Polymorphism

```java
Animal a = new Dog();
a.sound();
```

Runtime decides Dog method.

Uses **dynamic dispatch**.

---

# 14. final Keyword

## final variable

Cannot reassign.

## final method

Cannot override.

## final class

Cannot inherit.

---

# 15. Collections Hierarchy

```text
Collection
 ├── List
 ├── Set
 └── Queue

Map separate
```

---

# 16. ArrayList Internals

* Dynamic array
* Indexed fast access O(1)
* Insert middle costly

Resize by creating larger array.

---

# 17. LinkedList

* Doubly linked nodes
* Insert/delete easier
* Access slower

---

# 18. HashMap Internals (Must Know)

## put(k,v)

1. hash(key)
2. bucket index
3. If empty → insert
4. Collision:

   * linked list
   * tree after threshold

## Important

* Load factor default 0.75
* Resize doubles capacity

## Why immutable key?

Changing key breaks lookup.

---

# 19. HashSet

Uses HashMap internally.

```java
map.put(value, PRESENT)
```

---

# 20. Thread Basics

## Ways

```java
extends Thread
implements Runnable
ExecutorService
Callable
```

---

# 21. Thread Lifecycle

```text
NEW
RUNNABLE
RUNNING
WAITING/BLOCKED
TERMINATED
```

---

# 22. synchronized

Locks object monitor.

```java
synchronized(obj) { }
```

Only one thread enters.

## Types

* Instance lock
* Class lock (static synchronized)

---

# 23. volatile

Guarantees:

* visibility
* ordering

Not atomicity.

```java
volatile boolean flag;
```

---

# 24. Atomic Classes

```java
AtomicInteger
```

Uses CAS.

Good for counters.

---

# 25. Deadlock

Two threads waiting forever.

```text
T1 holds A waits B
T2 holds B waits A
```

Prevent:

* lock ordering
* timeout locks

---

# 26. ExecutorService

Better than manual threads.

```java
Executors.newFixedThreadPool(4)
```

Benefits:

* reuse threads
* queue tasks
* control resources

---

# 27. Callable vs Runnable

| Runnable             | Callable      |
| -------------------- | ------------- |
| No return            | Returns value |
| No checked exception | Can throw     |

---

# 28. Java Memory Model

Defines thread visibility rules.

Important:

* happens-before
* synchronization visibility

---

# 29. Exceptions

## Checked

Compile-time checked.

```java
IOException
```

## Unchecked

Runtime.

```java
NullPointerException
```

---

# 30. try-with-resources

Auto closes resources.

```java
try(FileInputStream f = ...)
```

---

# 31. Generics

```java
List<String>
```

Compile-time type safety.

## Runtime

Uses **type erasure**.

---

# 32. Wildcards

```java
<? extends Number>
<? super Integer>
```

PECS:

* Producer extends
* Consumer super

---

# 33. Stream API

```java
list.stream()
.filter()
.map()
.collect()
```

## Lazy

Runs only terminal operation.

---

# 34. Reflection

Access runtime metadata.

```java
Class.forName()
getMethods()
```

Used by Spring/Hibernate.

---

# 35. Serialization

Convert object to bytes.

```java
implements Serializable
```

Use `serialVersionUID`

---

# 36. Common Performance Rules

* Prefer StringBuilder in loops
* Use primitives where possible
* Avoid unnecessary objects
* Use proper collection type
* Tune thread pools
* Watch GC pauses

---

# 37. Senior Interview Hot Questions

## Q. Why HashMap not thread-safe?

Multiple threads corrupt buckets / resize issue.

## Q. Why ConcurrentHashMap?

Safe concurrent access.

## Q. Why String immutable?

Pool + security + thread-safe.

## Q. Why volatile not enough for count++?

Because increment is multiple steps.

## Q. Why use ExecutorService?

Thread reuse and control.

---

# 38. Must Master Internals

* HashMap
* synchronized
* volatile
* class loading
* GC
* String pool
* thread pool
* JMM

---

# 39. If You’re Android Senior Dev

Extra revise:

* Handler / Looper
* Memory leaks
* ANR causes
* Threading model
* JNI basics
* ProGuard/R8
* Collections optimization

---

# 40. Golden Rule

For every topic know:

```text
What
Why
How internally
When use
When avoid
Complexity
Thread safety
```

---

# If you want, I can also make **Senior Java Notes PDF**, **100 Interview Q&A**, or **Java Internals Diagram Notes** next.
