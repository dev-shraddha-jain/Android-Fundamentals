# Guide to Creating a Vulnerable Android App (Jetpack Compose)

This guide outlines how to build a sample Android application using **Jetpack Compose**, specifically designed for reverse engineering practice. We will intentionally include common vulnerabilities and "protection" mechanisms.

---

## 1. Project Setup
Create a new Android Studio project with **Empty Compose Activity**.
- **Name**: `RE-Target-App`
- **Package Name**: `com.example.retarget`
- **Language**: Kotlin

---

## 2. Hardcoded Secrets
In Compose, we still use `strings.xml` or hardcode values directly in the `@Composable` functions.

### 2.1 API Key in strings.xml
Add this to `res/values/strings.xml`:
```xml
<string name="api_key">AIzaSyB-SecretKey-Compose-99</string>
```

Accessing it in a Composable:
```kotlin
@Composable
fun SecretDisplay() {
    val apiKey = stringResource(id = R.string.api_key)
    Text(text = "API Key: $apiKey")
}
```

### 2.2 Hardcoded Token in Code
```kotlin
class MainActivity : ComponentActivity() {
    private val adminToken = "compose-exclusive-secret-2024"
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            RETargetAppTheme {
                MainScreen()
            }
        }
    }
}
```

---

## 3. Logic Bypass Challenges (Compose UI)
Reverse engineers will try to find where these states are checked and modify the logic.

### 3.1 Premium Feature Toggle
```kotlin
@Composable
fun PremiumScreen() {
    var isPremium by remember { mutableStateOf(checkPremiumStatus()) }

    Column {
        if (isPremium) {
            Text("Welcome to the Secret Premium Area!")
        } else {
            Button(onClick = { /* Logic to buy */ }) {
                Text("Upgrade to Premium")
            }
        }
    }
}

// Challenge: Hook this function with Frida or modify Smali to return true
fun checkPremiumStatus(): Boolean {
    return false 
}
```

### 3.2 Login Screen Bypass
```kotlin
@Composable
fun LoginScreen(onLoginSuccess: () -> Unit) {
    var password by remember { mutableStateOf("") }

    Column {
        TextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Enter Admin Password") }
        )
        Button(onClick = {
            // Challenge: Find this hardcoded string in the DEX or bypass the IF
            if (password == "compose_rules_123") {
                onLoginSuccess()
            }
        }) {
            Text("Login")
        }
    }
}
```

---

## 4. Insecure Data Storage
Even in modern apps, data is often stored insecurely.

### 4.1 SharedPreferences (Plaintext)
```kotlin
fun saveSecrets(context: Context) {
    val sharedPref = context.getSharedPreferences("UserPrefs", Context.MODE_PRIVATE)
    with (sharedPref.edit()) {
        putString("vault_key", "plaintext_password_is_bad")
        apply()
    }
}
```

---

## 5. Security Controls to Bypass
Mechanisms that attempt to detect the environment or protect the app.

### 5.1 Root Detection (Compose Trigger)
```kotlin
@Composable
fun SecurityCheckScreen() {
    val isRooted = remember { isDeviceRooted() }
    
    if (isRooted) {
        Text("Device is Rooted! App will now close.", color = Color.Red)
        // In a real app, you might trigger a finish() here
    }
}

fun isDeviceRooted(): Boolean {
    val paths = arrayOf("/system/app/Superuser.apk", "/sbin/su", "/system/bin/su")
    return paths.any { File(it).exists() }
}
```

---

## 6. Native Code (JNI) Challenge
Native code remains the same regardless of UI framework.

1. Add C++ support.
2. Create `native-lib.cpp`:
```cpp
#include <jni.h>
#include <string>

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_retarget_MainActivity_stringFromJNI(JNIEnv* env, jobject /* this */) {
    return env->NewStringUTF("NATIVE-SECRET-IN-COMPOSE-APP");
}
```

---

## 7. Enabling Obfuscation
In `build.gradle (Module: app)`:
```gradle
buildTypes {
    release {
        isMinifyEnabled = true
        isShrinkResources = true
        proguardFiles(getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro')
    }
}
```
*Note: R8 is particularly aggressive with Compose, making reverse engineering even more challenging!*

---

## 8. Summary of Tools Needed
1. **jadx-gui**: Decompile DEX (now with Compose metadata).
2. **apktool**: Disassemble to Smali.
3. **frida**: Hook `@Composable` state or standard Kotlin functions.
4. **Layout Inspector**: (In Android Studio) to see the Compose tree.
