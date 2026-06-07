# Parrot-AI

Parrot-AI is a conversation-first language learning app. The overhaul moves the project from a Streamlit proof of concept to a production-oriented Next.js app focused on live speaking practice, scenario simulation, cultural context, and repair-based coaching.

The core product idea is simple: the learner should practice by applying the language in realistic conversations, not by only memorizing isolated phrases.

## Current App

- Scenario Studio for configuring language, level, role, goal, intensity, and cultural focus.
- Conversation Workspace with typed input, browser speech recognition when available, and speech playback.
- Learning Coach with corrections, repaired phrases, phrase bank additions, and session scores.
- Provider-pluggable tutor backend with a deterministic fallback provider and optional local Ollama-compatible chat model support.
- Unit, integration, and Playwright browser tests for the new web app.

The old Streamlit/FastAPI files are still in the repository as legacy reference code. The active app path is the Next.js app at the repo root.

## Tech Stack

- Next.js 16 App Router
- React 19
- TypeScript 6
- Zod for request and response validation
- Browser Web Speech APIs for free speech recognition and playback where supported
- Optional Ollama-compatible local LLM provider
- Vitest and Testing Library
- Playwright

## Quick Start

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

The app works without paid API keys by using the deterministic fallback tutor. For a better local AI experience, install a chat model in Ollama and run:

```bash
ollama pull qwen3:8b
OLLAMA_MODEL=qwen3:8b npm run dev
```

Optional environment variables:

```bash
TUTOR_PROVIDER=fallback
TUTOR_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

When `TUTOR_PROVIDER` is not set, the app attempts Ollama if an Ollama model is configured and falls back cleanly if the local model is unavailable or returns malformed output.

## Testing

```bash
npm run typecheck
npm test
npm run build
npm run e2e
```

Playwright starts the local Next.js dev server automatically for browser tests.

## Production Readiness

This branch is ready for a first production-style deployment of the web app, with these boundaries:

- The app has request validation, structured tutor responses, basic per-instance API rate limiting, security headers, browser E2E coverage, and a health endpoint at `/api/health`.
- The default tutor is deterministic demo mode, so the app works without paid API keys.
- Browser speech uses the user's browser capabilities and can vary by device, browser, and language.
- Stronger production controls still need external services: hosted rate limiting, auth, analytics, persistent user accounts, and a managed AI/voice provider for high-quality real-time speech.

## Planning Docs

The overhaul planning docs live in `docs/overhaul/`:

- `research-voice-llm-stack.md`
- `product-design-spec.md`
- `engineering-plan.md`
- `test-plan.md`

These capture the provider research, product direction, implementation architecture, and verification strategy for the production app.

## Product Direction

Parrot-AI should become an application-based language tutor:

- The user enters or selects a real-world scenario.
- The app plays a believable conversation partner.
- The tutor pushes the learner to respond in the target language.
- Feedback is short, concrete, and immediately reusable.
- Cultural context is part of every exchange, not an afterthought.

The default operating mode should stay cheap and private-friendly. Paid providers can be added behind adapters when quality, latency, or production reliability requires them.

## Legacy App

The original project used:

- Streamlit frontend
- FastAPI backend
- Docker Compose
- Local llamafile model experiments

Those files remain for reference while the Next.js app becomes the main product surface.
