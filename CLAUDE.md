# Claude Code Rules

## Project

- Follow existing code style and patterns in this repo.
- Prefer small, focused changes; avoid unnecessary refactors.
- Keep new code consistent with the project's structure and conventions.
- When adding dependencies, use the project's existing package manager and lockfiles.
- **Web lookup**: Use web search and fetch tools whenever needed to look up docs, APIs, or current information. Do not ask for permission first—proceed with the lookup.

## Documentation

Applies to: `**/*.adoc`, `**/*.md`

### Format

- **Use AsciiDoc (`.adoc`)** unless the project or the user explicitly specifies another format.
- Prefer AsciiDoc for new docs when no format is mandated.
- **Use Markdown (`.md`)** for README.md only.

### File naming and language

- **English**: use the `_en.adoc` suffix. Example: `getting-started_en.adoc`
- **Japanese**: use the `_ja.adoc` suffix. Example: `getting-started_ja.adoc`
- For a single-language doc, still use the appropriate suffix so language is clear.

### URLs and spacing

- When a URL immediately follows a non-ASCII character (e.g. Japanese text), insert a half-width space before the URL.
  - Avoid: `詳細はhttps://example.com/を参照。`
  - Prefer: `詳細は https://example.com/ を参照。`

### AsciiDoc formatting

- Put one blank line before the first item of a list when it follows paragraph text or other non-list content.

### Diagrams

- Use PlantUML for text-based diagrams.
- Use PNG format for image files.

### Math and special characters

Use plain ASCII only for math signs. Do not use Unicode math symbols.

| Instead of  | Use        | Example            |
|-------------|------------|--------------------|
| × (U+00D7)  | `x` or `*` | `2x H100`, `a * b` |
| − (U+2212)  | `-`        | `80 - 14`          |
| – (U+2013)  | `-`        | `latency - 10`     |
| ≈ (U+2248)  | `~=`       | `latency ~= 100ms` |
| ▼           | `v`        | ASCII art arrows   |
| √x (U+221A) | `sqrt(x)`  | `sqrt(d_k)`        |
