import { NextResponse } from "next/server";
import { tutorTurnRequestSchema } from "@/lib/domain";
import { runTutorProvider } from "@/lib/tutor/provider";

export async function POST(request: Request) {
  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: "Request body must be valid JSON." },
      { status: 400 },
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
      { status: 400 },
    );
  }

  const result = await runTutorProvider(parsed.data);
  return NextResponse.json(result);
}
