"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Language } from "@/lib/domain";
import { languageCodes } from "@/lib/domain";

type SpeechState = {
  isRecognitionSupported: boolean;
  isSynthesisSupported: boolean;
  isListening: boolean;
  interimTranscript: string;
  error: string | null;
  startListening: (language: Language) => void;
  stopListening: () => void;
  speak: (text: string, language: Language) => void;
  cancelSpeech: () => void;
};

export function useBrowserSpeech(onFinalTranscript: (text: string) => void): SpeechState {
  const [isListening, setIsListening] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [speechSupport, setSpeechSupport] = useState({
    recognition: false,
    synthesis: false,
  });
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const recognitionConstructorRef = useRef<SpeechRecognitionConstructor | undefined>(undefined);
  const finalTranscriptRef = useRef(onFinalTranscript);

  useEffect(() => {
    finalTranscriptRef.current = onFinalTranscript;
  }, [onFinalTranscript]);

  useEffect(() => {
    recognitionConstructorRef.current =
      window.SpeechRecognition ?? window.webkitSpeechRecognition;
    setSpeechSupport({
      recognition: Boolean(recognitionConstructorRef.current),
      synthesis: "speechSynthesis" in window,
    });
  }, []);

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  const startListening = useCallback(
    (language: Language) => {
      const SpeechRecognitionCtor = recognitionConstructorRef.current;
      if (!SpeechRecognitionCtor) {
        setError("Speech recognition is not available in this browser.");
        return;
      }

      setError(null);
      setInterimTranscript("");
      const recognition = new SpeechRecognitionCtor();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = languageCodes[language];
      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let finalText = "";
        let interimText = "";
        for (let index = event.resultIndex; index < event.results.length; index += 1) {
          const result = event.results[index];
          const transcript = result[0]?.transcript ?? "";
          if (result.isFinal) {
            finalText += transcript;
          } else {
            interimText += transcript;
          }
        }
        setInterimTranscript(interimText.trim());
        if (finalText.trim()) {
          finalTranscriptRef.current(finalText.trim());
        }
      };
      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        setError(event.message || event.error || "Speech recognition failed.");
        setIsListening(false);
      };
      recognition.onend = () => {
        setIsListening(false);
      };
      recognitionRef.current = recognition;
      recognition.start();
      setIsListening(true);
    },
    [],
  );

  const speak = useCallback((text: string, language: Language) => {
    if (typeof window === "undefined") {
      return;
    }
    if (!("speechSynthesis" in window)) {
      setError("Speech synthesis is not available in this browser.");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = languageCodes[language];
    utterance.rate = 0.94;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  }, []);

  const cancelSpeech = useCallback(() => {
    if (typeof window === "undefined") {
      return;
    }
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  }, []);

  return {
    isRecognitionSupported: speechSupport.recognition,
    isSynthesisSupported: speechSupport.synthesis,
    isListening,
    interimTranscript,
    error,
    startListening,
    stopListening,
    speak,
    cancelSpeech,
  };
}
