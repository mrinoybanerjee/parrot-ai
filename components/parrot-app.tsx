"use client";

import {
  Bot,
  CheckCircle2,
  Languages,
  Mic,
  MicOff,
  RefreshCw,
  Send,
  Square,
  Volume2,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { z } from "zod";
import {
  buildBriefing,
  coachFeedbackSchema,
  createMessage,
  defaultScenarioConfig,
  languageOptions,
  messageSchema,
  scenarioConfigSchema,
  sessionScoreSchema,
  type CoachFeedback,
  type ConversationMessage,
  type Intensity,
  type PracticeMode,
  type Proficiency,
  type ScenarioConfig,
  type SessionScore,
  type TutorTurnResponse,
} from "@/lib/domain";
import { useBrowserSpeech } from "@/hooks/use-browser-speech";

type ProviderStatus = {
  provider: string;
  ollamaModel: string | null;
  speech: string;
};

type SavedState = {
  config: ScenarioConfig;
  messages: ConversationMessage[];
  phraseBank: string[];
  lastFeedback: CoachFeedback | null;
  lastScore: SessionScore | null;
  lastCulturalNote: string | null;
};

const storageKey = "parrot-ai-v2-session";

const savedStateSchema = z.object({
  config: scenarioConfigSchema.optional(),
  messages: z.array(messageSchema).max(18).optional(),
  phraseBank: z.array(z.string().min(1).max(180)).max(12).optional(),
  lastFeedback: coachFeedbackSchema.nullable().optional(),
  lastScore: sessionScoreSchema.nullable().optional(),
  lastCulturalNote: z.string().min(1).max(500).nullable().optional(),
});

function formatTutorStatus(status: ProviderStatus | null): string {
  if (!status) {
    return "Tutor: checking";
  }
  if (status.provider === "ollama") {
    return `Tutor: Ollama${status.ollamaModel ? ` (${status.ollamaModel})` : ""}`;
  }
  if (status.provider === "fallback") {
    return "Tutor: demo";
  }
  return "Tutor: unavailable";
}

function tutorStatusTitle(status: ProviderStatus | null): string {
  if (!status) {
    return "Checking which tutor provider is active.";
  }
  if (status.provider === "ollama") {
    return "Using the configured local Ollama chat model.";
  }
  if (status.provider === "fallback") {
    return "Using the built-in demo tutor. No paid AI provider or local chat model is configured.";
  }
  return "Tutor provider status could not be checked.";
}

function speechStatusText(speech: ReturnType<typeof useBrowserSpeech>): string {
  if (speech.isRecognitionSupported) {
    return "Mic: browser";
  }
  if (speech.isSynthesisSupported) {
    return "Audio: playback";
  }
  return "Voice: typed only";
}

export function ParrotApp() {
  const [config, setConfig] = useState<ScenarioConfig>(defaultScenarioConfig);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [lastFeedback, setLastFeedback] = useState<CoachFeedback | null>(null);
  const [lastScore, setLastScore] = useState<SessionScore | null>(null);
  const [lastCulturalNote, setLastCulturalNote] = useState<string | null>(null);
  const [phraseBank, setPhraseBank] = useState<string[]>([]);
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null);
  const [warning, setWarning] = useState<string | null>(null);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(storageKey);
      if (!raw) {
        return;
      }
      const parsed = savedStateSchema.safeParse(JSON.parse(raw));
      if (!parsed.success) {
        window.localStorage.removeItem(storageKey);
        return;
      }

      const saved = parsed.data;
      if (saved.config) {
        setConfig(saved.config);
      }
      if (saved.messages) {
        setMessages(saved.messages);
      }
      if (saved.phraseBank) {
        setPhraseBank(saved.phraseBank);
      }
      if (saved.lastFeedback) {
        setLastFeedback(saved.lastFeedback);
      }
      if (saved.lastScore) {
        setLastScore(saved.lastScore);
      }
      if (saved.lastCulturalNote) {
        setLastCulturalNote(saved.lastCulturalNote);
      }
    } catch {
      window.localStorage.removeItem(storageKey);
    }
  }, []);

  useEffect(() => {
    fetch("/api/tutor/status")
      .then((response) => response.json())
      .then((status: ProviderStatus) => setProviderStatus(status))
      .catch(() => setProviderStatus({ provider: "unknown", ollamaModel: null, speech: "browser" }));
  }, []);

  useEffect(() => {
    const state: SavedState = {
      config,
      messages,
      phraseBank,
      lastFeedback,
      lastScore,
      lastCulturalNote,
    };
    window.localStorage.setItem(storageKey, JSON.stringify(state));
  }, [config, lastCulturalNote, lastFeedback, lastScore, messages, phraseBank]);

  const handleFinalTranscript = useCallback((text: string) => {
    setDraft((current) => `${current}${current ? " " : ""}${text}`.trim());
  }, []);

  const speech = useBrowserSpeech(handleFinalTranscript);
  const briefing = useMemo(() => buildBriefing(config), [config]);

  async function sendTurn() {
    const userInput = draft.trim();
    if (!userInput || isSending) {
      return;
    }

    setIsSending(true);
    setWarning(null);
    const userMessage = createMessage("user", userInput);
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setDraft("");

    try {
      const response = await fetch("/api/tutor/turn", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          config,
          messages,
          userInput,
        }),
      });

      if (!response.ok) {
        throw new Error(`Tutor request failed with ${response.status}`);
      }

      const result = (await response.json()) as TutorTurnResponse;
      const partnerMessage = createMessage("partner", result.partnerMessage);
      const coachMessage = createMessage("coach", result.coachFeedback.summary);
      setMessages([...nextMessages, partnerMessage, coachMessage]);
      setLastFeedback(result.coachFeedback);
      setLastScore(result.sessionScore);
      setLastCulturalNote(result.culturalNote);
      setPhraseBank((current) =>
        Array.from(new Set([...result.phraseBankAdditions, ...current])).slice(0, 12),
      );
      setWarning(result.warning ?? null);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Tutor request failed.";
      setWarning(message);
      setMessages([
        ...nextMessages,
        createMessage("coach", "I could not reach the tutor service. Try again or keep practicing with typed notes."),
      ]);
    } finally {
      setIsSending(false);
    }
  }

  function resetSession() {
    speech.cancelSpeech();
    setMessages([]);
    setDraft("");
    setLastFeedback(null);
    setLastScore(null);
    setLastCulturalNote(null);
    setPhraseBank([]);
    setWarning(null);
  }

  return (
    <main className="app-shell">
      <header className="top-bar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            <Languages size={22} />
          </span>
          <div>
            <h1>Parrot-AI</h1>
            <p>{config.language} practice with cultural context</p>
          </div>
        </div>
        <div className="status-row" aria-label="System status">
          <span
            className={`status-pill ${providerStatus?.provider === "fallback" ? "info" : "good"}`}
            title={tutorStatusTitle(providerStatus)}
          >
            <Bot size={15} />
            {formatTutorStatus(providerStatus)}
          </span>
          <span
            className={`status-pill ${speech.isRecognitionSupported ? "good" : "warn"}`}
            title="Speech uses this browser's built-in speech APIs when available. Typed input always works."
          >
            {speech.isRecognitionSupported ? <Mic size={15} /> : <MicOff size={15} />}
            {speechStatusText(speech)}
          </span>
          <button className="secondary-button" type="button" onClick={resetSession} title="Clear this practice session">
            <RefreshCw size={16} />
            Reset
          </button>
        </div>
      </header>

      <section className="workspace" aria-label="Language practice workspace">
        <ScenarioStudio config={config} onChange={setConfig} />
        <ConversationWorkspace
          briefing={briefing}
          config={config}
          draft={draft}
          isSending={isSending}
          messages={messages}
          speech={speech}
          warning={warning ?? speech.error}
          onDraftChange={setDraft}
          onSend={sendTurn}
        />
        <LearningCoach
          culturalNote={lastCulturalNote}
          feedback={lastFeedback}
          phraseBank={phraseBank}
          score={lastScore}
          warning={warning}
        />
      </section>
    </main>
  );
}

