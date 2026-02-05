"use client";

import { useState, useCallback } from "react";

type VoiceState = "idle" | "listening" | "processing" | "speaking";

export default function useVoiceState() {
  const [state, setState] = useState<VoiceState>("idle");

  const startListening = useCallback(() => {
    setState("listening");
  }, []);

  const stopListening = useCallback(() => {
    setState("processing");
    setTimeout(() => setState("idle"), 1200);
  }, []);

  return { state, startListening, stopListening } as const;
}
