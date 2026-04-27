# Content Provider Example (Android Interview)

## What is Content Provider?

- Component used to **share structured data** between apps.
- Provides CRUD operations:
  - Create
  - Read
  - Update
  - Delete

- Accessed using `ContentResolver`.

---

## Real Examples of Content Providers

### 1. Contacts Provider

Used to read phone contacts.

```text
content://contacts/people
```

Use cases:

- Contact picker
- Messaging apps
- Dialer apps

### 2. MediaStore Provider

Used for images, videos, audio files.

```text
content://media/external/images/media
```

Use cases:

- Gallery apps
- Upload image apps
- Camera apps

### 3. SMS Provider (restricted/private on newer Android)

Used earlier for messages.

### 4. Calendar Provider

Access calendar events.

---

## Example Code: Read Contacts

```kotlin id="t7m6px"
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null, null, null, null
)
```

---

## Custom Content Provider Example

Suppose your app shares employee data.

```text
content://com.company.app.provider/employees
```

Other authorized apps can query employee records.


---

## Interview Short Answer

- A common example is **Contacts Provider**, where apps read user contacts using `ContentResolver`.
- Another example is **MediaStore**, used to access images/videos from device storage.

---

## Security Point

- Provider should use:
  - `android:exported`
  - read/write permissions
  - URI permissions

---

## Senior-Level Statement

Content Providers are ideal when structured data must be shared securely across apps with standardized URI-based access.
