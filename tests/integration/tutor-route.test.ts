import { beforeEach, describe, expect, it } from "vitest";
import { defaultScenarioConfig, createMessage } from "@/lib/domain";
import { POST } from "@/app/api/tutor/turn/route";
import { resetRateLimitForTests } from "@/lib/server/rate-limit";

describe("/api/tutor/turn", () => {
  beforeEach(() => {
    resetRateLimitForTests();
  });

  it("returns a fallback tutor turn for a valid request", async () => {
    const request = new Request("http://localhost/api/tutor/turn", {
      method: "POST",
      body: JSON.stringify({
        config: defaultScenarioConfig,
        messages: [createMessage("partner", "Hola, en que puedo ayudarle?")],
        userInput: "Tengo alergias y necesito medicina.",
      }),
    });

    const response = await POST(request);
    const json = await response.json();

    expect(response.status).toBe(200);
    expect(json.partnerMessage).toBeTruthy();
    expect(json.coachFeedback.repairedPhrase).toBeTruthy();
  });

  it("rejects empty user input", async () => {
    const request = new Request("http://localhost/api/tutor/turn", {
      method: "POST",
      body: JSON.stringify({
        config: defaultScenarioConfig,
        messages: [],
        userInput: "",
      }),
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
  });

  it("rate limits repeated tutor requests from the same client", async () => {
    const body = JSON.stringify({
      config: defaultScenarioConfig,
      messages: [],
      userInput: "Tengo alergias y necesito medicina.",
    });

    let response: Response | null = null;
    for (let index = 0; index < 31; index += 1) {
      response = await POST(
        new Request("http://localhost/api/tutor/turn", {
          method: "POST",
          headers: {
            "x-forwarded-for": "203.0.113.9",
          },
          body,
        }),
      );
    }

    expect(response?.status).toBe(429);
    expect(response?.headers.get("Retry-After")).toBeTruthy();
  });
});
