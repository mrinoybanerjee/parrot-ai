import type {
  CoachFeedback,
  ScenarioConfig,
  SessionScore,
  TutorTurnResponse,
} from "@/lib/domain";

const partnerLines: Record<ScenarioConfig["language"], string[]> = {
  English: [
    "I understand. Could you explain one more detail so I can help you better?",
    "That makes sense. What would you like to do next?",
  ],
  Spanish: [
    "Entiendo. Puede contarme un poco mas para ayudarle mejor?",
    "Claro. Que prefiere hacer ahora?",
  ],
  French: [
    "Je comprends. Pouvez-vous me donner un peu plus de contexte?",
    "Bien sur. Qu'est-ce que vous aimeriez faire maintenant?",
  ],
  German: [
    "Ich verstehe. Konnen Sie mir noch ein Detail nennen?",
    "Naturlich. Was mochten Sie als Nachstes tun?",
  ],
  Hindi: [
    "Samajh gaya. Kripya thoda aur bataiye taaki main madad kar sakun.",
    "Theek hai. Aap ab kya karna chahenge?",
  ],
  Japanese: [
    "わかりました。もう少し詳しく教えていただけますか。",
    "そうですね。次にどうしたいですか。",
  ],
  Korean: [
    "알겠습니다. 조금 더 자세히 말씀해 주시겠어요?",
    "좋습니다. 이제 어떻게 하고 싶으세요?",
  ],
  Portuguese: [
    "Entendo. Pode me dar mais um detalhe para eu ajudar melhor?",
    "Claro. O que voce gostaria de fazer agora?",
  ],
  Italian: [
    "Capisco. Puo darmi un dettaglio in piu per aiutarla meglio?",
    "Certo. Che cosa vorrebbe fare adesso?",
  ],
  Arabic: [
    "فهمت. هل يمكنك أن تعطيني تفصيلا إضافيا؟",
    "حسنا. ماذا تريد أن تفعل الآن؟",
  ],
};

export function createFallbackTurn(
  config: ScenarioConfig,
  userInput: string,
  warning?: string,
): TutorTurnResponse {
  const shortInput = userInput.trim().slice(0, 140);
  const lines = partnerLines[config.language];
  const line = lines[shortInput.length % lines.length];
  const repairedPhrase = buildRepairPhrase(config);
  const feedback: CoachFeedback = {
    summary: `You kept the conversation moving. Now make the turn more specific to the goal: ${config.goal}`,
    correction: `Try adding one concrete detail instead of a broad answer. Your turn was: "${shortInput}"`,
    repairedPhrase,
    encouragement:
      config.intensity === "Stretch"
        ? "Stay in the target language and answer the follow-up directly."
        : "Good momentum. Keep the next answer short and concrete.",
  };
  const score: SessionScore = {
    clarity: Math.min(88, 58 + Math.floor(shortInput.length / 5)),
    culturalFit: config.culturalFocus.length > 0 ? 72 : 55,
    momentum: shortInput.split(/\s+/).length >= 4 ? 76 : 58,
  };

  return {
    partnerMessage: line,
    coachFeedback: feedback,
    culturalNote: `In this scenario, ${config.culturalFocus.toLowerCase()}`,
    phraseBankAdditions: [repairedPhrase, buildScenarioPhrase(config)],
    sessionScore: score,
    provider: "fallback",
    warning,
  };
}

function buildRepairPhrase(config: ScenarioConfig): string {
  switch (config.language) {
    case "Spanish":
      return "Podria recomendarme una opcion adecuada?";
    case "French":
      return "Pourriez-vous me recommander une option adaptee?";
    case "German":
      return "Konnten Sie mir eine passende Option empfehlen?";
    case "Hindi":
      return "Kya aap mujhe ek sahi vikalp bata sakte hain?";
    case "Japanese":
      return "合うものをおすすめしていただけますか。";
    case "Korean":
      return "저에게 맞는 선택지를 추천해 주실 수 있나요?";
    case "Portuguese":
      return "Voce poderia me recomendar uma opcao adequada?";
    case "Italian":
      return "Potrebbe consigliarmi un'opzione adatta?";
    case "Arabic":
      return "هل يمكنك أن تنصحني بخيار مناسب؟";
    default:
      return "Could you recommend a suitable option?";
  }
}

function buildScenarioPhrase(config: ScenarioConfig): string {
  switch (config.proficiency) {
    case "Beginner":
      return `I need help with ${config.scenario.split(" ").slice(0, 5).join(" ")}`;
    case "Advanced":
      return `I want to handle this with the right tone: ${config.culturalFocus}`;
    default:
      return `Can I explain the situation first?`;
  }
}
