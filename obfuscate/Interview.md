# Interview QnA: Proguard & R8

### Q1. [How Mechanism] How does R8 differentiate between used and unused code?
**The Mechanism:**
*   R8 starts from "Entry Points" (Classes/Methods defined in your Manifest or keep rules).
*   It builds a "Call Graph" to see which methods and classes are reachable from those entry points.
*   Any code not reachable in the graph is considered "Dead Code" and is stripped away.

**How to Answer:**
*   Describe the process as "Tree Shaking".
*   Explain that this is why "Keep Rules" are necessary for code accessed via Reflection—R8 cannot see those connections in the static call graph.

---

### Q2. [Tricky] If R8 obfuscates your code, why is your `mapping.txt` file sensitive?
**The Reason:**
*   The `mapping.txt` is essentially the "Translation Key".
*   Anyone with the APK and the mapping file can perfectly reconstruct your original class and method names.
*   Leaking this file makes your obfuscation useless for security.

**How to Answer:**
*   Highlight that `mapping.txt` should be treated like a private key.
*   Mention that it should be archived for every release build to debug crashes.

---

### Q3. [What If] What if you use Reflection to call a method that R8 has obfuscated?
**The Result:**
*   A `NoSuchMethodException` will occur at runtime.
*   R8 renamed the method to something like `a()`, but your reflection code is looking for `"myMethod"`.

**How to Answer:**
*   Identify this as a common "Release-only" bug.
*   Explain the fix: Add a `-keep` rule for that specific class or method in your `proguard-rules.pro` file.


### Q4. [Internals] What is the difference between "Shrinking", "Optimization", and "Obfuscation" in R8?

**The Answer:**
*   **Shrinking:** Removes unused code and resources (Tree shaking).
*   **Optimization:** Performs various optimizations like inlining methods and merging classes.
*   **Obfuscation:** Renames classes/methods/fields to short names (e.g., `a`, `b`).

**How to Answer:**
*   Explain that Shrinking and Optimization happen **first**, and Obfuscation happens **last**.


### Q5. [Best Practices] When would you use `-keep` vs `-keepnames` vs `-keepclassmembers`?

**Answer:**

* **`-keep`**: Keeps the class and all its members (methods and fields). Use this for entry points like Activity, Service, and BroadcastReceiver.
* **`-keepnames`**: Keeps the class name, but allows its members to be renamed. Use this when reflection relies on class names but not method names.
* **`-keepclassmembers`**: Keeps the members (methods and fields) but allows the class itself to be renamed. Use this for classes that are instantiated via reflection (e.g., custom Views) but whose method names are fixed.


### Q6. [Advanced] How do you handle custom Views (e.g., `MyCustomView`) that are inflated using XML or custom attributes?

**Answer:**
You must use `-keep` to preserve the class name and its constructors.

```
-keep class com.example.myapp.views.** { *; }
-keep class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
}
```

### Q7. [Tricky] What is the difference between `minifyEnabled` and `obfuscate` in `build.gradle`?

**Answer:**
`minifyEnabled true` is the main switch in your `build.gradle` that enables the R8/ProGuard tool. This tool handles three distinct phases: **Shrinking** (removing unused code/resources), **Optimization**, and **Obfuscation**. There is no separate `obfuscate` flag in Gradle; instead, obfuscation is a sub-feature of minification. If you want to shrink code but *not* obfuscate it (common for library debugging), you keep `minifyEnabled true` but add `-dontobfuscate` to your `proguard-rules.pro` file.


### Q8 Your release app crashes only in **release build**, debug works fine. Likely due to R8/ProGuard. Explain full debugging mechanism:

* Why debug works but release crashes
* What shrinking/obfuscation changes
* Reflection issue examples
* How mapping.txt helps
* How to fix systematically



### Why debug works but release crashes

* Debug usually has no shrinking/obfuscation.
* Release enables R8, which may:

  * remove “unused” code
  * rename symbols
  * optimize call paths

### Why it breaks

R8 uses static reachability analysis. Dynamic usages are hard to infer:

* reflection
* JNI native bindings
* JSON serialization
* XML-instantiated classes
* annotation processors / generated code
* JavaScript bridges

### mapping.txt use

* Convert obfuscated stacktrace:

  * `a.a.a(Unknown Source)` → real class/method
* Essential for crash tools (Crashlytics, Play Console)

### Fix systematically

1. Reproduce on release locally
2. Get stacktrace + deobfuscate with mapping
3. Identify dynamic access path
4. Add narrow keep rules
5. Rebuild + retest
6. Avoid blanket keep-all rules

```pro
-keep class com.example.model.** { *; }
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}
-keepclasseswithmembers class * {
    native <methods>;
}
```

