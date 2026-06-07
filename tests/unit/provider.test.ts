import { afterEach, describe, expect, it, vi } from "vitest";
import { getProviderName } from "@/lib/tutor/provider";

describe("getProviderName", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("uses fallback by default", () => {
    expect(getProviderName()).toBe("fallback");
  });

  it("uses the documented tutor provider env var", () => {
    vi.stubEnv("TUTOR_PROVIDER", "ollama");

    expect(getProviderName()).toBe("ollama");
  });

  it("auto-selects ollama when a local model is configured", () => {
    vi.stubEnv("OLLAMA_MODEL", "qwen3:8b");

    expect(getProviderName()).toBe("ollama");
  });

  it("keeps the legacy provider env var working", () => {
    vi.stubEnv("AI_PROVIDER", "ollama");

    expect(getProviderName()).toBe("ollama");
  });
});
