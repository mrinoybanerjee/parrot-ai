import { describe, expect, it } from "vitest";
import { defaultScenarioConfig } from "@/lib/domain";
import { parseProviderResponse } from "@/lib/tutor/response-parser";

describe("parseProviderResponse", () => {
  it("parses valid JSON", () => {
    const response = parseProviderResponse(
      JSON.stringify({
        partnerMessage: "Claro, puedo ayudarle.",
        coachFeedback: {
          summary: "Good.",
          correction: "Add one detail.",
          repairedPhrase: "Tengo alergias desde ayer.",
          encouragement: "Keep going.",
        },
        culturalNote: "Polite requests fit this setting.",
        phraseBankAdditions: ["Tengo alergias desde ayer."],
        sessionScore: {
          clarity: 80,
          culturalFit: 75,
          momentum: 78,
        },
      }),
      defaultScenarioConfig,
      "Tengo alergias.",
      "test",
    );

    expect(response.provider).toBe("test");
    expect(response.partnerMessage).toContain("Claro");
  });

  it("falls back on malformed JSON", () => {
    const response = parseProviderResponse(
      "not json",
      defaultScenarioConfig,
      "Tengo alergias.",
      "test",
    );

    expect(response.provider).toBe("fallback");
    expect(response.warning).toContain("non-JSON");
  });
});
