# Interview QnA: Build & App Structure

### Q1. [How Mechanism] How does the system choose which DEX file to load first in a multi-DEX APK?
**The Mechanism:**
*   The primary `classes.dex` contains the startup classes (Application, Splash screen, etc.).
*   Secondary DEX files (`classes2.dex`, etc.) are loaded as needed or during app startup if using the `MultiDex` library.
*   The `MainDexList` configuration determines which classes MUST go into the primary DEX.

**How to Answer:**
*   Explain the 65k method limit that led to Multi-DEX.
*   Mention that modern Android (API 21+) handles Multi-DEX natively via the ART runtime.

---

### Q2. [Tricky] Why are resources like strings and layouts compiled into binary XML?
**The Reason:**
*   Parsing plain text XML at runtime is slow and memory-intensive.
*   Binary XML is pre-parsed and optimized for the Android system to read quickly.

**How to Answer:**
*   Focus on **Performance** and **Battery Life**.
*   Mention that compilation happens during the build process so the phone doesn't have to do it.

---

### Q3. [What If] What if you include a 10MB image in the `res/drawable/` folder?
**The Impact:**
*   The APK size will increase significantly.
*   Loading that image into memory will consume a large portion of the app's heap, potentially leading to an `OutOfMemoryError`.

**How to Answer:**
*   Advise against large assets in the APK.
*   Suggest using **Vector Drawables** for icons and **WebP** or optimized JPGs for photos.
*   Mention "Dynamic Delivery" (AAB) to serve specific image sizes to specific devices.
