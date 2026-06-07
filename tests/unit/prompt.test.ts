import { describe, expect, it } from "vitest";
import { createMessage, defaultScenarioConfig } from "@/lib/domain";
import { buildTutorPrompt } from "@/lib/tutor/prompt";

describe("buildTutorPrompt", () => {
  it("includes scenario context and JSON instructions", () => {
    const prompt = buildTutorPrompt(
      defaultScenarioConfig,
      [createMessage("user", "Tengo alergias.")],
      "Necesito ayuda.",
    );

    expect(prompt).toContain(defaultScenarioConfig.language);
    expect(prompt).toContain(defaultScenarioConfig.partnerRole);
    expect(prompt).toContain("Return only valid JSON");
    expect(prompt).toContain("Necesito ayuda.");
  });
});
