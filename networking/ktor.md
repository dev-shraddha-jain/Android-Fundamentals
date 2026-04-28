# Ktor — Android Networking (Expert Level)

Ktor is JetBrains' multiplatform HTTP client written in pure Kotlin. Unlike Retrofit, it uses coroutines natively and works across Android, iOS, Desktop, and Server (KMP).

---

## 1. Ktor Client Setup

**Definition:** Ktor's `HttpClient` is configured with installable **plugins** (previously called "features"). Each capability (serialization, logging, auth) is installed as a plugin.

**When to use:** Kotlin Multiplatform Mobile (KMM) projects, or when you want full coroutine-first HTTP without code generation.

**Example Code:**
```kotlin
val client = HttpClient(OkHttp) {            // OkHttp engine for Android
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
    install(Logging) {
        logger = Logger.ANDROID
        level = LogLevel.BODY                // Only in Debug
    }
    install(HttpTimeout) {
        requestTimeoutMillis = 30_000
        connectTimeoutMillis = 15_000
    }
    install(HttpRequestRetry) {
        retryOnServerErrors(maxRetries = 3)
        exponentialDelay()
    }
}
```

---

## 2. Making Requests

**Definition:** Ktor uses typed extension functions (`get`, `post`, `put`, `delete`) that are all `suspend` — no callbacks, no `enqueue`, just coroutines.

**When to use:** Any API call in a coroutine scope.

**Example Code:**
```kotlin
// Data class (must be @Serializable)
@Serializable
data class User(val id: Int, val name: String)

// GET request
val user: User = client.get("https://api.example.com/users/1").body()

// POST with JSON body
val created: User = client.post("https://api.example.com/users") {
    contentType(ContentType.Application.Json)
    setBody(User(id = 0, name = "Alice"))
}.body()

// With query params
val users: List<User> = client.get("https://api.example.com/users") {
    parameter("page", 1)
    parameter("size", 20)
}.body()
```

---

## 3. Auth Plugin (Bearer Token)

**Definition:** The `Auth` plugin handles adding tokens to requests and can automatically refresh tokens on 401 responses — similar to OkHttp's `Authenticator`.

**When to use:** Any app with JWT / OAuth2 authentication.

**Example Code:**
```kotlin
val client = HttpClient(OkHttp) {
    install(Auth) {
        bearer {
            loadTokens {
                BearerTokens(
                    accessToken = prefs.getAccessToken(),
                    refreshToken = prefs.getRefreshToken()
                )
            }
            refreshTokens {
                // Called automatically on 401
                val newTokens = client.post("https://api.example.com/auth/refresh") {
                    setBody(RefreshRequest(oldTokens?.refreshToken ?: ""))
                }.body<TokenResponse>()
                prefs.saveTokens(newTokens)
                BearerTokens(newTokens.accessToken, newTokens.refreshToken)
            }
        }
    }
}
```

---

## 4. Error Handling

**Definition:** Ktor throws `ResponseException` for non-2xx responses (when `HttpResponseValidator` or `expectSuccess = true`). Wrap calls in `try/catch` or a safe wrapper.

**When to use:** Every Ktor API call in production.

**Example Code:**
```kotlin
// Install response validator globally
val client = HttpClient(OkHttp) {
    HttpResponseValidator {
        handleResponseExceptionWithRequest { exception, _ ->
            val clientException = exception as? ClientRequestException ?: return@handleResponseExceptionWithRequest
            if (clientException.response.status == HttpStatusCode.Unauthorized) {
                throw UnauthorizedException()
            }
        }
    }
}

// Safe call wrapper
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}

suspend inline fun <reified T> safeKtorCall(crossinline call: suspend () -> T): Result<T> {
    return try {
        Result.Success(call())
    } catch (e: ClientRequestException) {
        Result.Error("HTTP ${e.response.status.value}: ${e.message}")
    } catch (e: IOException) {
        Result.Error("Network error: ${e.message}")
    }
}

// Usage
val result = safeKtorCall { client.get<User>("https://api.example.com/user/1").body() }
```

---

## 5. WebSockets

**Definition:** Ktor has first-class coroutine-based WebSocket support. The `webSocket` block is a coroutine with incoming/outgoing `Channel`s.

**When to use:** Real-time chat, live data feeds, collaborative features.

**Example Code:**
```kotlin
val client = HttpClient(OkHttp) {
    install(WebSockets)
}

// Connect and listen
client.webSocket("wss://chat.example.com/ws") {
    // Send a message
    send(Frame.Text("""{"type":"join","room":"general"}"""))

    // Listen for incoming frames
    for (frame in incoming) {
        when (frame) {
            is Frame.Text -> {
                val message = frame.readText()
                println("📩 $message")
            }
            is Frame.Close -> break
            else -> {}
        }
    }
}
```

---

## 6. Multipart / File Upload

**Definition:** Sending files or images to a server using multipart/form-data encoding.

**When to use:** Avatar upload, document submission, photo sharing features.

**Example Code:**
```kotlin
suspend fun uploadImage(imageBytes: ByteArray, fileName: String) {
    client.submitFormWithBinaryData(
        url = "https://api.example.com/upload",
        formData = formData {
            append("description", "Profile photo")
            append("image", imageBytes, Headers.build {
                append(HttpHeaders.ContentType, "image/jpeg")
                append(HttpHeaders.ContentDisposition, "filename=$fileName")
            })
        }
    )
}
```

---

## 7. Ktor vs Retrofit — When to Choose

| Aspect | Retrofit | Ktor |
|---|---|---|
| **Platform** | Android only | KMP (Android, iOS, Desktop, Server) |
| **API style** | Interface + annotations | Builder DSL + `suspend` functions |
| **Coroutine support** | Via adapter (native in v2.9+) | Native from the ground up |
| **Plugin system** | OkHttp interceptors | Ktor plugins (`install {}`) |
| **Code generation** | Yes (annotation processor) | No |
| **Learning curve** | Low (familiar to Android devs) | Medium |
| **Best for** | Android-only apps | KMM projects sharing networking code |

### Choose **Retrofit** when:
- Android-only project
- Team familiar with Retrofit
- Need mature ecosystem (Moshi, Gson, RxJava adapters)

### Choose **Ktor** when:
- Kotlin Multiplatform project (shared networking between Android & iOS)
- Want a fully coroutine-native client with no adapters
- Building a Ktor server-side app (same library, familiar API)

---

## 🎯 Quick Reference

| Feature | Ktor Plugin / API |
|---|---|
| JSON serialization | `install(ContentNegotiation) { json() }` |
| Logging | `install(Logging)` |
| Timeout | `install(HttpTimeout)` |
| Retry | `install(HttpRequestRetry)` |
| Bearer auth + refresh | `install(Auth) { bearer { } }` |
| WebSockets | `install(WebSockets)` + `client.webSocket {}` |
| File upload | `client.submitFormWithBinaryData()` |
