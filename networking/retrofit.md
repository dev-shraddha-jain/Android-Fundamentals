# Retrofit — Android Networking (Expert Level)

Retrofit is a type-safe HTTP client for Android built on top of OkHttp. It turns your REST API into a Kotlin interface.

---

## 1. OkHttp

**Definition:** OkHttp is the HTTP engine that powers Retrofit. It handles connection pooling, request/response caching, GZIP compression, and retries. Retrofit uses it as its `Call.Factory`.

**When to use:** You rarely use OkHttp directly — configure it via `OkHttpClient.Builder` and pass it to `Retrofit.Builder`. Use it directly only for raw HTTP calls without REST abstraction (e.g., file downloads).

**Example Code:**
```kotlin
val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .addInterceptor(loggingInterceptor)
    .build()

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)          // inject configured OkHttpClient
    .addConverterFactory(GsonConverterFactory.create())
    .build()
```

---

## 2. Interceptors

**Definition:** Interceptors are middleware for OkHttp. They can observe, modify, or short-circuit requests/responses. Two types:
- **Application interceptors** (`addInterceptor`) — run once, before caching
- **Network interceptors** (`addNetworkInterceptor`) — run every time, after caching (sees redirects)

**When to use:** Adding auth headers, logging, caching custom headers, response mutation, or analytics.

**Example Code:**
```kotlin
// Auth header interceptor
val authInterceptor = Interceptor { chain ->
    val original = chain.request()
    val request = original.newBuilder()
        .header("Authorization", "Bearer ${tokenManager.getToken()}")
        .build()
    chain.proceed(request)
}

// Logging interceptor
val logging = HttpLoggingInterceptor().apply {
    level = HttpLoggingInterceptor.Level.BODY  // Only in DEBUG builds
}

val client = OkHttpClient.Builder()
    .addInterceptor(authInterceptor)
    .addInterceptor(logging)
    .build()
```

---

## 3. Auth Token Refresh (Authenticator)

**Definition:** When an API returns `401 Unauthorized`, OkHttp's `Authenticator` intercepts the response and can silently refresh the token, then retry the original request — transparent to the caller.

**When to use:** Any app with JWT / OAuth2 tokens that expire. Do NOT use a regular interceptor for this — use `Authenticator` to handle 401 specifically.

**Example Code:**
```kotlin
class TokenAuthenticator(
    private val tokenApi: TokenApi,
    private val prefs: SecurePrefs
) : Authenticator {

    override fun authenticate(route: Route?, response: Response): Request? {
        // Avoid infinite loop if refresh itself fails
        if (response.code == 401 && response.request.header("X-Retry") != null) return null

        // Synchronized to prevent concurrent refresh storms
        return synchronized(this) {
            val newToken = runBlocking { tokenApi.refreshToken(prefs.getRefreshToken()) }
            prefs.saveToken(newToken.accessToken)

            response.request.newBuilder()
                .header("Authorization", "Bearer ${newToken.accessToken}")
                .header("X-Retry", "true")   // prevent re-retrying
                .build()
        }
    }
}

val client = OkHttpClient.Builder()
    .authenticator(TokenAuthenticator(tokenApi, prefs))
    .build()
```

---

## 4. SSL Pinning

**Definition:** SSL Pinning validates that the server's certificate matches a known public key or certificate hash — preventing man-in-the-middle attacks even if the device's CA store is compromised.

**When to use:** Banking, healthcare, fintech apps, or any app handling PII. Required by many security standards (OWASP MASVS).

**Example Code:**
```kotlin
val certificatePinner = CertificatePinner.Builder()
    // Get the SHA256 hash from: openssl s_client -connect api.example.com:443
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .add("api.example.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=") // backup pin
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()

// ⚠️ Always include a backup pin and a pin rotation plan before shipping
```

---

## 5. Retry Mechanism

**Definition:** Automatically re-attempt failed requests (network errors, 5xx responses) with optional exponential backoff. OkHttp has built-in retry for connection failures; for custom retry logic use an interceptor.

**When to use:** Flaky mobile networks, idempotent GET requests, or any non-destructive operation where retrying is safe.

**Example Code:**
```kotlin
class RetryInterceptor(private val maxRetries: Int = 3) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        var response: Response? = null
        var attempt = 0

        while (attempt < maxRetries) {
            try {
                response = chain.proceed(request)
                if (response.isSuccessful) return response
            } catch (e: IOException) {
                // Network error — retry
            }
            attempt++
            Thread.sleep(1000L * attempt) // exponential backoff: 1s, 2s, 3s
        }
        return response ?: chain.proceed(request)
    }
}

val client = OkHttpClient.Builder()
    .addInterceptor(RetryInterceptor(maxRetries = 3))
    .build()
```

