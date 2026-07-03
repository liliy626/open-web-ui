# Open WebUI Campus Development Rules

These rules apply to this Open WebUI campus platform fork.

## Ponytail Full

Before writing or modifying Open WebUI, FastAPI, or Svelte code, climb this ladder:

1. Does this feature really need to exist?
2. Can the existing codebase owner handle it? Check CodeGraph first.
3. Can Python stdlib or native JS/TS solve it?
4. Can browser-native features or CSS solve it?
5. Can an already-installed dependency solve it?
6. Can a small patch solve it?

Only then add the minimum new code that works.

Do not create speculative abstractions, duplicate tenant systems, or rewrite whole files when a small patch is enough. Never cut trust-boundary validation, input validation, security, error handling, or accessibility.

If a simplification is intentional, add a short comment above it:

```text
// ponytail: [reason]
```

## Campus Boundaries

- Reuse Open WebUI `groups`, `group_member`, `access_grant`, and `user.info` for school/organization context.
- Do not add a parallel campus tenant model unless the existing Open WebUI model is proven insufficient.
- Keep RAGFlow as the campus knowledge backend.
- Keep FastGPT as an external flow/agent/plugin backend, not the mobile H5 shell.
- Keep `/apps` provider-driven through `entry_url` and `display_mode`; avoid provider-specific branching in Svelte.
