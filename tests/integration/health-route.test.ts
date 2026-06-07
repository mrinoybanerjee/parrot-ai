import { describe, expect, it } from "vitest";
import { GET } from "@/app/api/health/route";

describe("/api/health", () => {
  it("returns service health", async () => {
    const response = await GET();
    const json = await response.json();

    expect(response.status).toBe(200);
    expect(json.ok).toBe(true);
    expect(json.provider).toBeTruthy();
    expect(Date.parse(json.timestamp)).not.toBeNaN();
  });
});
