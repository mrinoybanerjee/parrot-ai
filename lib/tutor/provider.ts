import type {
  ConversationMessage,
  ScenarioConfig,
  TutorTurnResponse,
} from "@/lib/domain";
import { createFallbackTurn } from "@/lib/tutor/fallback-provider";
import { buildTutorPrompt } from "@/lib/tutor/prompt";
import { parseProviderResponse } from "@/lib/tutor/response-parser";

type ProviderName = "fallback" | "ollama";

type ProviderInput = {
  config: ScenarioConfig;
  messages: ConversationMessage[];
  userInput: string;
};

export async function runTutorProvider(
  input: ProviderInput,
): Promise<TutorTurnResponse> {
  const provider = getProviderName();
  if (provider === "ollama") {
    return runOllamaProvider(input);
  }

  return createFallbackTurn(input.config, input.userInput);
}

export function getProviderName(): ProviderName {
  const provider = (process.env.TUTOR_PROVIDER ?? process.env.AI_PROVIDER)?.toLowerCase();
  if (provider === "ollama") {
    return "ollama";
  }
  if (provider === "fallback") {
    return "fallback";
  }
  if (process.env.OLLAMA_MODEL || process.env.OLLAMA_BASE_URL) {
    return "ollama";
  }
  return "fallback";
}

async function runOllamaProvider({
  config,
  messages,
  userInput,
}: ProviderInput): Promise<TutorTurnResponse> {
  const baseUrl = process.env.OLLAMA_BASE_URL ?? "http://localhost:11434";
  const model = process.env.OLLAMA_MODEL ?? "qwen3:8b";
  const prompt = buildTutorPrompt(config, messages, userInput);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 22_000);

  try {
    const response = await fetch(`${baseUrl}/v1/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        messages: [
          {
            role: "system",
            content:
              "You are a precise language tutor. Return only valid JSON.",
          },
          { role: "user", content: prompt },
        ],
        temperature: 0.7,
        stream: false,
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      return createFallbackTurn(
        config,
        userInput,
        `Ollama returned ${response.status}; fallback response used.`,
      );
    }

    const json = (await response.json()) as {
      choices?: Array<{ message?: { content?: string } }>;
    };
    const rawText = json.choices?.[0]?.message?.content;
    if (!rawText) {
      return createFallbackTurn(
        config,
        userInput,
        "Ollama returned an empty message; fallback response used.",
      );
    }
    return parseProviderResponse(rawText, config, userInput, "ollama");
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown Ollama provider error.";
    return createFallbackTurn(
      config,
      userInput,
      `Ollama unavailable (${message}); fallback response used.`,
    );
  } finally {
    clearTimeout(timeout);
  }
}
