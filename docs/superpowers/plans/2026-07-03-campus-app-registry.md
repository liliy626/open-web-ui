# Campus App Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first platform layer for a campus agent application center that can expose Open WebUI native pages, RAGFlow assistants, FastGPT apps, MCP tools, and OpenAPI tool servers through one registry contract.

**Architecture:** Add a focused FastAPI router that returns normalized app cards with `provider_type`, `entry_url`, and `display_mode`. The Svelte `/apps` page consumes that contract and renders provider-agnostic cards without branching on provider-specific names.

**Tech Stack:** FastAPI, Pydantic, Svelte, TypeScript, Tailwind utility classes.

---

### Task 1: Backend Registry Contract

**Files:**

- Create: `backend/open_webui/routers/test_campus_apps.py`
- Create: `backend/open_webui/routers/campus_apps.py`
- Modify: `backend/open_webui/main.py`

- [ ] **Step 1: Write the failing test**

```python
from open_webui.routers.campus_apps import (
    CampusAppDisplayMode,
    CampusAppProviderType,
    get_seed_campus_apps,
)


def test_seed_campus_apps_expose_provider_agnostic_entry_contract():
    apps = get_seed_campus_apps()

    assert {app.provider_type for app in apps} >= {
        CampusAppProviderType.NATIVE_OPENWEBUI,
        CampusAppProviderType.RAGFLOW_ASSISTANT,
        CampusAppProviderType.FASTGPT_APP,
        CampusAppProviderType.MCP_TOOL,
        CampusAppProviderType.OPENAPI_TOOL_SERVER,
    }
    assert all(app.entry_url for app in apps)
    assert all(app.display_mode in set(CampusAppDisplayMode) for app in apps)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=backend pytest backend/open_webui/routers/test_campus_apps.py -q`

Expected: FAIL because `open_webui.routers.campus_apps` does not exist.

- [ ] **Step 3: Implement the router**

Create `campus_apps.py` with Pydantic enums/models, a small seed registry, and `GET /`.

- [ ] **Step 4: Register the router**

Import `campus_apps` in `backend/open_webui/main.py` and include it at `/api/v1/campus/apps`.

- [ ] **Step 5: Verify backend**

Run: `PYTHONPATH=backend pytest backend/open_webui/routers/test_campus_apps.py -q`

Expected: PASS.

### Task 2: Frontend API Contract

**Files:**

- Create: `src/lib/apis/campus/apps.ts`

- [ ] **Step 1: Define TypeScript types**

Expose `CampusAgentApp`, `CampusAppProviderType`, `CampusAppDisplayMode`, and `getCampusApps(token)`.

- [ ] **Step 2: Keep frontend generic**

The API contract should not contain RAGFlow/FastGPT-specific behavior. Provider details belong in backend data.

### Task 3: Dynamic Mobile App Center

**Files:**

- Modify: `src/routes/(app)/apps/+page.svelte`

- [ ] **Step 1: Replace hardcoded cards with registry data**

Load `getCampusApps(localStorage.token)` on mount. Group by category for display.

- [ ] **Step 2: Route by generic display mode**

Use only `display_mode` and `entry_url` to decide `native`, `redirect`, or `iframe` behavior.

- [ ] **Step 3: Preserve mobile shell**

Keep fixed top identity area, scrollable card content, and fixed bottom navigation.

### Task 4: Verification and Upload

**Files:**

- Run focused backend test.
- Run `git diff --check`.
- Run the smallest feasible frontend check for touched TypeScript/Svelte files.
- Commit and push only relevant files; keep local scripts and runtime configs out of Git.
