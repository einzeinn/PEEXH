"use client";

import React, { useEffect, useRef, useState } from "react";
import { Volume2, RotateCcw, PlusCircle, CheckCircle } from "lucide-react";
import { ConfirmedPhraseSource } from "@/hooks/useSpeechStream";

interface ConfirmedMessageViewProps {
  phrase: string;
  source: ConfirmedPhraseSource | null;
  onStartNew: () => void;
}

export function ConfirmedMessageView({
  phrase,
  source,
  onStartNew,
}: ConfirmedMessageViewProps) {
  const headingRef = useRef<HTMLHeadingElement>(null);
  const [hasPlayed, setHasPlayed] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ttsSupported, setTtsSupported] = useState(false);

  // Check TTS feature flag and browser support
  const ttsEnabled = process.env.NEXT_PUBLIC_ENABLE_TTS !== "false";

  useEffect(() => {
    // Check SpeechSynthesis support
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      setTtsSupported(true);
    }
    // Auto-focus the confirmed heading on mount for accessibility
    headingRef.current?.focus();
  }, []);

  const handleSpeak = () => {
    if (!ttsSupported || !ttsEnabled || !phrase) return;

    window.speechSynthesis.cancel(); // Stop any pending speech
    const utterance = new SpeechSynthesisUtterance(phrase);
    utterance.rate = 0.95; // Slightly slower for clarity
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => {
      setIsSpeaking(false);
      setHasPlayed(true);
    };
    utterance.onerror = () => {
      setIsSpeaking(false);
      setHasPlayed(true);
    };

    window.speechSynthesis.speak(utterance);
  };

  const getSourceLabel = () => {
    switch (source) {
      case "proposal":
        return "Confirmed Proposal";
      case "candidate":
        return "Selected Candidate";
      case "correction":
        return "Manual Correction";
      default:
        return "Confirmed Phrase";
    }
  };

  return (
    <div
      role="region"
      aria-label="Confirmed communication output"
      className="w-full rounded-2xl border-2 border-green-600 dark:border-green-500 bg-green-50/80 dark:bg-green-950/40 p-6 sm:p-8 space-y-6 shadow-md transition-all animate-in fade-in zoom-in-95 duration-200"
    >
      {/* Status Header */}
      <div className="flex items-center justify-between border-b border-green-200 dark:border-green-800 pb-3">
        <div className="flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-green-700 dark:text-green-400 shrink-0" aria-hidden="true" />
          <span className="text-xs font-bold uppercase tracking-wider text-green-800 dark:text-green-300">
            Ready to Communicate
          </span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-200 text-green-900 dark:bg-green-900 dark:text-green-200">
          {getSourceLabel()}
        </span>
      </div>

      {/* Confirmed Message Display */}
      <div className="space-y-2">
        <span className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400">
          Your Verified Message
        </span>
        <h2
          ref={headingRef}
          tabIndex={-1}
          className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight break-words focus:outline-none focus-visible:ring-2 focus-visible:ring-green-500 rounded-lg p-1"
        >
          &ldquo;{phrase}&rdquo;
        </h2>
      </div>

      {/* Action Controls */}
      <div className="flex flex-wrap items-center gap-3 pt-2">
        {/* TTS Button */}
        {ttsEnabled && ttsSupported && (
          <button
            type="button"
            onClick={handleSpeak}
            disabled={isSpeaking}
            aria-label={hasPlayed ? "Replay spoken message" : "Speak message out loud"}
            className="min-h-[48px] min-w-[48px] inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-base text-white bg-green-700 hover:bg-green-800 active:bg-green-900 shadow-sm focus:outline-none focus-visible:ring-4 focus-visible:ring-green-400 transition-all cursor-pointer disabled:opacity-50"
          >
            {hasPlayed ? (
              <>
                <RotateCcw className={`w-5 h-5 ${isSpeaking ? "animate-spin" : ""}`} aria-hidden="true" />
                <span>Replay message</span>
              </>
            ) : (
              <>
                <Volume2 className={`w-5 h-5 ${isSpeaking ? "animate-pulse" : ""}`} aria-hidden="true" />
                <span>{isSpeaking ? "Speaking..." : "Speak message"}</span>
              </>
            )}
          </button>
        )}

        {/* Start New Message Button */}
        <button
          type="button"
          onClick={onStartNew}
          aria-label="Start a new message"
          className="min-h-[48px] min-w-[48px] inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold text-base text-slate-800 dark:text-slate-100 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 shadow-sm focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400 transition-all cursor-pointer"
        >
          <PlusCircle className="w-5 h-5" aria-hidden="true" />
          <span>Start new message</span>
        </button>
      </div>
    </div>
  );
}