---

## 6. Pagination

**Definition:** Loading data in chunks (pages) to avoid loading thousands of records at once. Use Jetpack Paging 3 with Retrofit for automatic scroll-triggered loading.

**When to use:** News feeds, product lists, search results, chat history — any list with potentially unbounded data.

**Example Code:**
```kotlin
// Retrofit API
interface ArticleApi {
    @GET("articles")
    suspend fun getArticles(
        @Query("page") page: Int,
        @Query("size") size: Int = 20
    ): List<Article>
}

// PagingSource
class ArticlePagingSource(private val api: ArticleApi) : PagingSource<Int, Article>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Article> {
        val page = params.key ?: 1
        return try {
            val articles = api.getArticles(page, params.loadSize)
            LoadResult.Page(
                data = articles,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (articles.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }
    override fun getRefreshKey(state: PagingState<Int, Article>) = state.anchorPosition
}

// ViewModel
val articles = Pager(PagingConfig(pageSize = 20)) {
    ArticlePagingSource(api)
}.flow.cachedIn(viewModelScope)
```

---

## 7. Error Handling

**Definition:** Wrapping Retrofit calls in a `Result` or sealed class to handle HTTP errors, network failures, and serialization errors gracefully without crashing.

**When to use:** Every production Retrofit call. Never let raw exceptions reach the UI layer.

**Example Code:**
```kotlin
// Sealed result wrapper
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
    data class NetworkError(val exception: IOException) : ApiResult<Nothing>()
}

// Safe API call wrapper
suspend fun <T> safeApiCall(call: suspend () -> Response<T>): ApiResult<T> {
    return try {
        val response = call()
        if (response.isSuccessful) {
            ApiResult.Success(response.body()!!)
        } else {
            val error = response.errorBody()?.string() ?: "Unknown error"
            ApiResult.Error(response.code(), error)
        }
    } catch (e: IOException) {
        ApiResult.NetworkError(e)
    }
}

// Usage in Repository
suspend fun fetchUser(id: String): ApiResult<User> = safeApiCall {
    api.getUser(id)  // returns Response<User>
}

// ViewModel
viewModelScope.launch {
    when (val result = repo.fetchUser("42")) {
        is ApiResult.Success      -> _state.value = UiState.Success(result.data)
        is ApiResult.Error        -> _state.value = UiState.Error("HTTP ${result.code}: ${result.message}")
        is ApiResult.NetworkError -> _state.value = UiState.Error("No internet connection")
    }
}
```

---

## 8. WebSockets Basics

**Definition:** WebSockets provide a persistent, full-duplex communication channel over TCP. Unlike HTTP (request/response), the server can push data at any time. OkHttp has native WebSocket support.

**When to use:** Real-time features — chat, live scores, stock tickers, collaborative editing, live notifications.

**Example Code:**
```kotlin
class ChatWebSocket(private val client: OkHttpClient) {

    private var webSocket: WebSocket? = null

    // Listener for events
    private val listener = object : WebSocketListener() {
        override fun onOpen(ws: WebSocket, response: Response) {
            println("✅ Connected")
        }
        override fun onMessage(ws: WebSocket, text: String) {
            println("📩 Message: $text")
            // Parse JSON and emit to Flow / StateFlow
        }
        override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
            println("❌ Error: ${t.message}")
            reconnect()  // implement reconnect with backoff
        }
        override fun onClosed(ws: WebSocket, code: Int, reason: String) {
            println("🔒 Closed: $reason")
        }
    }

    fun connect() {
        val request = Request.Builder()
            .url("wss://chat.example.com/ws")
            .header("Authorization", "Bearer $token")
            .build()
        webSocket = client.newWebSocket(request, listener)
    }

    fun sendMessage(json: String) = webSocket?.send(json)

    fun disconnect() = webSocket?.close(1000, "User left")

    private fun reconnect() {
        // Implement exponential backoff reconnect
    }
}
```

---

## 🎯 Quick Reference

| Topic | Key Class / API | Use Case |
|---|---|---|
| OkHttp | `OkHttpClient.Builder` | Base HTTP engine configuration |
| Interceptor | `Interceptor` | Auth headers, logging, mutation |
| Token Refresh | `Authenticator` | Silent 401 → refresh → retry |
| SSL Pinning | `CertificatePinner` | MITM prevention in sensitive apps |
| Retry | Custom `Interceptor` | Flaky network resilience |
| Pagination | `PagingSource` + Paging 3 | Infinite scroll lists |
| Error Handling | `sealed class ApiResult` | Safe, typed error propagation |
| WebSocket | `WebSocketListener` | Real-time bidirectional data |