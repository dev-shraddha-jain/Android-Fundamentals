# Resource Analysis

## Definition
Resources in Android are the non-code assets (XML layouts, images, strings) that are packaged into the APK. Analyzing them is crucial for understanding UI structure and identifying potential data leaks.

---

## 📂 The `res/` Directory
| Folder | Content | Analysis Tip |
| :--- | :--- | :--- |
| **layout/** | XML UI definitions. | Check for deep nesting (overdraw). |
| **values/** | Strings, colors, styles. | Search for hardcoded API keys or secrets. |
| **drawable/** | Images and icons. | Check for unoptimized large bitmaps. |
| **raw/** | Arbitrary files (e.g., JSON, Media). | Often contains config files. |

## 🔍 The Compilation Process
When an app is built, resources are compiled into binary XML and a unique integer ID is assigned in the `R.java` file.
*   **`resources.arsc`**: A lookup table that maps resource IDs (e.g., `0x7f040001`) to their actual values or paths.

---

## 🎯 Interview-Ready Answer (Senior)

**Q: What is the difference between `res/` and `assets/`?**

**Answer:**
> `res/` is compiled. Every item in `res/` gets an ID in the `R` class, allowing the system to optimize access and handle configuration changes (like `-land` or `-night`) automatically. `assets/` are raw files; they don't get IDs and must be accessed via `AssetManager` with a file path string.

---

**Q: How do resource qualifiers work under the hood?**

**Answer:**
> When a resource is requested (e.g., `R.layout.main`), the Android system checks the current device configuration (Language, Screen density, Orientation). It matches these against the qualifiers on the folders (e.g., `layout-land` or `values-hi`) and selects the most specific match.
