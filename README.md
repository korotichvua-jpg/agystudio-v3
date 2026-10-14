# AgyStudio v3 вљЎ

A high-performance local engineering canvas and telemetry studio powered by the `agy` agent CLI engine, featuring an **Intelligent Cognitive Model Router** and zero-reload dynamic workspace architectures.

## What's New in v3 (Major Version Increment)

- **вљЎ Intelligent Cognitive Model Router:** Dynamically analyzes prompt semantics, code AST structures, and mathematical proofs to autonomously route tasks to the optimal tier:
  - **Tier 1 (Fast & Minimal Quota):** `gemini-3.8-flash-low` for quick syntax, regex, git commands, and lookup.
  - **Tier 2 (Balanced Code Engine):** `gemini-3.8-flash-high` / `claude-sonnet-4-6` for multi-step feature development.
  - **Tier 3 (Deep Cognitive Reasoning):** `claude-opus-4-6-thinking` for formal proofs, complex architecture, and security audits.
- **рџ“Љ Real-Time Pre-Flight Economics Estimator:** Debounced prompt evaluator that previews the routed model, estimated input tokens, expected TTFT (time-to-first-token), and quota tier *before* dispatching.
- **рџ§  Continuous Thinking Budget Controls:** Granular cognitive effort controls with custom token budgets (`2k`, `8k`, `16k`, `32k`, `64k`) for thinking models.
- **рџ–јпёЏ Zero-Reload In-Page Layout Lab:** Instantly switch between Split Canvas, Model Arena, Inspector Dock, and Masonry Grid without page reloads.
- **рџ”Њ Offline-First Resilience:** 100% self-contained vendor libraries (`static/vendor/`) with defensive guards, ensuring uninterrupted offline local operation.
- **рџ›ЎпёЏ Hardened Podman D: Sandbox:** Rootless container execution and isolated storage on `D:\agystudio_secure_env` with canary verification.
- **рџљЂ Port Isolation:** Runs isolated on port **`8130`** (`http://127.0.0.1:8130`).

## Running Locally

Activate the isolated virtual environment and run uvicorn:

```bash
# Using the dedicated virtual environment
D:\projects\agystudio-v3\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8130 --reload
```

Open `http://127.0.0.1:8130` in your browser.

## Testing Suite

Run the full automated Playwright test suite:

```bash
pytest tests/test_studio_e2e.py -v
```
