# Parrot-AI overhaul research: voice, LLM, and cost stack

Date: 2026-06-07
Branch: overhaul/conversation-learning-app

## Goal

Build a conversation-first language learning app where the user learns by
speaking, repairing mistakes, replaying culturally realistic situations, and
reviewing what they struggled with.

Primary constraint: keep the default experience free or very cheap, but do not
let cheapness degrade the core loop. The app should support local-first
providers and cloud upgrades through the same interface.

## Current recommendation

Use a provider-pluggable architecture:

1. Browser/local baseline:
   - STT: Web Speech API when available.
   - TTS: SpeechSynthesis when available.
   - LLM: Ollama OpenAI-compatible adapter when a local chat model is installed.
   - Fallback: deterministic scripted tutor for demos/tests when no model exists.
2. Cloud production upgrade:
   - STT: Deepgram Flux/Nova-3 for low-latency multilingual conversation, or
     AssemblyAI Universal-Streaming for a cheaper real-time path.
   - TTS: browser SpeechSynthesis for beta, Deepgram Aura for lower-cost cloud
     voice, OpenAI gpt-4o-mini-tts for simple developer integration, ElevenLabs
     only for premium voice quality.
   - LLM: OpenAI-compatible adapter, with OpenAI/Anthropic/etc. as optional
     hosted providers and Ollama for local.

This lets us launch a good local beta without keys, then add API keys only where
quality or browser compatibility requires it.

## Source-backed notes

### Browser speech baseline

MDN describes the Web Speech API as having two parts: SpeechSynthesis for TTS
and SpeechRecognition for asynchronous speech recognition:
https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

Important caveat: MDN says recognition can use a platform service by default or
local browser recognition if supported. This is free from the app's perspective,
but not guaranteed to be fully offline or consistent across browsers.

SpeechSynthesis is widely available and can retrieve available device voices:
https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis

Use this for the first free baseline. Production UI must detect support and
show a cloud/provider setup path when recognition is unavailable.

### Deepgram

Official pricing page:
https://deepgram.com/pricing

Relevant facts:
- Pay-as-you-go has a free credit and no minimums.
- Flux is positioned for real-time voice agents with turn detection,
  interruption handling, and low latency.
- Nova-3 is the recommended high-performing STT model for noisy/multilingual
  cases.
- Streaming pay-as-you-go rates listed:
  - Flux English: about $0.0065/min.
  - Flux Multilingual: about $0.0078/min.
  - Nova-3 Monolingual: about $0.0048/min.
  - Nova-3 Multilingual: about $0.0058/min.
- Aura TTS listed:
  - Aura-2: $0.030/1k characters.
  - Aura-1: $0.015/1k characters.

Product implication: Deepgram is the best first paid STT adapter because it is
designed for conversational latency and supports turn-taking concerns that this
app cares about.

### AssemblyAI

Official pricing page:
https://www.assemblyai.com/pricing/

Relevant facts:
- Pre-recorded Universal-2: $0.15/hr and supports 99 languages.
- Universal-3 Pro pre-recorded: $0.21/hr, currently narrower language support.
- Realtime Universal-Streaming: $0.15/hr.
- Realtime Universal-3 Pro Streaming: $0.45/hr.
- Realtime multilingual streaming supports English, Spanish, German, French,
  Portuguese, and Italian at $0.15/hr.

Product implication: AssemblyAI is attractive for cost, especially English and
common European languages. Deepgram is still the stronger first paid voice-agent
fit because of Flux and explicit turn-taking posture.

### OpenAI audio

Official model docs:
- Transcription: https://developers.openai.com/api/docs/models/gpt-4o-transcribe
- TTS: https://developers.openai.com/api/docs/models/gpt-4o-mini-tts

Relevant facts:
- GPT-4o Transcribe model page lists audio input pricing by 1M tokens and
  compares it with GPT-4o mini Transcribe.
- GPT-4o mini TTS lists text input and audio output token pricing.

Product implication: OpenAI is useful for simple provider integration because
the app can use one OpenAI-compatible stack for LLM and audio. It may be less
cost-transparent for a beginner project than per-hour STT and per-character TTS.

### Google Cloud speech

Official pricing:
- STT: https://cloud.google.com/speech-to-text/pricing
- TTS: https://cloud.google.com/text-to-speech/pricing

Relevant facts:
- Google STT dynamic batch recognition lists $0.003/min for standard models.
- Standard models include default, command_and_search, latest_short,
  latest_long, phone_call, video, and chirp.
- Google Chirp 3 HD TTS lists 1M free characters then $30/1M characters.

Product implication: Google is useful for broad language support and mature
cloud infrastructure, but the first implementation should avoid Google setup
complexity unless a target language needs it.

### Azure speech

