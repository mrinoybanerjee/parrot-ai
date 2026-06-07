import {
  tutorTurnResponseSchema,
  type ScenarioConfig,
  type TutorTurnResponse,
} from "@/lib/domain";
import { createFallbackTurn } from "@/lib/tutor/fallback-provider";

export function parseProviderResponse(
  rawText: string,
  config: ScenarioConfig,
  userInput: string,
  provider: string,
): TutorTurnResponse {
  const parsed = tryParseJson(rawText);
  if (!parsed) {
    return createFallbackTurn(
      config,
      userInput,
      `${provider} returned non-JSON output; fallback response used.`,
    );
  }

  const candidate = {
    ...parsed,
    provider,
  };
  const result = tutorTurnResponseSchema.safeParse(candidate);
  if (!result.success) {
    return createFallbackTurn(
      config,
      userInput,
      `${provider} returned an invalid response shape; fallback response used.`,
    );
  }

  return result.data;
}

function tryParseJson(rawText: string): unknown | null {
  const trimmed = rawText.trim();
  const extracted = extractJsonObject(trimmed);
  const candidates = [
    trimmed,
    trimmed.replace(/^```json\s*/i, "").replace(/```$/i, "").trim(),
    ...(extracted ? [extracted] : []),
  ];

  for (const candidate of candidates) {
    try {
      return JSON.parse(candidate);
    } catch {
      continue;
    }
  }

  return null;
}

function extractJsonObject(text: string): string | null {
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start === -1 || end === -1 || end <= start) {
    return null;
  }
  return text.slice(start, end + 1);
}
