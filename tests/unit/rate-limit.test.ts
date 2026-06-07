import { beforeEach, describe, expect, it } from "vitest";
import {
  checkRateLimit,
  getClientIp,
  resetRateLimitForTests,
} from "@/lib/server/rate-limit";

describe("rate limiting", () => {
  beforeEach(() => {
    resetRateLimitForTests();
  });

  it("allows requests until the configured limit is reached", () => {
    expect(checkRateLimit("client-a", { limit: 2, windowMs: 60_000 }).allowed).toBe(true);
    expect(checkRateLimit("client-a", { limit: 2, windowMs: 60_000 }).allowed).toBe(true);

    const blocked = checkRateLimit("client-a", { limit: 2, windowMs: 60_000 });

    expect(blocked.allowed).toBe(false);
    expect(blocked.remaining).toBe(0);
  });

  it("prefers forwarded client IP headers", () => {
    const request = new Request("http://localhost", {
      headers: {
        "x-forwarded-for": "203.0.113.1, 203.0.113.2",
        "x-real-ip": "198.51.100.1",
      },
    });

    expect(getClientIp(request)).toBe("203.0.113.1");
  });
});
