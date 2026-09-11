"use client";

import React, { useState } from "react";
import { History, Volume2, Copy, Check, Trash2 } from "lucide-react";
import { ConfirmedPhraseSource } from "@/hooks/useSpeechStream";

export interface HistoryItem {
  id: string;
  phrase: string;
  source: ConfirmedPhraseSource | null;
  timestamp: Date;
}

interface CommunicationHistoryProps {
  items: HistoryItem[];
  onClear: () => void;
}

export function CommunicationHistory({
  items,
  onClear,
}: CommunicationHistoryProps) {
  const [speakingId, setSpeakingId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const ttsEnabled = process.env.NEXT_PUBLIC_ENABLE_TTS !== "false";
  const ttsSupported =
    typeof window !== "undefined" && "speechSynthesis" in window;

  const handleSpeak = (item: HistoryItem) => {
    if (!ttsSupported || !ttsEnabled || !item.phrase) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(item.phrase);
    utterance.rate = 0.95;
    utterance.onstart = () => setSpeakingId(item.id);
    utterance.onend = () => setSpeakingId(null);
    utterance.onerror = () => setSpeakingId(null);

    window.speechSynthesis.speak(utterance);
  };

  const handleCopy = async (item: HistoryItem) => {
    try {
      await navigator.clipboard.writeText(item.phrase);
      setCopiedId(item.id);
      setTimeout(() => {
        setCopiedId(null);
      }, 2000);
    } catch {
      // Graceful fallback if clipboard API fails
    }
  };

  const getSourceBadge = (source: ConfirmedPhraseSource | null) => {
    switch (source) {
      case "proposal":
        return {
          label: "Proposal",
          classes:
            "bg-green-100 text-green-800 dark:bg-green-950/60 dark:text-green-300 border-green-200 dark:border-green-800",
        };
      case "candidate":
        return {
          label: "Candidate",
          classes:
            "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800",
        };
      case "correction":
        return {
          label: "Correction",
          classes:
            "bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border-blue-200 dark:border-blue-800",
        };
      default:
        return {
          label: "Verified",
          classes:
            "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700",
        };
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  if (items.length === 0) {
    return null;
  }

  return (
    <section
      aria-labelledby="heading-history"
      className="w-full rounded-2xl border border-surface-border bg-surface p-6 sm:p-8 space-y-4 shadow-sm"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-border pb-3">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-blue-500" aria-hidden="true" />
          <h2
            id="heading-history"
            className="text-xs font-semibold text-foreground uppercase tracking-wider"
          >
            Session History
          </h2>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            {items.length}
          </span>
        </div>

        <button
          type="button"
          onClick={onClear}
          aria-label="Clear session history"
          className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition-colors cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Clear</span>
        </button>
      </div>

      {/* History List */}
      <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
        {items.map((item) => {
          const badge = getSourceBadge(item.source);
          const isItemSpeaking = speakingId === item.id;
          const isItemCopied = copiedId === item.id;

          return (
            <div
              key={item.id}
              className="flex items-center justify-between gap-4 p-4 rounded-xl border border-surface-border bg-surface-muted/60 hover:bg-surface-muted transition-colors"
            >
              <div className="space-y-1 min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-block px-2 py-0.5 rounded-md text-[11px] font-semibold border ${badge.classes}`}
                  >
                    {badge.label}
                  </span>
                  <time className="text-xs text-slate-400 dark:text-slate-500">
                    {formatTime(item.timestamp)}
                  </time>
                </div>
                <p className="text-base sm:text-lg font-semibold text-foreground leading-snug break-words">
                  &ldquo;{item.phrase}&rdquo;
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 shrink-0">
                {ttsEnabled && ttsSupported && (
                  <button
                    type="button"
                    onClick={() => handleSpeak(item)}
                    disabled={isItemSpeaking}
                    aria-label={`Speak "${item.phrase}"`}
                    title="Speak out loud"
                    className="min-h-[40px] min-w-[40px] inline-flex items-center justify-center p-2 rounded-xl text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all cursor-pointer disabled:opacity-50"
                  >
                    <Volume2
                      className={`w-4 h-4 text-green-600 dark:text-green-400 ${
                        isItemSpeaking ? "animate-pulse" : ""
                      }`}
                      aria-hidden="true"
                    />
                  </button>
                )}

                <button
                  type="button"
                  onClick={() => handleCopy(item)}
                  aria-label={`Copy "${item.phrase}"`}
                  title="Copy text"
                  className="min-h-[40px] min-w-[40px] inline-flex items-center justify-center p-2 rounded-xl text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all cursor-pointer"
                >
                  {isItemCopied ? (
                    <Check
                      className="w-4 h-4 text-green-600 dark:text-green-400"
                      aria-hidden="true"
                    />
                  ) : (
                    <Copy className="w-4 h-4 text-slate-500" aria-hidden="true" />
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