Official pricing:
https://azure.microsoft.com/en-us/pricing/details/speech/

Relevant facts:
- Azure exposes unified speech-to-text, text-to-speech, and translation pricing.
- TTS billing is per character.
- Free/container pricing paths exist, but public page pricing is region and
  account dependent in places.

Product implication: Azure is enterprise-capable and language-rich, but too
heavy for the first indie rebuild unless deployment is already on Azure.

### Local ASR

whisper.cpp:
https://github.com/ggml-org/whisper.cpp

Relevant facts:
- High-performance C/C++ implementation of OpenAI Whisper.
- Supports Apple Silicon optimizations, Metal, Core ML, CPU-only inference,
  Vulkan, NVIDIA GPU, and WebAssembly.
- Model memory ranges from tiny (~273 MB) to large (~3.9 GB).

faster-whisper:
https://github.com/SYSTRAN/faster-whisper

Relevant facts:
- Benchmarks show major speedups versus original Whisper, especially with
  batching and int8 quantization.
- Best suited for a Python sidecar service rather than browser-only app.

Silero VAD:
https://github.com/snakers4/silero-vad

Relevant facts:
- Lightweight voice activity detector.
- One 30 ms audio chunk can process in less than 1 ms on a single CPU thread.
- MIT licensed and useful for turn detection.

Product implication: local ASR is good enough for desktop users with modern
hardware, but browser integration is non-trivial. For the first production web
foundation, Web Speech API is the local/free path; whisper.cpp/faster-whisper
becomes a future optional local sidecar.

### Local TTS

Piper:
https://github.com/rhasspy/piper

Relevant facts:
- Fast, local neural TTS system.
- Good CPU/edge candidate.

Product implication: local TTS is viable for an offline sidecar, but browser
SpeechSynthesis is easier and already cross-device. Piper or Kokoro should be a
future optional local service, not a first dependency.

### Local LLMs

Ollama:
- Docs: https://docs.ollama.com/index
- OpenAI compatibility: https://docs.ollama.com/api/openai-compatibility

Relevant facts:
- Ollama supports local models such as Gemma, Qwen, DeepSeek, and others.
- Ollama exposes partial OpenAI API compatibility.
- Local machine currently has Ollama installed, but only embedding models are
  installed, not a chat model.

Gemma 3:
https://ai.google.dev/gemma/docs/core/model_card_3

Relevant facts:
- Open-weight model family from Google.
- Multimodal text/image input and text output.
- 128K context and multilingual support in over 140 languages.

Product implication: local models are good enough for a strong beta if the user
installs a capable chat model. They may not be reliable enough as the only
production path for cultural nuance, correction accuracy, and safety. Build the
app so local is first-class but cloud LLMs can be enabled without UI changes.

## Provider decision matrix

| Layer | Free/local beta | Best first paid path | Premium path | Notes |
|---|---|---|---|---|
| STT | Web Speech API | Deepgram Flux/Nova-3 | Google/Azure for specific languages | Browser support is the beta risk. |
| TTS | SpeechSynthesis | Deepgram Aura or OpenAI mini TTS | ElevenLabs | ElevenLabs should be premium-only due cost. |
| LLM | Ollama OpenAI-compatible | OpenAI-compatible hosted model | Best frontier model available | Use structured JSON and evals for quality. |
| Turn detection | Browser push-to-talk | Deepgram Flux / Silero VAD sidecar | Voice-agent API | Push-to-talk is simplest and reliable. |
| Persistence | localStorage | Supabase/Postgres | Managed Postgres + auth | Start local, design DB schema now. |

## Local model answer

Local models can be good enough for:
- Scenario generation.
- Basic role-play.
- Vocabulary extraction.
- Simple grammar correction.
- Private/offline practice.

Local models are risky for:
- Accurate cultural nuance across many languages.
- Fine-grained pronunciation coaching.
- Multi-turn pedagogy that adapts over weeks.
- Safety and prompt-injection resistance.
- Consistent structured JSON under small model constraints.

Decision: implement local-first and provider-pluggable. Do not hardcode local as
the only production path.

## First implementation scope

Build the standalone web app with:
- Scenario studio.
- Live conversation practice.
- Browser mic capture through Web Speech API.
- Browser TTS through SpeechSynthesis.
- LLM provider abstraction:
  - deterministic fallback for tests/demo,
  - Ollama/OpenAI-compatible endpoint when configured.
- Cultural briefing before each scenario.
- Tutor feedback after each user turn.
- Session debrief with corrections, phrases, and next drills.
- Local progress persistence.

Defer:
- User auth and cloud DB.
- Paid STT/TTS adapters.
- Pronunciation scoring.
- Whisper/faster-whisper sidecar.
- Mobile app packaging.
