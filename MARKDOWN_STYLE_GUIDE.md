# 📝 Markdown Style Guide

This guide ensures your documentation looks premium and well-aligned in the browser. Follow these patterns to maintain a clean academic layout.

## 1. Lists & Indentation
Always use **2 spaces** for nesting. Our CSS is optimized to step bullets correctly at this level.

- Parent level
  - Second level (2 spaces)
    - Third level (2 spaces more)

> [!TIP]
> Use `-` for bullets instead of `*` for better consistency in the source files.

## 2. Vertical Spacing
To prevent "unwanted spacing" while keeping the hierarchy clear:

- **Tight Spacing**: Use exactly one blank line between a paragraph and a list.
- **Section Gaps**: Use two blank lines before a major `##` or `###` heading.

## 3. Task Lists
You can now create interactive-looking checklists:
- [x] Correct indentation
- [x] Muted pastel colors
- [ ] Add more Android internals

## 4. Code Blocks
Use triple backticks with the language name for syntax highlighting.

```kotlin
// Example Kotlin block
fun startApp() {
    println("Zygote forked!")
}
```

## 5. Admonitions (Blockquotes)
Use blockquotes for "Interview Gold" or "Core Ideas".

> **Core Idea:** Everything in Android is a process. Security is enforced at the Kernel level via UID sandboxing.
