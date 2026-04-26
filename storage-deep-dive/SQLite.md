# SQLite & Room (Structured Storage)

## Definition
SQLite is the built-in, lightweight relational database engine in Android. **Room** is the modern Jetpack library that provides an abstraction layer over SQLite to allow for more robust database access while leveraging the full power of SQLite.

---

## 🛠️ SQLite vs. Room
| SQLite | Room |
| :--- | :--- |
| Manual SQL queries (error-prone). | Compile-time SQL validation. |
| No object mapping (requires Cursor). | Automatic object mapping (Entities). |
| Manual schema migrations. | Built-in migration support. |
| Synchronous (often leads to UI lag). | Supports Coroutines/Flow out of the box. |

## 🔍 Internal Process: How Room Works
Room uses **Annotation Processing**. When you compile:
1.  It checks your `@Entity` and `@Dao`.
2.  It generates the implementation code for your DAO.
3.  It validates that the SQL query is correct for the schema.

---

## 🎯 Interview-Ready Answer (Senior)

**Q: How do you handle database migrations in Room?**

**Answer:**
> You define a `Migration` object that specifies the `startVersion` and `endVersion` and includes the SQL `ALTER TABLE` commands. You then pass this migration to the Room database builder. If you forget to provide a migration after changing the schema, Room will throw an `IllegalStateException` unless `fallbackToDestructiveMigration()` is called (which clears the data—don't use in production!).