function ScenarioStudio({
  config,
  onChange,
}: {
  config: ScenarioConfig;
  onChange: (config: ScenarioConfig) => void;
}) {
  const update = <K extends keyof ScenarioConfig>(key: K, value: ScenarioConfig[K]) => {
    onChange({ ...config, [key]: value });
  };

  return (
    <aside className="panel">
      <div className="panel-header">
        <div>
          <h2>Scenario Studio</h2>
          <p>{config.userRole} with {config.partnerRole}</p>
        </div>
      </div>
      <div className="panel-body">
        <div className="scenario-form">
          <div className="field-grid">
            <div className="field">
              <label htmlFor="language">Target language</label>
              <select
                id="language"
                value={config.language}
                onChange={(event) => update("language", event.target.value as ScenarioConfig["language"])}
              >
                {languageOptions.map((language) => (
                  <option key={language} value={language}>
                    {language}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="nativeLanguage">Feedback language</label>
              <select
                id="nativeLanguage"
                value={config.nativeLanguage}
                onChange={(event) =>
                  update("nativeLanguage", event.target.value as ScenarioConfig["nativeLanguage"])
                }
              >
                {languageOptions.map((language) => (
                  <option key={language} value={language}>
                    {language}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="field">
            <label>Proficiency</label>
            <div className="segmented" role="group" aria-label="Proficiency">
              {(["Beginner", "Intermediate", "Advanced"] as Proficiency[]).map((level) => (
                <button
                  className={config.proficiency === level ? "active" : ""}
                  key={level}
                  type="button"
                  onClick={() => update("proficiency", level)}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          <div className="field-grid">
            <div className="field">
              <label htmlFor="mode">Mode</label>
              <select
                id="mode"
                value={config.mode}
                onChange={(event) => update("mode", event.target.value as PracticeMode)}
              >
                <option>Conversation</option>
                <option>Debate</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="intensity">Intensity</label>
              <select
                id="intensity"
                value={config.intensity}
                onChange={(event) => update("intensity", event.target.value as Intensity)}
              >
                <option>Gentle</option>
                <option>Focused</option>
                <option>Stretch</option>
              </select>
            </div>
          </div>

          <div className="field">
            <label htmlFor="scenario">Situation</label>
            <textarea
              id="scenario"
              value={config.scenario}
              onChange={(event) => update("scenario", event.target.value)}
            />
          </div>

          <div className="field-grid role-grid">
            <div className="field">
              <label htmlFor="userRole">Your role</label>
              <input
                id="userRole"
                value={config.userRole}
                onChange={(event) => update("userRole", event.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="partnerRole">Counterpart</label>
              <input
                id="partnerRole"
                value={config.partnerRole}
                onChange={(event) => update("partnerRole", event.target.value)}
              />
            </div>
          </div>

          <div className="field">
            <label htmlFor="goal">Conversation goal</label>
            <textarea
              id="goal"
              value={config.goal}
              onChange={(event) => update("goal", event.target.value)}
            />
          </div>

          <div className="field">
            <label htmlFor="culturalFocus">Cultural focus</label>
            <textarea
              id="culturalFocus"
              value={config.culturalFocus}
              onChange={(event) => update("culturalFocus", event.target.value)}
            />
          </div>
        </div>
      </div>
    </aside>
  );
}

function ConversationWorkspace({
  briefing,
  config,
  draft,
  isSending,
  messages,
  speech,
  warning,
  onDraftChange,
  onSend,
}: {
  briefing: string;
  config: ScenarioConfig;
  draft: string;
  isSending: boolean;
  messages: ConversationMessage[];
  speech: ReturnType<typeof useBrowserSpeech>;
  warning: string | null;
  onDraftChange: (value: string) => void;
  onSend: () => void;
}) {
  const lastPartnerMessage = [...messages].reverse().find((message) => message.speaker === "partner");

  return (
    <section className="panel conversation-panel">
      <div className="briefing">
        <h2>{config.partnerRole} in {config.language}</h2>
        <p>{briefing}</p>
      </div>

      <div aria-label="Conversation messages" className="message-list" aria-live="polite">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>Start with the first thing you would actually say in this situation.</p>
          </div>
        ) : (
          messages.map((message) => (
            <article className={`message-card ${message.speaker}`} key={message.id}>
              <div className="message-meta">
                <span>{message.speaker === "user" ? config.userRole : message.speaker === "partner" ? config.partnerRole : "Coach"}</span>
                {message.speaker === "partner" ? (
                  <button
                    aria-label="Replay partner message"
                    className="icon-button"
                    title="Replay partner message"
                    type="button"
                    onClick={() => speech.speak(message.content, config.language)}
                    disabled={!speech.isSynthesisSupported}
                  >
                    <Volume2 size={16} />
                  </button>
                ) : null}
              </div>
              <p>{message.content}</p>
            </article>
          ))
        )}
      </div>

      <div className="composer">
        {warning ? <div className="warning-text">{warning}</div> : null}
        <div className="transcript-preview">
          {speech.isListening
            ? speech.interimTranscript || "Listening..."
            : lastPartnerMessage
              ? `Respond to: ${lastPartnerMessage.content.slice(0, 110)}`
              : "Your first turn sets the tone."}
        </div>
        <div className="composer-row">
          <button
            aria-label={speech.isListening ? "Stop listening" : "Start listening"}
            className={`icon-button ${speech.isListening ? "active" : ""}`}
            title={speech.isListening ? "Stop listening" : "Start listening"}
            type="button"
            disabled={!speech.isRecognitionSupported}
            onClick={() =>
              speech.isListening ? speech.stopListening() : speech.startListening(config.language)
            }
          >
            {speech.isListening ? <Square size={17} /> : <Mic size={17} />}
          </button>
          <textarea
            aria-label="Your response"
            value={draft}
            placeholder="Type your response if speech is unavailable."
            onChange={(event) => onDraftChange(event.target.value)}
            onKeyDown={(event) => {
              if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
                void onSend();
              }
            }}
          />
          <button className="primary-button" type="button" disabled={isSending || !draft.trim()} onClick={onSend}>
            {isSending ? <RefreshCw size={16} /> : <Send size={16} />}
            {isSending ? "Thinking" : "Send"}
          </button>
        </div>
      </div>
    </section>
  );
}

function LearningCoach({
  culturalNote,
  feedback,
  phraseBank,
  score,
  warning,
}: {
  culturalNote: string | null;
  feedback: CoachFeedback | null;
  phraseBank: string[];
  score: SessionScore | null;
  warning: string | null;
}) {
  return (
    <aside className="panel coach-panel">
      <div className="panel-header">
        <div>
          <h3>Learning Coach</h3>
          <p>{feedback ? feedback.encouragement : "Waiting for your first turn"}</p>
        </div>
        <CheckCircle2 size={19} color="var(--jade)" />
      </div>
      <div className="panel-body">
        <div className="coach-stack">
          <div className="metric-grid">
            <Metric label="Clarity" value={score?.clarity ?? 0} />
            <Metric label="Culture" value={score?.culturalFit ?? 0} />
            <Metric label="Momentum" value={score?.momentum ?? 0} />
          </div>

          <div className="coach-card">
            <h4>Repair</h4>
            <p>{feedback?.correction ?? "A correction will appear after your first response."}</p>
          </div>

          <div className="coach-card">
            <h4>Culture note</h4>
            <p>{culturalNote ?? "A cultural note will appear after your first response."}</p>
          </div>

          <div className="coach-card">
            <h4>Try this</h4>
            <p>{feedback?.repairedPhrase ?? "Send a turn to build a phrase you can reuse."}</p>
          </div>

          {warning ? (
            <div className="coach-card">
              <h4>Provider note</h4>
              <p>{warning}</p>
            </div>
          ) : null}

          <section aria-label="Phrase bank" className="phrase-card">
            <h4>Phrase bank</h4>
            <div className="phrase-list">
              {phraseBank.length === 0 ? (
                <p>Reusable phrases will collect here.</p>
              ) : (
                phraseBank.map((phrase) => <p key={phrase}>{phrase}</p>)
              )}
            </div>
          </section>
        </div>
      </div>
    </aside>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
