"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { useSpeechStream } from "@/hooks/useSpeechStream";
import { TapToTalkButton } from "@/components/speech/TapToTalkButton";
import { TranscriptView } from "@/components/speech/TranscriptView";
import { ConfirmedMessageView } from "@/components/speech/ConfirmedMessageView";

interface BackendHealth {
  status: string;
  app: string;
  environment: string;
}

export default function HomePage() {
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(true);
  const [healthError, setHealthError] = useState<string | null>(null);

  const {
    status,
    partialTranscript,
    finalTranscript,
    confidence,
    error: speechError,
    provider,
    agentDecision,
    confirmationStatus,
    confirmedPhrase,
    confirmedSource,
    confirmPending,
    startRecording,
    stopRecording,
    confirmProposal,
    selectCandidate,
    submitCorrection,
    requestRepeat,
  } = useSpeechStream();


  const checkBackendHealth = async () => {
    setLoadingHealth(true);
    setHealthError(null);
    try {
      const apiBaseUrl =
        process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const res = await fetch(`${apiBaseUrl}/health`, {
        cache: "no-store",
      });
      if (!res.ok) {
        throw new Error(`HTTP error ${res.status}`);
      }
      const data = await res.json();
      setHealth(data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to connect to backend";
      setHealthError(message);
      setHealth(null);
    } finally {
      setLoadingHealth(false);
    }
  };

  useEffect(() => {
    checkBackendHealth();
  }, []);

  return (
    <div className="flex flex-col gap-8 pb-12">
      {/* Brand & Introduction */}
      <section aria-labelledby="heading-overview" className="space-y-2">
        <h1
          id="heading-overview"
          className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground"
        >
          Be understood.
        </h1>
        <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl">
          A voice communication aid designed for people with dysarthria. Speak
          at your own pace; PEEXH captures and interprets your voice in realtime.
        </p>
      </section>

      {/* Main Accessible Speech Interface */}
      <section
        aria-label="Speech communication area"
        className="flex flex-col items-center gap-8"
      >
        {/* Confirmed Communication Output View */}
        {confirmationStatus === "confirmed" && confirmedPhrase && (
          <ConfirmedMessageView
            phrase={confirmedPhrase}
            source={confirmedSource}
            onStartNew={startRecording}
          />
        )}

        {/* Realtime Transcript & Decision Controls Display */}
        <TranscriptView
          status={status}
          partialTranscript={partialTranscript}
          finalTranscript={finalTranscript}
          confidence={confidence}
          error={speechError}
          provider={provider}
          agentDecision={agentDecision}
          confirmationStatus={confirmationStatus}
          confirmPending={confirmPending}
          onConfirmProposal={confirmProposal}
          onSelectCandidate={selectCandidate}
          onSubmitCorrection={submitCorrection}
          onRequestRepeat={requestRepeat}
        />

        {/* Primary Accessible Tap-to-Talk Action */}
        <TapToTalkButton
          status={status}
          onStart={startRecording}
          onStop={stopRecording}
        />
      </section>

      {/* System Status and Diagnostics */}
      <section
        aria-labelledby="heading-status"
        className="mt-6 rounded-xl border border-surface-border bg-surface p-5 space-y-3 shadow-sm text-sm"
      >
        <div className="flex items-center justify-between">
          <h2
            id="heading-status"
            className="font-semibold text-foreground text-xs uppercase tracking-wider"
          >
            Backend & Service Connectivity
          </h2>
          <button
            onClick={checkBackendHealth}
            disabled={loadingHealth}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-md border border-surface-border hover:bg-surface-muted transition-colors disabled:opacity-50"
            aria-label="Refresh backend status"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${loadingHealth ? "animate-spin" : ""}`}
              aria-hidden="true"
            />
            <span>Refresh</span>
          </button>
        </div>

        {loadingHealth && (
          <div role="status" aria-live="polite" className="text-xs text-slate-500">
            Checking backend status...
          </div>
        )}

        {!loadingHealth && health && (
          <div
            role="status"
            aria-live="polite"
            className="flex items-center gap-2 text-xs text-green-700 dark:text-green-400"
          >
            <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400 shrink-0" />
            <span>
              Connected to backend (Environment:{" "}
              <strong className="font-mono">{health.environment}</strong>)
            </span>
          </div>
        )}

        {!loadingHealth && healthError && (
          <div
            role="status"
            aria-live="polite"
            className="flex items-center gap-2 text-xs text-amber-700 dark:text-amber-400"
          >
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>
              Backend offline: ensure server is running on{" "}
              <code>
                {process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}
              </code>
            </span>
          </div>
        )}
      </section>
    </div>
  );
}
