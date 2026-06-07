import { z } from "zod";

export const languageSchema = z.enum([
  "English",
  "Spanish",
  "French",
  "German",
  "Hindi",
  "Japanese",
  "Korean",
  "Portuguese",
  "Italian",
  "Arabic",
]);

export const proficiencySchema = z.enum(["Beginner", "Intermediate", "Advanced"]);
export const practiceModeSchema = z.enum(["Conversation", "Debate"]);
export const intensitySchema = z.enum(["Gentle", "Focused", "Stretch"]);

export const scenarioConfigSchema = z.object({
  language: languageSchema,
  nativeLanguage: languageSchema,
  proficiency: proficiencySchema,
  mode: practiceModeSchema,
  scenario: z.string().trim().min(4).max(280),
  userRole: z.string().trim().min(2).max(80),
  partnerRole: z.string().trim().min(2).max(80),
  goal: z.string().trim().min(4).max(220),
  culturalFocus: z.string().trim().min(4).max(220),
  intensity: intensitySchema,
});

export const messageSchema = z.object({
  id: z.string().min(1),
  speaker: z.enum(["user", "partner", "coach"]),
  content: z.string().min(1).max(1800),
  createdAt: z.string().min(1),
});

export const coachFeedbackSchema = z.object({
  summary: z.string().min(1).max(700),
  correction: z.string().min(1).max(700),
  repairedPhrase: z.string().min(1).max(360),
  encouragement: z.string().min(1).max(360),
});

export const sessionScoreSchema = z.object({
  clarity: z.number().min(0).max(100),
  culturalFit: z.number().min(0).max(100),
  momentum: z.number().min(0).max(100),
});

export const tutorTurnResponseSchema = z.object({
  partnerMessage: z.string().min(1).max(1200),
  coachFeedback: coachFeedbackSchema,
  culturalNote: z.string().min(1).max(500),
  phraseBankAdditions: z.array(z.string().min(1).max(180)).max(6),
  sessionScore: sessionScoreSchema,
  provider: z.string().min(1),
  warning: z.string().optional(),
});

export const tutorTurnRequestSchema = z.object({
  config: scenarioConfigSchema,
  messages: z.array(messageSchema).max(18),
  userInput: z.string().trim().min(1).max(1200),
});

export type Language = z.infer<typeof languageSchema>;
export type Proficiency = z.infer<typeof proficiencySchema>;
export type PracticeMode = z.infer<typeof practiceModeSchema>;
export type Intensity = z.infer<typeof intensitySchema>;
export type ScenarioConfig = z.infer<typeof scenarioConfigSchema>;
export type ConversationMessage = z.infer<typeof messageSchema>;
export type CoachFeedback = z.infer<typeof coachFeedbackSchema>;
export type SessionScore = z.infer<typeof sessionScoreSchema>;
export type TutorTurnRequest = z.infer<typeof tutorTurnRequestSchema>;
export type TutorTurnResponse = z.infer<typeof tutorTurnResponseSchema>;

export const languageOptions: Language[] = [
  "Spanish",
  "French",
  "German",
  "Hindi",
  "Japanese",
  "Korean",
  "Portuguese",
  "Italian",
  "Arabic",
  "English",
];

export const languageCodes: Record<Language, string> = {
  English: "en-US",
  Spanish: "es-ES",
  French: "fr-FR",
  German: "de-DE",
  Hindi: "hi-IN",
  Japanese: "ja-JP",
  Korean: "ko-KR",
  Portuguese: "pt-BR",
  Italian: "it-IT",
  Arabic: "ar-SA",
};

export const defaultScenarioConfig: ScenarioConfig = {
  language: "Spanish",
  nativeLanguage: "English",
  proficiency: "Intermediate",
  mode: "Conversation",
  scenario: "You are at a neighborhood pharmacy asking about allergy medicine.",
  userRole: "Customer with seasonal allergies",
  partnerRole: "Pharmacist",
  goal: "Explain symptoms, ask for a recommendation, and confirm dosage politely.",
  culturalFocus: "Use polite requests, brief context, and a natural closing.",
  intensity: "Focused",
};

export function createMessage(
  speaker: ConversationMessage["speaker"],
  content: string,
): ConversationMessage {
  return {
    id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
    speaker,
    content,
    createdAt: new Date().toISOString(),
  };
}

export function buildBriefing(config: ScenarioConfig): string {
  const tone =
    config.intensity === "Gentle"
      ? "Keep the pressure low and give the learner extra room."
      : config.intensity === "Stretch"
        ? "Increase the pressure with follow-up questions and mild ambiguity."
        : "Keep the exchange natural and focused.";

  return `${config.language} ${config.proficiency.toLowerCase()} practice: ${config.scenario} Your role is ${config.userRole}; the counterpart is ${config.partnerRole}. Goal: ${config.goal} Cultural focus: ${config.culturalFocus} ${tone}`;
}
