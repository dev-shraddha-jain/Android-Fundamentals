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
