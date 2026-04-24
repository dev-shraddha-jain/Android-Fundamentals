# Proguard / R8

## Definition
R8 (the modern successor to Proguard) shrinks, optimizes, and obfuscates your code before it's packaged into an APK.

## 💻 Code Example (Keep Rules)

```proguard
# Prevent R8 from renaming your Data Models
-keep class com.myapp.models.** { *; }
```

## 🔍 Real-World Process: Obfuscation

```text
  [ Original Code ]           [ Obfuscated Code ]
  -----------------           -------------------
  class LoginManager {        class a {
    void authenticate() {  →    void b() {
      // Secret logic            // Secret logic
    }                         }
  }                           }
```

## 🧠 Core Idea
> **Shrinking:** Removes code that is never reached.
> **Obfuscation:** Makes reverse engineering significantly harder by renaming classes and methods to meaningless characters.

## 🎯 Interview-Ready Answer

**Q: Why is obfuscation important for security?**

**Answer:**
> It prevents attackers from easily reading your business logic if they decompile your APK. It turns readable code like `processPayment()` into `a()`, making it hard to understand the app's internal workings.
