# Java & Kotlin Interoperability

## 🔍 The Bridge
Since both Java and Kotlin compile to the same **JVM Bytecode**, they can exist in the same project and call each other seamlessly.

### 1. Calling Java from Kotlin
*   **Properties:** Java getters/setters (`getName()`, `setName()`) are accessed as properties (`user.name`).
*   **Platform Types:** Java types are seen as `T!` (could be null or not). Kotlin doesn't enforce null checks here unless you add `@Nullable` or `@NotNull` in Java.

### 2. Calling Kotlin from Java (The "Jvm" Annotations)
Kotlin generates code that looks natural to Java using these annotations:

| Annotation | Purpose | Result in Java |
| :--- | :--- | :--- |
| **`@JvmStatic`** | Makes a member of an `object` a real static method. | `MyObject.method()` |
| **`@JvmOverloads`** | Generates multiple Java methods for default parameters. | Multiple overloaded methods. |
| **`@JvmField`** | Exposes a property as a public field instead of a getter. | `myObject.field` |
| **`@JvmName`** | Changes the name of the generated Java class or method. | `UtilsKt` becomes `MyUtils`. |

## 🧠 Real-World Scenario: Migration
Most companies migrate by converting one file at a time. 
1.  **Step 1:** Convert Data Models to Kotlin (Data Classes).
2.  **Step 2:** Convert Utility classes.
3.  **Step 3:** Convert Activities/Fragments.

> **Pro Tip:** Keep your internal APIs in Kotlin but use `@JvmStatic` and `@JvmOverloads` if you still have Java consumers to keep their code clean.

---

## 🎯 Interview-Ready Answer (Senior)

**Q: What is a "Platform Type" and how do you handle it?**

**Answer:**
> A Platform Type is a type that comes from Java code where nullability is not specified (no `@Nullable` or `@NonNull` annotation). In Kotlin, it is represented with an exclamation mark (e.g., `String!`). You should handle it cautiously by checking for null or, better yet, by adding proper annotations to the Java source code so Kotlin can treat it as a safe non-nullable or nullable type.
