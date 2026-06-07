# Parrot-AI engineering plan

Date: 2026-06-07
Branch: overhaul/conversation-learning-app

## Recommended stack

- Next.js 16, React 19, TypeScript.
- App Router with server route handlers for AI provider calls.
- Plain CSS modules/global CSS for tight design control.
- Browser Web Speech API for the zero-cost speech baseline.
- OpenAI-compatible provider interface:
  - `fallback` deterministic provider for tests/demo.
  - `ollama` provider for local models.
  - future `openai`, `deepgram`, `assemblyai`, `elevenlabs` adapters.
- Vitest for unit/integration tests.
- Playwright for browser-level E2E.

Why Next.js:
- Single production app instead of Streamlit + FastAPI split.
- Good TypeScript support.
- Server routes can hide API keys.
- Easy Vercel deployment later.
- Current local package ecosystem supports latest Next.js, React, Vitest, and
  Playwright.

## Architecture

```
Browser
  |
  | speech recognition / speech synthesis
  v
Next.js app
  |
  +-- Scenario Studio UI
  +-- Conversation Workspace UI
  +-- Learning Coach UI
  +-- Local persistence
  |
  v
Next.js API route /api/tutor/turn
  |
  +-- request validation
  +-- prompt construction
  +-- provider selection
  +-- structured response parsing
  |
  v
AI provider adapter
  |
  +-- deterministic fallback
  +-- Ollama OpenAI-compatible local model
  +-- future cloud providers
```

## Data model

```
ScenarioConfig
  language
  nativeLanguage
  proficiency
  mode
  scenario
  userRole
  partnerRole
  goal
  culturalFocus
  intensity

Message
  id
  speaker: user | partner | coach
  content
  translation?
  feedback?
  createdAt

TurnRequest
  config
  messages
  userInput
  provider

TurnResponse
  partnerMessage
  coachFeedback
  culturalNote
  phraseBankAdditions
  sessionScore
```

## Provider contract

Provider adapters must return the same structured shape:

```
{
  partnerMessage: string,
  coachFeedback: {
    summary: string,
    correction: string,
    repairedPhrase: string,
    encouragement: string
  },
  culturalNote: string,
  phraseBankAdditions: string[],
  sessionScore: {
    clarity: number,
    culturalFit: number,
    momentum: number
  }
}
```

If a provider returns malformed JSON, the route should:
1. Attempt to extract JSON from text.
2. Fall back to deterministic response.
3. Include a provider warning in the response metadata.

## Error and rescue map

| Codepath | What can go wrong | Handling | User sees |
|---|---|---|---|
| Browser STT | Unsupported browser | Detect support | Typed fallback |
| Browser STT | Permission denied | Catch error | Mic permission guidance |
| Browser TTS | No voices | Detect voices | Text-only/replay disabled |
| `/api/tutor/turn` | Invalid payload | Zod validation | Clear client error |
| Provider call | Timeout | Abort/retry/fallback | Fallback response + warning |
| Provider call | Malformed JSON | Parse recovery/fallback | Session continues |
| Local storage | Parse error | Reset bad state | Fresh local session |
| Debrief | No messages | Disable debrief | Prompt to start session |

## Security review

New attack surfaces:
- Prompt injection through scenario/user messages.
- User-controlled text rendered in message timeline.
- Future API keys for providers.
- Future persisted user data.

Mitigations in first implementation:
- Treat AI output as plain text only.
- Never render HTML from provider/user text.
- Keep provider keys server-side only.
- Validate all API request bodies with Zod.
- Limit transcript/message lengths.
- Use deterministic fallback rather than exposing raw provider failures.

Future production requirements:
- Auth and per-user scoping.
- Rate limits for provider-backed endpoints.
- Abuse detection for prompt injection / unsafe role-play.
- Provider secret rotation.
- Content moderation for public/shared scenarios.

## Prompt design

The prompt should separate:
- System role: language tutor and role-play counterpart.
- Scenario context.
- Conversation rules.
- Output JSON schema.
- Recent message history.
- User latest turn.

Important constraints:
- Keep AI partner message concise.
- Feedback in native language.
- Correction must be actionable.
- Cultural note must be tied to the turn.
- Phrase bank additions should be reusable.

## Test strategy

Unit:
- Scenario defaults.
- Prompt building.
- Fallback provider.
- Provider JSON parsing.
- Local storage reducer/helpers.

Integration:
- `/api/tutor/turn` valid payload.
- `/api/tutor/turn` invalid payload.
- Provider fallback path.

E2E:
- App renders.
- User changes scenario fields.
- User sends typed turn.
- AI response appears.
- Feedback appears.
- Debrief/phrase bank appears.
- Browser speech unsupported state is non-blocking.

Eval:
- Prompt output schema adherence.
- Partner response stays in target language.
- Feedback is repair-focused.
- Cultural note is concrete.

## Implementation phases

### Phase 1: Production web foundation

- Add Next.js app in repo root.
- Keep legacy Streamlit/FastAPI files for history but remove them from active
  scripts.
- Implement typed domain models.
- Implement fallback and Ollama provider adapters.
- Implement full app UI.
- Add tests and Playwright.

### Phase 2: Persistence and provider upgrades

- Add Supabase/Postgres schema.
- Add user auth.
- Add cloud STT/TTS adapters.
- Add server-side rate limiting.

### Phase 3: Voice-agent quality

- Add WebSocket streaming.
- Add VAD/turn detection.
- Add pronunciation scoring.
- Add quality eval suite by language and proficiency.

## Rollback

This branch does not modify production deployment yet. Rollback is git revert or
switching active scripts back to legacy app.

## Deployment path

First deploy target: Vercel.

Implemented env vars for optional providers:

```
TUTOR_PROVIDER=fallback | ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

For production provider integrations later:

```
OPENAI_API_KEY=
OPENAI_MODEL=
DEEPGRAM_API_KEY=
ASSEMBLYAI_API_KEY=
ELEVENLABS_API_KEY=
```

## Existing code leverage

Reuse conceptually:
- Old role/scenario conversation premise.
- Old supported languages list.
- Old local LLM privacy idea.

Do not reuse directly:
- Streamlit UI.
- FastAPI global `dual_chatbot` state.
- gTTS dependency.
- Existing evaluation script, except as historical benchmark.

## Design review summary

Initial design completeness: 8/10 after this plan.

Remaining gaps:
- Exact visual mockups not generated by gstack designer.
- Mobile microphone UX will need real browser QA.
- Provider error copy needs refinement after implementation.

## CEO review summary

Scope mode: selective expansion.

Accepted now:
- Full standalone web app.
- Local-first speech/LLM baseline.
- Cultural briefing and repair feedback.
- Tests and browser QA.

Deferred:
- Cloud paid providers.
- Auth/database.
- Real-time duplex voice.
- Pronunciation scoring.

Rationale: this gives the user a real app to try quickly while preserving the
long-term architecture.
