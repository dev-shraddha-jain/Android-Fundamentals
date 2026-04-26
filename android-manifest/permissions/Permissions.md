# Permissions

## Definition
The mechanism that protects user privacy by restricting access to sensitive data and device features.

## 🛡️ Types of Permissions

1.  **Normal:** Automatically granted (e.g., Internet).
2.  **Dangerous:** Requires user approval at runtime (e.g., Camera).
3.  **Signature:** Granted only if apps share the same certificate.
4.  **Special:** Requires explicit user authorization in system settings (e.g., Draw over other apps).

## 🔍 Real-World Process: Runtime Request

```text
  [ App needs Camera ]
          ↓
  [ Check Permission ]
      ↙          ↘
 [ GRANTED ]   [ DENIED ]
     ↓             ↓
 [ Use Camera ] [ requestPermissions() ]
                   ↓
              [ System Dialog ]
                   ↓
              [ User Choice ]
              ↙           ↘
          [ ALLOW ]      [ DENY ]
              ↓              ↓
       [ Success Flow ]  [ Handle Error ]
```

## 🎯 Interview-Ready Answer

**Q: What is a "Special" permission?**

**Answer:**
> These are permissions that cover particularly sensitive actions, like `SYSTEM_ALERT_WINDOW` or `WRITE_SETTINGS`. They cannot be granted via a simple popup; the app must send the user to a specific page in the system Settings to manually toggle the permission.

---

**Q: What is a "Signature" permission?**

**Answer:**
> It is a permission that the system grants only if the app requesting it is signed with the same developer certificate as the app that defined the permission. This is used for secure communication between apps from the same developer.
