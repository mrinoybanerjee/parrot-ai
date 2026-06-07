# Parrot-AI product and design spec

Date: 2026-06-07
Branch: overhaul/conversation-learning-app
Mode: gstack office-hours builder mode, auto-decided

## Problem statement

Language learning does not stick when the user only studies words and grammar.
The product should force application: realistic back-and-forth conversation,
cultural context, correction, repetition, and reflection.

The app should feel less like a quiz app and more like a private conversation
gym: the user enters a situation, speaks in the target language, gets pushed to
repair mistakes, and leaves with a concrete memory of what they can now say.

## Product thesis

Duolingo optimizes for low-friction habit loops. Parrot-AI should optimize for
high-transfer practice: the user should become more capable in real-world
conversations after each session.

The core loop:

1. Choose or generate a scenario.
2. Read a short cultural briefing.
3. Speak to an AI counterpart.
4. Get immediate lightweight coaching.
5. Repair weak turns.
6. Finish with a debrief, phrase bank, and next drill.

## Premises

1. Conversation is the primary learning object, not a decorative output.
2. Push-to-talk is acceptable for the first high-quality web version.
3. Browser speech is good enough for a free beta if the UI detects unsupported
   browsers and provides typed fallback.
4. The app must work without paid keys, but paid providers should be pluggable.
5. Local LLMs should be supported, but not treated as the only production path.
6. Cultural context has to be generated and shown before the conversation,
   then reinforced during feedback.

## Approaches considered

### Approach A: Minimal web rewrite

Summary: Replace Streamlit with a standalone React/Next.js app, use browser
speech, and call the old FastAPI backend.

Effort: M
Risk: Medium

Pros:
- Fastest path from current repo.
- Reuses some existing Python code.
- Low dependency churn.

Cons:
- Keeps split app/backend complexity.
- Existing backend global state is not production-safe.
- Old prompt model is not rich enough for the desired experience.

### Approach B: Production web foundation (recommended)

Summary: Build a new Next.js app with typed domain models, provider adapters,
browser speech baseline, deterministic fallback, and room for cloud/local
providers.

Effort: L
Risk: Medium

Pros:
- Removes Streamlit completely from the active path.
- Keeps one deployable web app for MVP.
- Makes local and cloud providers swappable.
- Allows proper UI testing and browser QA.

Cons:
- Rewrites more code.
- The first implementation will not include every paid provider.
- Auth/database still need a second phase.

### Approach C: Full voice-agent backend

Summary: Build real-time STT/TTS/LLM orchestration with WebSockets, turn
detection, VAD, provider streaming, and persisted user profiles.

Effort: XL
Risk: High

Pros:
- Best long-term voice UX.
- Can support interruptions and natural live conversation.
- Strongest production voice-agent architecture.

Cons:
- Too much infrastructure before we know the exact learning loop.
- Requires paid services or local sidecars to feel good.
- More failure modes before the product surface is proven.

Recommendation: Approach B. It moves decisively away from Streamlit, ships a
real app surface, and avoids overcommitting to expensive voice infrastructure
before the learning loop is tested.

## Experience principles

- Speak first: text input is fallback, not the main experience.
- Context first: every scenario starts with social/cultural setup.
- Repair beats scoring: feedback should get the user to try again, not just
  grade them.
- Make progress visible: show stronger phrases, corrected turns, and next
  challenge.
- Keep the interface calm: language practice is cognitively heavy; avoid noisy
  decoration and gamified clutter.

## Information architecture

```
App shell
  Header
    Product name
    Provider/status indicator
    Session controls

  Main workspace
    Left rail: Scenario Studio
      Language
      Proficiency
      Scenario
      Conversation goal
      Cultural lens
      Intensity

    Center: Live Conversation
      Cultural briefing
      Dialogue timeline
      Push-to-talk / typed fallback
      Tutor nudge after each turn

    Right rail: Learning Coach
      Session objective
      Active corrections
      Useful phrases
      Confidence/progress

  Debrief view
    What you handled well
    What to repair
    Phrase bank
    Next drills
```

## Core screens

### Scenario Studio

The user configures:
- Target language.
- Native language.
- Proficiency.
- Situation.
- AI counterpart role.
- User role.
- Conversation goal.
- Cultural focus.
- Challenge level.

Default examples:
- Spanish, intermediate, asking a pharmacist about allergy medicine.
- French, beginner, ordering at a bakery without switching to English.
- German, advanced, negotiating an apartment viewing time.
- Hindi, intermediate, visiting a family friend and handling politeness.

