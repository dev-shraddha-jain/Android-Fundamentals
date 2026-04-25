# Intents


## Explicit Intents

```kotlin
// Explicit intent
val intent = Intent(this, TargetActivity::class.java)
startActivity(intent)
```

to start specific components by name.

## Implicit Intents

```kotlin
// Implicit intent
val intent = Intent(Intent.ACTION_VIEW)
intent.setDataAndType(uri, "application/pdf")
startActivity(intent)
```

to request actions without specifying the handler; the system finds appropriate components based on intent filters.

### 🎬 Interactive Mechanism Walkthrough

<iframe src="intent_mechanism.html" width="100%" height="450px" style="border:none; border-radius: 8px; margin: 1.5rem 0;"></iframe>

## Example: How Android knows which app should open a PDF

Android doesn’t “guess” randomly—it uses a **well-defined intent resolution system** based on **MIME types + intent filters** to decide which app should open a PDF.

---

# 🧠 Core Idea

> The system identifies the file type (PDF) → matches it with apps that declared support → lets user choose (or auto-opens default)

---

# 🔍 Step-by-Step Flow

## 1. File Type Detection (MIME Type)

When you try to open a file:

```kotlin
val intent = Intent(Intent.ACTION_VIEW)
intent.setDataAndType(uri, "application/pdf")
```

👉 `"application/pdf"` is the **MIME type**

---

## 2. Apps Declare Support (Intent Filters)

PDF reader apps (like Adobe Acrobat Reader) declare:

```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />

    <category android:name="android.intent.category.DEFAULT" />

    <data android:mimeType="application/pdf" />
</intent-filter>
```

👉 This tells Android:

> “I can handle PDF files”

---

## 3. Intent Resolution

Android Package Manager:

* Scans all installed apps
* Matches:

  * `ACTION_VIEW`
  * `application/pdf`

👉 Builds a list of apps that can open PDF

---

## 4. Chooser / Default App

* If multiple apps:

  * Shows **chooser dialog**
* If user selected “Always”:

  * Opens directly next time

---

# 🔗 Complete Flow

```text
User taps PDF
   ↓
Intent fired (ACTION_VIEW + application/pdf)
   ↓
System checks intent filters of apps
   ↓
Matching apps found
   ↓
Chooser OR default app opens
```

---

# 📦 What If MIME Type Is Missing?

If you only pass URI:

```kotlin
intent.setData(uri)
```

👉 System may:

* Fail to resolve
* Or guess based on file extension (`.pdf`)

⚠️ Not reliable → always set MIME type

---

# 🔐 Security Perspective (Important)

* Apps **cannot open files arbitrarily**
* Must have:

  * Proper URI permission (`content://` via FileProvider)
* System enforces:

  * Access control
  * Sandboxing

---

# ⚠️ Edge Cases

### 1. No PDF app installed

* System shows:

  * “No app can open this file”

---

### 2. Malicious app registers for PDF

* Can intercept PDF open
* That’s why:

  * Users should verify default apps

---

### 3. FileProvider Required (Android 7+)

```kotlin
intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
```

---

# 🎯 Interview-Ready Answer

**Q: How does Android know which app should open a PDF?**

**Answer:**

> Android uses intent resolution. When a PDF is opened, an implicit intent with MIME type `application/pdf` is fired. The system matches this against apps that declared intent filters for that MIME type. It then either shows a chooser or launches the default app selected by the user.

---
