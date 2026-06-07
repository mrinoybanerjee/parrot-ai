import { describe, expect, it } from "vitest";
import { defaultScenarioConfig, createMessage } from "@/lib/domain";
import { POST } from "@/app/api/tutor/turn/route";

describe("/api/tutor/turn", () => {
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
});