### Live Conversation

Visible hierarchy:
1. What situation am I in?
2. What is my objective?
3. What did the AI say?
4. How do I respond?
5. What should I repair?

The screen must support:
- Listening state.
- Speaking state.
- Thinking state.
- Error state.
- Typed fallback.
- Replay AI voice.
- "Give me a hint" without ending the attempt.
- "Repair this turn" after feedback.

### Debrief

The debrief should not be a generic summary. It should produce:
- Three strongest phrases the user used or should use.
- Three corrected turns.
- Cultural notes tied to the scenario.
- Next scenario recommendation.
- A small review deck saved locally.

## Interaction state table

| Feature | Loading | Empty | Error | Success | Partial |
|---|---|---|---|---|---|
| Provider status | Checking model/provider | Fallback mode | Provider unavailable | Connected | Connected but no speech |
| Scenario generation | Drafting briefing | Default scenario shown | Use manual defaults | Briefing ready | Some fields missing |
| Mic capture | Listening pulse | Typed fallback | Browser unsupported | Transcript captured | Interim transcript |
| AI turn | Thinking indicator | Starter prompt available | Retry/fallback turn | AI message shown | Message without audio |
| TTS | Preparing voice | Text-only | Voice unavailable | Audio spoken | Voice changed |
| Feedback | Analyzing turn | No user turn yet | Show simple heuristic | Correction shown | Low confidence feedback |
| Debrief | Building review | No session yet | Retry summary | Debrief saved | Partial phrase bank |

## User journey

```
Step | User does | User should feel | Design support
--- | --- | --- | ---
1 | Opens app | Oriented, not sold to | Workspace first, no landing page
2 | Chooses scenario | In control | Compact scenario controls
3 | Reads briefing | Situated | Clear cultural note before speaking
4 | Speaks first turn | Challenged but safe | Push-to-talk, typed fallback
5 | Gets response | In a real exchange | Timeline, replay, concise AI turns
6 | Gets correction | Coached, not judged | Repair-focused feedback
7 | Finishes | Progress is concrete | Debrief and saved phrase bank
```

## AI behavior spec

The AI must:
- Stay in the selected role.
- Keep responses appropriate to proficiency.
- Avoid solving the user's turn for them.
- Add cultural realism without long lectures.
- Ask follow-up questions that force a response.
- Track session objective and escalate difficulty gradually.
- Provide feedback in the user's native language unless configured otherwise.

The AI must not:
- Produce long monologues.
- Translate every line automatically during live practice.
- Overcorrect every mistake.
- Switch languages unless the scenario or feedback mode requires it.
- Pretend the user spoke correctly when transcript is empty or unclear.

## Design direction

Use a calm productivity-app style, not a marketing hero and not a childish game.

Visual constraints:
- No card grids as the first impression.
- No purple/blue gradient theme.
- No emoji-based controls.
- Use icons for actions.
- Keep cards for actual repeated content: messages, correction items, phrase
  bank entries.
- Dense, readable controls.
- Text must never overlap controls on mobile or desktop.
- Use visible labels for form fields.

Palette:
- Warm white background.
- Ink text.
- Jade accent for success/listening.
- Amber for coaching/repair.
- Slate for structure.

## Success criteria

For the first production foundation:
- User can run app without API keys.
- User can complete a session using text fallback.
- Browser speech works when supported.
- User receives cultural briefing, AI turns, feedback, and debrief.
- Local session state persists.
- Tests cover core prompt/domain logic and UI flows.
- Playwright verifies the main route and a complete typed conversation.

For production readiness later:
- Auth and persisted profiles.
- Cloud STT/TTS adapters.
- Pronunciation scoring.
- LLM quality evals across target languages.
- Deployment with secrets and monitoring.

## Not in scope for first implementation

- Payment/subscriptions.
- User auth.
- Database persistence.
- Cloud speech API implementation.
- Full duplex real-time voice agent.
- Mobile native app.
- CEFR-certified assessment.
- True pronunciation scoring.

## Manual tasks expected later

1. Choose which paid provider keys to enable:
   - Deepgram for STT/TTS.
   - OpenAI for LLM/TTS/transcription.
   - ElevenLabs only if premium TTS is required.
2. Install a local chat model if local mode should be used:
   - Example: `ollama pull qwen3:8b` or a newer multilingual chat model.
3. Choose hosting:
   - Vercel for the Next.js app.
   - Render/Fly/Railway only if a Python/sidecar service is added.
4. Choose persistence:
   - Supabase/Postgres is the most direct next step.
