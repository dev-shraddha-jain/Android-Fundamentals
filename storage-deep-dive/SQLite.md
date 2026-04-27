# SQLite & Room (Structured Storage)

### Definition
SQLite is the built-in, lightweight relational database engine in Android. **Room** is the modern Jetpack library that provides an abstraction layer over SQLite to allow for more robust database access while leveraging the full power of SQLite.


# 🛠️ Traditional SQLite Methods
If you are not using Room, you interact with SQLite using these core classes and methods:

### 1. SQLiteOpenHelper (Lifecycle)
Manage database creation and version management.
- `onCreate(db: SQLiteDatabase)`: Called when the database is created for the first time. Used to create tables.
- `onUpgrade(db: SQLiteDatabase, old: Int, new: Int)`: Called when the version changes. Used to `DROP` or `ALTER` tables.

### 2. SQLiteDatabase (Operations)
The main class for interacting with data.
- **`insert(table, nullColumnHack, values)`**: Convenience method to add a row.
- **`query(table, columns, selection, selectionArgs, ...)`**: Powerful method to search and filter data. Returns a `Cursor`.
- **`update(table, values, whereClause, whereArgs)`**: Modifies existing data.
- **`delete(table, whereClause, whereArgs)`**: Removes data.
- **`execSQL(sql)`**: Run a single SQL statement that is NOT a `SELECT` (e.g., `CREATE TABLE`).
- **`rawQuery(sql, selectionArgs)`**: Runs a manual SQL `SELECT` and returns a `Cursor`.

### 3. ContentValues (Data Preparation)
Used to store a set of key-value pairs for `insert` and `update`.
- `put(key, value)`: Adds a value to the set.

### 4. Cursor (Reading Results)
Think of this as a pointer to the result set.
- `moveToFirst()`: Moves to the first row of results.
- `getColumnIndex(name)`: Gets the index of a column by name.
- `getString(index)` / `getInt(index)`: Extracts data from the current row.
- `close()`: **Crucial!** Always close to prevent memory leaks.


# 🔍 Internal Process: How Room Works
Room uses **Annotation Processing**. When you compile:
1.  It checks your `@Entity` and `@Dao`.
2.  It generates the implementation code for your DAO.
3.  It validates that the SQL query is correct for the schema.

## 🔄 Room Lifecycle Callbacks
While SQLite uses `SQLiteOpenHelper`, Room uses a `RoomDatabase.Callback` to listen for database events.

### 1. `onCreate(db: SupportSQLiteDatabase)`
- Called when the database is created for the **first time**.
- **Common Use Case:** Pre-populating the database with initial data (e.g., a list of countries or default settings).

### 2. `onOpen(db: SupportSQLiteDatabase)`
- Called every time the database is **opened**.
- **Common Use Case:** Performing cleanup or checking for specific states before the app starts using the DB.

### 3. `onUpgrade`? (The Room Way)
Room does **not** use an `onUpgrade` method like traditional SQLite. Instead, it uses **Migrations**:
- You create `Migration` objects (e.g., `Migration(1, 2)`).
- Each migration contains the specific SQL to transform the schema from the old version to the new version.
- These are added to the database builder using `.addMigrations()`.


# Room + SQLCipher (Database Encryption)
Standard Room/SQLite databases are stored in plain text. To secure them:
*   **SQLCipher** is the industry standard for 256-bit AES encryption of SQLite files.
*   **Pairing with Room:** You provide a `SupportFactory` from the SQLCipher library to the Room database builder.
*   **Methods:**
    *   `SafeHelperFactory`: Used to provide the passphrase to the database.
    *   `Room.databaseBuilder(...).openHelperFactory(factory).build()`.


# 🛠️ SQLite vs. Room

| SQLite | Room |
| :--- | :--- |
| Manual SQL queries (error-prone). | Compile-time SQL validation. |
| No object mapping (requires Cursor). | Automatic object mapping (Entities). |
| Manual schema migrations. | Built-in migration support. |
| Synchronous (often leads to UI lag). | Supports Coroutines/Flow out of the box. |


For securing db, refer to [securingDb.md](securingDb.md).

## 🎯 Interview-Ready Answer (Senior)


**Q: How do you handle database migrations in Room?**

**Answer:**
> You define a `Migration` object that specifies the `startVersion` and `endVersion` and includes the SQL `ALTER TABLE` commands. You then pass this migration to the Room database builder. If you forget to provide a migration after changing the schema, Room will throw an `IllegalStateException` unless `fallbackToDestructiveMigration()` is called (which clears the data—don't use in production!).
