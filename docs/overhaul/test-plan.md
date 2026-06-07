# Parrot-AI overhaul test plan

Date: 2026-06-07
Branch: overhaul/conversation-learning-app

## Affected pages and routes

- `/` - main language practice workspace.
- `/api/tutor/turn` - structured tutor/partner response endpoint.

## Critical paths

1. User opens the app.
2. App shows scenario controls, provider status, conversation workspace, and
   coach panel.
3. User edits scenario settings.
4. User submits a typed response.
5. API returns a partner message, coaching feedback, cultural note, phrase bank
   additions, and score.
6. UI appends the user message and AI response.
7. Feedback appears in the coach panel.
8. Phrase bank persists locally.
9. User can replay AI speech if SpeechSynthesis is available.

## Unit coverage

| Area | Required tests |
|---|---|
| Domain defaults | Default scenario config has valid language/proficiency/roles |
| Prompt builder | Includes scenario, target language, proficiency, recent history |
| Fallback provider | Produces structured response for empty and non-empty turns |
| Response parser | Parses JSON, extracts JSON from text, falls back on malformed text |
| Validation | Rejects missing/too-long fields |
| Local state | Adds messages, phrase bank, and feedback without mutation bugs |

## Integration coverage

| Route | Case | Expected |
|---|---|---|
| `/api/tutor/turn` | Valid payload, fallback provider | 200 structured response |
| `/api/tutor/turn` | Empty user input | 400 validation error |
| `/api/tutor/turn` | Provider unavailable | 200 fallback response with warning |
| `/api/tutor/turn` | Long transcript | 400 validation error |

## E2E coverage

| Flow | Assertions |
|---|---|
| App smoke | Main controls and conversation workspace visible |
| Typed conversation | Send turn, see user message, AI message, coach feedback |
| Scenario editing | Changing language/scenario updates briefing context |
| Debrief/phrase bank | Phrase bank item appears after turn |
| Responsive | Mobile viewport does not overlap controls |

## QA focus

- No text overlap at desktop or mobile widths.
- Mic unsupported state is clear and does not block typed practice.
- Buttons have stable dimensions.
- Provider status is visible.
- User can practice without reading instructions.
- AI output is displayed as text, never HTML.

## Eval cases

Initial eval cases for future LLM quality tests:

1. Spanish beginner, restaurant order:
   - Partner uses Spanish only.
   - Feedback is short and in English.
   - Correction is beginner-friendly.
2. German intermediate, apartment viewing:
   - Partner asks a follow-up question.
   - Cultural note mentions formality or punctuality.
3. Hindi intermediate, family visit:
   - Feedback handles politeness/register.
   - Does not over-literalize cultural behavior.
4. French advanced, work disagreement:
   - Uses advanced vocabulary.
   - Feedback focuses on nuance and tone.

## Manual QA after implementation

1. Run `npm run dev`.
2. Open `http://localhost:3000`.
3. Complete one typed session.
4. Try microphone if browser supports speech recognition.
5. Try replay voice.
6. Resize to mobile width.
7. Run Playwright.
