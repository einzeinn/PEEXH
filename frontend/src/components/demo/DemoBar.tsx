"use client";

import React, { useState } from "react";
import { FlaskConical, ChevronDown, ChevronUp, Zap } from "lucide-react";

/** A single pre-set dysarthric speech simulation sample. */
interface DemoSample {
  id: string;
  label: string;
  /** Raw distorted utterance sent as the "transcript" to the backend. */
  rawText: string;
  /** Short plain-English description shown to the user. */
  description: string;
  /** Expected outcome badge text for judges. */
  expectedOutcome: string;
  /** Visual accent colour for this sample tile. */
  accentClass: string;
}

const DEMO_SAMPLES: DemoSample[] = [
  {
    id: "sample-water",
    label: "Sample 1",
    rawText: "i ned wtr",
    description: "\"I need some water\"",
    expectedOutcome: "High confidence proposal",
    accentClass: "border-green-300 dark:border-green-700 hover:border-green-500 focus-visible:ring-green-400",
  },
  {
    id: "sample-medicine",
    label: "Sample 2",
    rawText: "wer iz pil",
    description: "\"Where is my medicine?\"",
    expectedOutcome: "Medium confidence candidates",
    accentClass: "border-amber-300 dark:border-amber-700 hover:border-amber-500 focus-visible:ring-amber-400",
  },
  {
    id: "sample-low",
    label: "Sample 3",
    rawText: "uh ...",
    description: "Unintelligible input",
    expectedOutcome: "Safe low-confidence repeat",
    accentClass: "border-slate-300 dark:border-slate-600 hover:border-slate-500 focus-visible:ring-slate-400",
  },
  {
    id: "sample-memory",
    label: "Sample 4 — Memory Loop",
    rawText: "wer iz pil",
    description: "After correcting Sample 2 → instant recall",
    expectedOutcome: "Memory personalisation",
    accentClass: "border-indigo-300 dark:border-indigo-700 hover:border-indigo-500 focus-visible:ring-indigo-400",
  },
];

interface DemoBarProps {
  /** Called when the user picks a demo sample. Provides the raw distorted text. */
  onSimulate: (rawText: string) => void;
  /** Disable buttons while the speech pipeline is active. */
  disabled?: boolean;
}

/**
 * DemoBar — an accessible, toggleable panel that lets judges and evaluators
 * trigger pre-set dysarthric speech simulation samples without requiring a
 * microphone or live AssemblyAI credentials.
 *
 * Zero audio is captured or stored. The component bypasses the WebSocket audio
 * pipeline and directly emits a simulated transcript event via `onSimulate`.
 */
export function DemoBar({ onSimulate, disabled = false }: DemoBarProps) {
  const [expanded, setExpanded] = useState(false);
  const [activeSampleId, setActiveSampleId] = useState<string | null>(null);

  const handleSample = (sample: DemoSample) => {
    setActiveSampleId(sample.id);
    onSimulate(sample.rawText);
    // Clear the active highlight after a short delay for visual feedback
    setTimeout(() => setActiveSampleId(null), 1200);
  };

  return (
    <section
      aria-label="Interactive demo mode"
      className="w-full rounded-2xl border border-indigo-200 dark:border-indigo-800 bg-indigo-50/50 dark:bg-indigo-950/20 overflow-hidden"
    >
      {/* Toggle trigger */}
      <button
        id="demo-bar-toggle"
        type="button"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
        aria-controls="demo-bar-content"
        className="w-full flex items-center justify-between px-5 py-3.5 text-left hover:bg-indigo-100/60 dark:hover:bg-indigo-900/30 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-indigo-500"
      >
        <div className="flex items-center gap-2.5">
          <FlaskConical
            className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0"
            aria-hidden="true"
          />
          <span className="text-sm font-semibold text-indigo-800 dark:text-indigo-300">
            Demo Mode — No Microphone Required
          </span>
          <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-200/70 dark:bg-indigo-800/60 text-indigo-700 dark:text-indigo-300">
            <Zap className="w-3 h-3" aria-hidden="true" />
            Interactive
          </span>
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-indigo-500 shrink-0" aria-hidden="true" />
        ) : (
          <ChevronDown className="w-4 h-4 text-indigo-500 shrink-0" aria-hidden="true" />
        )}
      </button>

      {/* Expandable sample grid */}
      {expanded && (
        <div
          id="demo-bar-content"
          className="px-5 pb-5 pt-2 space-y-4"
        >
          <p className="text-xs text-indigo-700 dark:text-indigo-400 leading-relaxed">
            Click a sample below to simulate a dysarthric speech input through the full
            PEEXH agent pipeline — interpretation, scoring, and confirmation — without
            requiring a microphone or live API credentials.
          </p>

          <div className="grid gap-3 sm:grid-cols-2">
            {DEMO_SAMPLES.map((sample) => {
              const isActive = activeSampleId === sample.id;
              return (
                <button
                  key={sample.id}
                  id={sample.id}
                  type="button"
                  onClick={() => handleSample(sample)}
                  disabled={disabled}
                  aria-label={`${sample.label}: simulate "${sample.rawText}" — ${sample.expectedOutcome}`}
                  className={`min-h-[72px] text-left p-4 rounded-xl border bg-white dark:bg-slate-800/80 shadow-sm
                    focus:outline-none focus-visible:ring-4 transition-all duration-200 cursor-pointer
                    disabled:opacity-50 disabled:cursor-not-allowed
                    ${sample.accentClass}
                    ${isActive ? "scale-[0.97] opacity-80" : "hover:shadow-md active:scale-[0.97]"}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="space-y-0.5">
                      <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                        {sample.label}
                      </p>
                      <p className="font-semibold text-sm text-foreground leading-snug">
                        {sample.description}
                      </p>
                      <p className="font-mono text-xs text-slate-400 dark:text-slate-500">
                        raw: &ldquo;{sample.rawText}&rdquo;
                      </p>
                    </div>
                    <span className="shrink-0 text-xs font-medium text-slate-500 dark:text-slate-400 text-right leading-tight max-w-[90px]">
                      {sample.expectedOutcome}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          <p className="text-xs text-indigo-600 dark:text-indigo-500">
            No audio is captured or stored during demo mode. All samples pass through
            the live PEEXH backend agent and LLM interpretation pipeline.
          </p>
        </div>
      )}
    </section>
  );
}
