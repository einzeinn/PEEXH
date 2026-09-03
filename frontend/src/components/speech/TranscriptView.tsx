"use client";

import React from "react";
import { Sparkles, AlertTriangle, Radio, CheckCircle, HelpCircle, RotateCcw } from "lucide-react";
import { StreamStatus, AgentDecision } from "@/hooks/useSpeechStream";

interface TranscriptViewProps {
  status: StreamStatus;
  partialTranscript: string;
  finalTranscript: string;
  confidence: number;
  error: string | null;
  provider: string | null;
  agentDecision: AgentDecision | null;
}

export function TranscriptView({
  status,
  partialTranscript,
  finalTranscript,
  confidence,
  error,
  provider,
  agentDecision,
}: TranscriptViewProps) {
  const hasText = Boolean(partialTranscript || finalTranscript);

  return (
    <div
      className="w-full rounded-2xl border border-surface-border bg-surface p-6 sm:p-8 space-y-6 shadow-sm"
      aria-labelledby="heading-transcript"
    >
      {/* Top Header Status */}
      <div className="flex items-center justify-between border-b border-surface-border pb-3">
        <div className="flex items-center gap-2">
          <h2
            id="heading-transcript"
            className="text-xs font-semibold text-foreground uppercase tracking-wider"
          >
            Live Speech Transcript
          </h2>
          {provider && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
              <Radio className="w-3 h-3 text-blue-500" aria-hidden="true" />
              <span>{provider === "assemblyai" ? "AssemblyAI STT" : "Local Mock STT"}</span>
            </span>
          )}
        </div>

        {confidence > 0 && finalTranscript && (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            <span>STT acoustic: {Math.round(confidence * 100)}%</span>
          </span>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div
          role="alert"
          className="flex items-start gap-3 p-4 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-sm"
        >
          <AlertTriangle className="w-5 h-5 shrink-0 text-red-600 dark:text-red-400 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      {/* Raw Transcript Area */}
      <div
        role="region"
        aria-live="polite"
        className="min-h-[100px] flex flex-col justify-center rounded-xl bg-surface-muted p-5 sm:p-6"
      >
        {!hasText && !error && (
          <p className="text-slate-400 dark:text-slate-500 text-center text-base sm:text-lg italic">
            {status === "listening"
              ? "Listening to speech..."
              : "Tap the button below and speak. Your speech will transcribe here."}
          </p>
        )}

        {finalTranscript && (
          <div className="space-y-1">
            <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">
              Raw Speech-to-Text
            </span>
            <p className="text-xl sm:text-2xl font-medium tracking-tight text-slate-700 dark:text-slate-300 leading-snug">
              &ldquo;{finalTranscript}&rdquo;
            </p>
          </div>
        )}

        {partialTranscript && (
          <div className="space-y-1">
            <span className="text-xs uppercase tracking-wider font-medium text-slate-500">
              Listening...
            </span>
            <p className="text-xl sm:text-2xl font-medium text-slate-500 animate-pulse leading-snug">
              {partialTranscript}
            </p>
          </div>
        )}
      </div>

      {/* PEEXH Agent Decision & Interpretation Section */}
      {agentDecision && (
        <div
          aria-labelledby="heading-agent-interpretation"
          className={`rounded-xl border p-5 sm:p-6 space-y-4 transition-all duration-300 ${
            agentDecision.confidence_level === "HIGH"
              ? "border-green-300 dark:border-green-800 bg-green-50/50 dark:bg-green-950/20"
              : agentDecision.confidence_level === "MEDIUM"
              ? "border-amber-300 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/20"
              : "border-slate-300 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-900/40"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {agentDecision.confidence_level === "HIGH" ? (
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              ) : agentDecision.confidence_level === "MEDIUM" ? (
                <HelpCircle className="w-5 h-5 text-amber-600 dark:text-amber-400" />
              ) : (
                <RotateCcw className="w-5 h-5 text-slate-500" />
              )}
              <h3
                id="heading-agent-interpretation"
                className="text-sm font-bold tracking-wide uppercase text-foreground"
              >
                PEEXH Interpretation
              </h3>
            </div>

            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                agentDecision.confidence_level === "HIGH"
                  ? "bg-green-200/70 text-green-900 dark:bg-green-900/60 dark:text-green-200"
                  : agentDecision.confidence_level === "MEDIUM"
                  ? "bg-amber-200/70 text-amber-900 dark:bg-amber-900/60 dark:text-amber-200"
                  : "bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-300"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>
                {agentDecision.confidence_level} CONFIDENCE (
                {Math.round(agentDecision.overall_confidence * 100)}%)
              </span>
            </span>
          </div>

          {/* High Confidence: Propose Best Phrase */}
          {agentDecision.action === "PROPOSE_PHRASE" && agentDecision.primary_phrase && (
            <div className="space-y-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-green-800 dark:text-green-400">
                Most Likely Intended Message
              </span>
              <p className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
                {agentDecision.primary_phrase}
              </p>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                {agentDecision.reason}
              </p>
            </div>
          )}

          {/* Medium Confidence: Candidate Choices */}
          {agentDecision.action === "SHOW_CANDIDATES" && (
            <div className="space-y-3">
              <span className="text-xs uppercase tracking-wider font-semibold text-amber-800 dark:text-amber-400">
                Candidate Interpretations (Select your intended phrase)
              </span>
              <div className="grid gap-2 sm:grid-cols-2">
                {agentDecision.candidates.map((cand, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg border border-surface-border bg-surface hover:border-blue-500 transition-colors"
                  >
                    <p className="font-semibold text-base text-foreground">
                      {cand.text}
                    </p>
                    {cand.explanation && (
                      <p className="text-xs text-slate-500 mt-0.5">
                        {cand.explanation}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Low Confidence: Request Repeat */}
          {agentDecision.action === "REQUEST_REPEAT" && (
            <div className="space-y-2 text-slate-700 dark:text-slate-300">
              <p className="text-lg font-semibold">
                PEEXH is not confident enough to guess.
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                {agentDecision.reason} Please tap the microphone and speak again.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
