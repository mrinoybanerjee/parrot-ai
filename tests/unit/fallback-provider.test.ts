import { describe, expect, it } from "vitest";
import { defaultScenarioConfig, tutorTurnResponseSchema } from "@/lib/domain";
import { createFallbackTurn } from "@/lib/tutor/fallback-provider";

describe("createFallbackTurn", () => {
  it("returns a valid structured tutor response", () => {
    const response = createFallbackTurn(defaultScenarioConfig, "Tengo alergias.");

    expect(tutorTurnResponseSchema.safeParse(response).success).toBe(true);
    expect(response.provider).toBe("fallback");
    expect(response.phraseBankAdditions.length).toBeGreaterThan(0);
  });
});
