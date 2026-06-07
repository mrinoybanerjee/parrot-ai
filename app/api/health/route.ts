import { NextResponse } from "next/server";
import { getProviderName } from "@/lib/tutor/provider";

export async function GET() {
  return NextResponse.json({
    ok: true,
    provider: getProviderName(),
    timestamp: new Date().toISOString(),
  });
}
