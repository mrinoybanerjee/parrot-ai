import { NextResponse } from "next/server";
import { tutorTurnRequestSchema } from "@/lib/domain";
import { checkRateLimit, getClientIp } from "@/lib/server/rate-limit";
import { runTutorProvider } from "@/lib/tutor/provider";

export async function POST(request: Request) {
  const rateLimit = checkRateLimit(getClientIp(request));
  const rateLimitHeaders = {
    "X-RateLimit-Remaining": String(rateLimit.remaining),
    "X-RateLimit-Reset": String(Math.ceil(rateLimit.resetAt / 1000)),
  };
  if (!rateLimit.allowed) {
    return NextResponse.json(
      { error: "Too many tutor requests. Please wait and try again." },
      {
        headers: {
          ...rateLimitHeaders,
          "Retry-After": String(Math.max(1, Math.ceil((rateLimit.resetAt - Date.now()) / 1000))),
        },
        status: 429,
      },
    );
  }

  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: "Request body must be valid JSON." },
      { headers: rateLimitHeaders, status: 400 },
    );
  }

  const parsed = tutorTurnRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      {
        error: "Invalid tutor turn request.",
        issues: parsed.error.issues.map((issue) => ({
          path: issue.path.join("."),
          message: issue.message,
        })),
      },
      { headers: rateLimitHeaders, status: 400 },
    );
  }

  const result = await runTutorProvider(parsed.data);
  return NextResponse.json(result, { headers: rateLimitHeaders });
}
