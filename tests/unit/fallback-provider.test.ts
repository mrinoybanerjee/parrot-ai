import { describe, expect, it } from "vitest";
import { defaultScenarioConfig, languageOptions, tutorTurnResponseSchema } from "@/lib/domain";
import { createFallbackTurn } from "@/lib/tutor/fallback-provider";

describe("createFallbackTurn", () => {
  it("returns a valid structured tutor response", () => {
    const response = createFallbackTurn(defaultScenarioConfig, "Tengo alergias.");

    expect(tutorTurnResponseSchema.safeParse(response).success).toBe(true);
    expect(response.provider).toBe("fallback");
    expect(response.phraseBankAdditions.length).toBeGreaterThan(0);
  });

  it("returns valid fallback turns for every target language", () => {
    for (const language of languageOptions) {
      const response = createFallbackTurn(
        { ...defaultScenarioConfig, language },
        "I need help with this.",
      );

      expect(tutorTurnResponseSchema.safeParse(response).success).toBe(true);
      expect(response.partnerMessage.length).toBeGreaterThan(0);
      expect(response.phraseBankAdditions).toHaveLength(2);
    }
  });

  it("uses Devanagari text for Hindi fallback practice", () => {
    const response = createFallbackTurn(
      { ...defaultScenarioConfig, language: "Hindi", nativeLanguage: "Hindi" },
      "मुझे एलर्जी है।",
    );

    expect(response.partnerMessage).toMatch(/[\u0900-\u097F]/);
    expect(response.coachFeedback.summary).toMatch(/[\u0900-\u097F]/);
    expect(response.coachFeedback.repairedPhrase).toMatch(/[\u0900-\u097F]/);
    expect(response.culturalNote).toMatch(/[\u0900-\u097F]/);
    expect(response.phraseBankAdditions.join(" ")).toMatch(/[\u0900-\u097F]/);
  });
});
