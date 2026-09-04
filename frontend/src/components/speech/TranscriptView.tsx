"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  AlertTriangle,
  Radio,
  CheckCircle,
  HelpCircle,
  RotateCcw,
  Edit3,
  Check,
  X,
  Loader2,
} from "lucide-react";
import {
  StreamStatus,
  AgentDecision,
  ConfirmationStatus,
} from "@/hooks/useSpeechStream";

interface TranscriptViewProps {
  status: StreamStatus;
  partialTranscript: string;
  finalTranscript: string;
  confidence: number;
  error: string | null;
  provider: string | null;
  agentDecision: AgentDecision | null;
  confirmationStatus?: ConfirmationStatus;
  confirmPending?: boolean;
  onConfirmProposal?: () => void;
  onSelectCandidate?: (phrase: string) => void;
  onSubmitCorrection?: (phrase: string) => void;
  onRequestRepeat?: () => void;
}

export function TranscriptView({
  status,
  partialTranscript,
  finalTranscript,
  confidence,
  error,
  provider,
  agentDecision,
  confirmationStatus = "idle",
  confirmPending = false,
  onConfirmProposal,
  onSelectCandidate,
  onSubmitCorrection,
  onRequestRepeat,
}: TranscriptViewProps) {
  const hasText = Boolean(partialTranscript || finalTranscript);
  const [isCorrecting, setIsCorrecting] = useState(false);
  const [correctionText, setCorrectionText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Focus textarea when entering correction mode
  useEffect(() => {
    if (isCorrecting) {
      textareaRef.current?.focus();
    }
  }, [isCorrecting]);

  // Reset correction mode if agent decision changes or resets
  useEffect(() => {
    if (!agentDecision) {
      setIsCorrecting(false);
      setCorrectionText("");
    } else if (agentDecision.primary_phrase) {
      setCorrectionText(agentDecision.primary_phrase);
    }
  }, [agentDecision]);

  const handleStartCorrection = () => {
    setCorrectionText(agentDecision?.primary_phrase || finalTranscript || "");
    setIsCorrecting(true);
  };

  const handleCancelCorrection = () => {
    setIsCorrecting(false);
  };

  const handleSubmitCorrection = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = correctionText.trim();
    if (trimmed && onSubmitCorrection) {
      onSubmitCorrection(trimmed);
      setIsCorrecting(false);
    }
  };

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
              : confirmationStatus === "repeat_requested"
              ? "Decision cleared. Tap Speak below to try again."
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

      {/* PEEXH Agent Decision & Interactive Confirmation Section */}
      {agentDecision && confirmationStatus !== "confirmed" && (
        <div
          aria-labelledby="heading-agent-interpretation"
          className={`rounded-xl border p-5 sm:p-6 space-y-5 transition-all duration-300 ${
            agentDecision.confidence_level === "HIGH"
              ? "border-green-300 dark:border-green-800 bg-green-50/50 dark:bg-green-950/20"
              : agentDecision.confidence_level === "MEDIUM"
              ? "border-amber-300 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/20"
              : "border-slate-300 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-900/40"
          }`}
        >
          {/* Decision header & confidence badge */}
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

          {/* Pending indicator */}
          {confirmPending && (
            <div
              role="status"
              aria-live="polite"
              className="flex items-center gap-2 p-3 rounded-lg bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900 text-blue-700 dark:text-blue-300 text-sm font-medium"
            >
              <Loader2 className="w-4 h-4 animate-spin shrink-0" />
              <span>Confirming message with server...</span>
            </div>
          )}

          {/* Correction Mode Form (Available for all 3 decisions) */}
          {isCorrecting ? (
            <form onSubmit={handleSubmitCorrection} className="space-y-4 pt-1">
              <div className="space-y-1">
                <label
                  htmlFor="correction-input"
                  className="block text-xs font-bold uppercase tracking-wider text-foreground"
                >
                  Type your intended message:
                </label>
                <textarea
                  id="correction-input"
                  ref={textareaRef}
                  value={correctionText}
                  onChange={(e) => setCorrectionText(e.target.value)}
                  maxLength={500}
                  rows={3}
                  disabled={confirmPending}
                  aria-required="true"
                  placeholder="Type what you intended to say..."
                  className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 p-3 text-base text-foreground shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50"
                />
                <div className="flex justify-between text-xs text-slate-500">
                  <span>Enter up to 500 characters.</span>
                  <span>{correctionText.trim().length} / 500</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="submit"
                  disabled={!correctionText.trim() || confirmPending}
                  className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400 transition-all cursor-pointer"
                >
                  <Check className="w-4 h-4" aria-hidden="true" />
                  <span>Confirm correction</span>
                </button>
                <button
                  type="button"
                  onClick={handleCancelCorrection}
                  disabled={confirmPending}
                  className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl font-medium text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" aria-hidden="true" />
                  <span>Cancel</span>
                </button>
              </div>
            </form>
          ) : (
            <>
              {/* High Confidence: Propose Best Phrase */}
              {agentDecision.action === "PROPOSE_PHRASE" && agentDecision.primary_phrase && (
                <div className="space-y-4">
                  <div className="space-y-1">
                    <span className="text-xs uppercase tracking-wider font-semibold text-green-800 dark:text-green-400">
                      Suggested message
                    </span>
                    <p className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
                      &ldquo;{agentDecision.primary_phrase}&rdquo;
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      {agentDecision.reason}
                    </p>
                  </div>

                  {/* Primary & Recovery Controls */}
                  <div className="flex flex-wrap items-center gap-3 pt-1">
                    <button
                      type="button"
                      onClick={onConfirmProposal}
                      disabled={confirmPending}
                      className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-base text-white bg-green-600 hover:bg-green-700 active:bg-green-800 disabled:opacity-50 shadow-sm focus:outline-none focus-visible:ring-4 focus-visible:ring-green-400 transition-all cursor-pointer"
                    >
                      <Check className="w-5 h-5" aria-hidden="true" />
                      <span>Confirm message</span>
                    </button>

                    <button
                      type="button"
                      onClick={handleStartCorrection}
                      disabled={confirmPending}
                      className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl font-semibold text-sm text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 shadow-sm focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400 transition-all cursor-pointer"
                    >
                      <Edit3 className="w-4 h-4" aria-hidden="true" />
                      <span>Correct phrase</span>
                    </button>

                    <button
                      type="button"
                      onClick={onRequestRepeat}
                      disabled={confirmPending}
                      className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl font-medium text-sm text-slate-600 dark:text-slate-400 hover:text-foreground hover:bg-slate-200/50 dark:hover:bg-slate-800 transition-all cursor-pointer"
                    >
                      <RotateCcw className="w-4 h-4" aria-hidden="true" />
                      <span>Speak again</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Medium Confidence: Candidate Choices */}
              {agentDecision.action === "SHOW_CANDIDATES" && (
                <div className="space-y-4">
                  <span className="text-xs uppercase tracking-wider font-semibold text-amber-800 dark:text-amber-400">
                    Candidate Interpretations (Tap your intended phrase)
                  </span>

                  <div className="grid gap-2.5 sm:grid-cols-2">
                    {agentDecision.candidates.map((cand, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => onSelectCandidate && onSelectCandidate(cand.text)}
                        disabled={confirmPending}
                        className="min-h-[56px] text-left p-4 rounded-xl border border-amber-200 dark:border-amber-800/80 bg-white dark:bg-slate-800 hover:border-blue-500 hover:bg-blue-50/50 dark:hover:bg-slate-700/80 shadow-sm focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400 transition-all cursor-pointer disabled:opacity-50"
                      >
                        <p className="font-bold text-base sm:text-lg text-foreground">
                          {cand.text}
                        </p>
                        {cand.explanation && (
                          <p className="text-xs text-slate-500 mt-1">
                            {cand.explanation}
                          </p>
                        )}
                      </button>
                    ))}
                  </div>

                  {/* Recovery controls */}
                  <div className="flex flex-wrap items-center gap-3 pt-2">
                    <button
                      type="button"
                      onClick={handleStartCorrection}
                      disabled={confirmPending}
                      className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl font-semibold text-sm text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 shadow-sm focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400 transition-all cursor-pointer"
                    >
                      <Edit3 className="w-4 h-4" aria-hidden="true" />
                      <span>Correct phrase</span>
                    </button>

                    <button
                      type="button"
                      onClick={onRequestRepeat}
                      disabled={confirmPending}
                      className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl font-medium text-sm text-slate-600 dark:text-slate-400 hover:text-foreground hover:bg-slate-200/50 dark:hover:bg-slate-800 transition-all cursor-pointer"
                    >
                      <RotateCcw className="w-4 h-4" aria-hidden="true" />
                      <span>Speak again</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Low Confidence: Request Repeat */}
              {agentDecision.action === "REQUEST_REPEAT" && (
                <div className="space-y-4 text-slate-700 dark:text-slate-300">
                  <div className="space-y-1">
                    <p className="text-lg font-bold text-foreground">
                      PEEXH is not confident enough to guess.
                    </p>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      {agentDecision.reason || "We could not determine a reliable interpretation."} Please tap &ldquo;Speak again&rdquo; to retry or enter your phrase manually.
                    </p>
                  </div>

                  {/* Primary & Recovery controls */}
                  <div className="flex flex-wrap items-center gap-3 pt-1">
                    <button
                      type="button"
                      onClick={onRequestRepeat}
                      disabled={confirmPending}
                      className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:opacity-50 shadow-sm focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400 transition-all cursor-pointer"
                    >
                      <RotateCcw className="w-4 h-4" aria-hidden="true" />
                      <span>Speak again</span>
                    </button>

                    <button
                      type="button"
                      onClick={handleStartCorrection}
                      disabled={confirmPending}
                      className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl font-semibold text-sm text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 shadow-sm focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-400 transition-all cursor-pointer"
                    >
                      <Edit3 className="w-4 h-4" aria-hidden="true" />
                      <span>Enter phrase manually</span>
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
