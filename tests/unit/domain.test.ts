import { describe, expect, it } from "vitest";
import {
  buildBriefing,
  defaultScenarioConfig,
  scenarioConfigSchema,
} from "@/lib/domain";

describe("domain model", () => {
  it("keeps the default scenario valid", () => {
    expect(scenarioConfigSchema.safeParse(defaultScenarioConfig).success).toBe(true);
  });

  it("builds a briefing with language, goal, and cultural focus", () => {
    const briefing = buildBriefing(defaultScenarioConfig);

    expect(briefing).toContain("Spanish");
    expect(briefing).toContain(defaultScenarioConfig.goal);
    expect(briefing).toContain(defaultScenarioConfig.culturalFocus);
  });
});
