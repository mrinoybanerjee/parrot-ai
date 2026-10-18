# Runtime validation — October 18, 2026

This is a bounded setup and integration check, not a language-quality benchmark.
No model was downloaded, no audio service was called, and no device permission was used.

## Setup

- Base commit: `f29f995`, plus the model-name/native-rendering fixes in this change.
- Apple M4, 16 GiB RAM, macOS 26.6.2, arm64; Python 3.12.12.
- A new temporary virtual environment installed the test/runtime requirements
  entirely from cached wheels, with network and source builds disabled.
- The final clean environment does not contain `streamlit-chat`.
- Streamlit 1.66.0, OpenAI client 3.35.1. Exact installed versions are in
  [the environment receipt](runtime-environment-20261018.txt).

Equivalent commands, using an existing Python 3.12 interpreter and populated wheel cache:

```sh
python3.12 -m venv /tmp/parrot-runtime-check
uv pip install --offline --only-binary :all: --python /tmp/parrot-runtime-check/bin/python -r tests/requirements.txt
/tmp/parrot-runtime-check/bin/python -m pytest --cov=backend --cov=frontend --cov-report=term-missing
```

An empty cache requires normal package installation from the README. The optional
legacy evaluation dependencies and model downloads are not part of this setup.

## Real local-model flow

The existing Ollama installation had `qwen3:4b` (2.5 GB on disk, Q4_K_M).
Its digest was `359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7`.
Ollama ran at `127.0.0.1:11434`; no remote API was used.

The original hardcoded `LLaMA_CPP` identifier returned HTTP 404/model not found.
With `LLM_MODEL=qwen3:4b`, the actual browser → Streamlit → FastAPI → OpenAI SDK
→ Ollama path completed four English conversation pairs and one learning summary.
Reset, all four generation requests and summary each returned HTTP 200.
Settings: English, Beginner, Conversation, Short. Synthetic scenario:
“order one apple; each character replies with one short sentence; /no_think”.

The old custom chat iframe timed out despite local HTML/JS assets returning 200.
The native chat renderer displayed all eight messages. The English display toggle
and learning-points expander worked. No online audio button was pressed.
The model was unloaded after completion to serialize the Vani inference check.

## Automated rendering and state checks

The complete Streamlit app test uses fixed synthetic HTTP responses. It checks
all eight native messages, translation display, one stable session ID, summary,
and preservation of the original conversation labels when draft settings change.
The settings regression fails against the original code and passes with the fix.
This complements the mocked API/helper tests; it does not replace browser checks.

Final local suite: 27 passed, 90% overall coverage. The app entrypoint is now exercised.

## Quality failure and remaining limits

The real generated summary incorrectly implied that “an apple” is invalid and
that the uncontracted “you are welcome” is a mistake. Those are not reliable
teaching rules. This single synthetic English case establishes integration only.
Human review of grammar, translation, role adherence and proficiency fit remains
necessary. No learner outcomes or multilingual quality were measured.

The English toggle displayed the application's prefixed English text; it was not
an independent translation-quality check. No real TTS or speech-quality check ran.
Docker was installed but its daemon was unavailable. CI image builds do not
establish container runtime behavior. The application remains an in-memory,
one-worker local prototype with the documented legacy shared no-header session.
