"use client";

import React from "react";
import { Mic, Square, Loader2, AlertCircle } from "lucide-react";
import { StreamStatus } from "@/hooks/useSpeechStream";

interface TapToTalkButtonProps {
  status: StreamStatus;
  onStart: () => void;
  onStop: () => void;
}

export function TapToTalkButton({ status, onStart, onStop }: TapToTalkButtonProps) {
  const isListening = status === "listening";
  const isBusy = status === "connecting" || status === "stopping";

  const handleClick = () => {
    if (isListening) {
      onStop();
    } else if (status === "idle" || status === "error") {
      onStart();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <button
        type="button"
        onClick={handleClick}
        disabled={isBusy}
        aria-pressed={isListening}
        aria-label={
          isListening
            ? "Stop speaking"
            : status === "error"
            ? "Retry speaking"
            : "Start speaking"
        }
        className={`relative group flex items-center justify-center w-28 h-28 sm:w-32 sm:h-32 rounded-full transition-all duration-300 shadow-lg select-none cursor-pointer focus:outline-none focus-visible:ring-4 focus-visible:ring-offset-4 ${
          isListening
            ? "bg-red-600 hover:bg-red-700 text-white focus-visible:ring-red-500 scale-105"
            : isBusy
            ? "bg-slate-200 dark:bg-slate-800 text-slate-500 cursor-not-allowed"
            : status === "error"
            ? "bg-amber-600 hover:bg-amber-700 text-white focus-visible:ring-amber-500"
            : "bg-blue-600 hover:bg-blue-700 text-white focus-visible:ring-blue-500 hover:scale-105"
        }`}
      >
        {/* Pulsing ring during recording */}
        {isListening && (
          <span
            className="absolute -inset-2 rounded-full bg-red-500/30 animate-ping pointer-events-none"
            aria-hidden="true"
          />
        )}

        {/* Icon representation */}
        {isBusy ? (
          <Loader2 className="w-12 h-12 animate-spin" aria-hidden="true" />
        ) : isListening ? (
          <Square className="w-10 h-10 fill-current" aria-hidden="true" />
        ) : status === "error" ? (
          <AlertCircle className="w-12 h-12" aria-hidden="true" />
        ) : (
          <Mic className="w-12 h-12" aria-hidden="true" />
        )}
      </button>

      {/* State label */}
      <div
        role="status"
        aria-live="polite"
        className="text-center space-y-1"
      >
        <p className="text-lg font-bold text-foreground">
          {isListening
            ? "Listening... Tap to stop"
            : status === "connecting"
            ? "Connecting..."
            : status === "stopping"
            ? "Processing..."
            : status === "error"
            ? "Tap to try again"
            : "Tap to Speak"}
        </p>
        <p className="text-xs text-slate-500 max-w-xs">
          {isListening
            ? "Speak naturally. Tap when finished."
            : "One tap to start. No holding required."}
        </p>
      </div>
    </div>
  );
}
