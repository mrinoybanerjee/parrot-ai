import { NextResponse } from "next/server";
import { getProviderName } from "@/lib/tutor/provider";

export async function GET() {
  const provider = getProviderName();
  const status = {
    provider,
    ollamaModel: process.env.OLLAMA_MODEL ?? null,
    speech: "browser",
  };

  return NextResponse.json(status);
}
