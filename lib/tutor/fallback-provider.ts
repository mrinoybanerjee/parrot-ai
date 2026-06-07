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
    "Entiendo. ¿Puede contarme un poco más para ayudarle mejor?",
    "Claro. ¿Qué prefiere hacer ahora?",
  ],
  French: [
    "Je comprends. Pouvez-vous me donner un peu plus de contexte?",
    "Bien sûr. Qu'est-ce que vous aimeriez faire maintenant?",
  ],
  German: [
    "Ich verstehe. Können Sie mir noch ein Detail nennen?",
    "Natürlich. Was möchten Sie als Nächstes tun?",
  ],
  Hindi: [
    "समझ गया। कृपया थोड़ा और बताइए ताकि मैं बेहतर मदद कर सकूं।",
    "ठीक है। अब आप क्या करना चाहेंगे?",
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
    "Claro. O que você gostaria de fazer agora?",
  ],
  Italian: [
    "Capisco. Può darmi un dettaglio in più per aiutarla meglio?",
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
  const feedback = buildCoachFeedback(config, shortInput, repairedPhrase);
  const score: SessionScore = {
    clarity: Math.min(88, 58 + Math.floor(shortInput.length / 5)),
    culturalFit: config.culturalFocus.length > 0 ? 72 : 55,
    momentum: shortInput.split(/\s+/).length >= 4 ? 76 : 58,
  };

  return {
    partnerMessage: line,
    coachFeedback: feedback,
    culturalNote: buildCulturalNote(config),
    phraseBankAdditions: [repairedPhrase, buildScenarioPhrase(config)],
    sessionScore: score,
    provider: "fallback",
    warning,
  };
}

function buildCoachFeedback(
  config: ScenarioConfig,
  shortInput: string,
  repairedPhrase: string,
): CoachFeedback {
  if (config.nativeLanguage === "Hindi") {
    return {
      summary: "आपने बातचीत जारी रखी। अब अपना उद्देश्य और स्पष्ट करें।",
      correction: `एक ठोस जानकारी जोड़ें। आपका उत्तर था: "${shortInput}"`,
      repairedPhrase,
      encouragement:
        config.intensity === "Stretch"
          ? "लक्ष्य भाषा में रहें और अगले सवाल का सीधे जवाब दें।"
          : "अच्छी शुरुआत। अगला उत्तर छोटा और स्पष्ट रखें।",
    };
  }

  return {
    summary: `You kept the conversation moving. Now make the turn more specific to the goal: ${config.goal}`,
    correction: `Try adding one concrete detail instead of a broad answer. Your turn was: "${shortInput}"`,
    repairedPhrase,
    encouragement:
      config.intensity === "Stretch"
        ? "Stay in the target language and answer the follow-up directly."
        : "Good momentum. Keep the next answer short and concrete.",
  };
}

function buildCulturalNote(config: ScenarioConfig): string {
  if (config.nativeLanguage === "Hindi") {
    return "इस स्थिति में विनम्र अभिवादन और सम्मानजनक अनुरोध पर ध्यान दें।";
  }

  return `In this scenario, ${config.culturalFocus.toLowerCase()}`;
}

function buildRepairPhrase(config: ScenarioConfig): string {
  switch (config.language) {
    case "Spanish":
      return "¿Podría recomendarme una opción adecuada?";
    case "French":
      return "Pourriez-vous me recommander une option adaptée?";
    case "German":
      return "Könnten Sie mir eine passende Option empfehlen?";
    case "Hindi":
      return "क्या आप मुझे एक उचित विकल्प सुझा सकते हैं?";
    case "Japanese":
      return "合うものをおすすめしていただけますか。";
    case "Korean":
      return "저에게 맞는 선택지를 추천해 주실 수 있나요?";
    case "Portuguese":
      return "Você poderia me recomendar uma opção adequada?";
    case "Italian":
      return "Potrebbe consigliarmi un'opzione adatta?";
    case "Arabic":
      return "هل يمكنك أن تنصحني بخيار مناسب؟";
    default:
      return "Could you recommend a suitable option?";
  }
}

function buildScenarioPhrase(config: ScenarioConfig): string {
  const phrases: Record<ScenarioConfig["language"], Record<ScenarioConfig["proficiency"], string>> = {
    English: {
      Beginner: "I need help with this.",
      Intermediate: "Can I explain the situation first?",
      Advanced: "I want to handle this with the right tone.",
    },
    Spanish: {
      Beginner: "Necesito ayuda con esto.",
      Intermediate: "¿Puedo explicar primero la situación?",
      Advanced: "Quiero manejar esto con el tono adecuado.",
    },
    French: {
      Beginner: "J'ai besoin d'aide avec cela.",
      Intermediate: "Puis-je d'abord expliquer la situation?",
      Advanced: "Je veux gérer cela avec le ton approprié.",
    },
    German: {
      Beginner: "Ich brauche dabei Hilfe.",
      Intermediate: "Kann ich zuerst die Situation erklären?",
      Advanced: "Ich möchte das mit dem richtigen Ton angehen.",
    },
    Hindi: {
      Beginner: "मुझे इसमें मदद चाहिए।",
      Intermediate: "क्या मैं पहले स्थिति समझा सकता हूँ?",
      Advanced: "मैं इसे सही लहजे में संभालना चाहता हूँ।",
    },
    Japanese: {
      Beginner: "これについて助けが必要です。",
      Intermediate: "まず状況を説明してもいいですか。",
      Advanced: "適切な口調で対応したいです。",
    },
    Korean: {
      Beginner: "이 일에 도움이 필요합니다.",
      Intermediate: "먼저 상황을 설명해도 될까요?",
      Advanced: "적절한 말투로 대응하고 싶습니다.",
    },
    Portuguese: {
      Beginner: "Preciso de ajuda com isso.",
      Intermediate: "Posso explicar a situação primeiro?",
      Advanced: "Quero lidar com isso no tom adequado.",
    },
    Italian: {
      Beginner: "Ho bisogno di aiuto con questo.",
      Intermediate: "Posso spiegare prima la situazione?",
      Advanced: "Voglio gestire la cosa con il tono giusto.",
    },
    Arabic: {
      Beginner: "أحتاج إلى مساعدة في هذا.",
      Intermediate: "هل يمكنني شرح الموقف أولا؟",
      Advanced: "أريد التعامل مع هذا بالنبرة المناسبة.",
    },
  };

  return phrases[config.language][config.proficiency];
}
