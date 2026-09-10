"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Mic, MicOff, AlertCircle } from "lucide-react";
import { useAudioSettings } from "@/context/AudioSettingsContext";
import { buildAudioConstraints } from "@/types/audioSettings";

export function AudioInputMeter() {
  const { settings } = useAudioSettings();
  const [isTesting, setIsTesting] = useState<boolean>(false);
  const [volumeLevel, setVolumeLevel] = useState<number>(0); // 0 to 100
  const [hardwareSampleRate, setHardwareSampleRate] = useState<number | null>(null);
  const [meterError, setMeterError] = useState<string | null>(null);

  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animFrameRef = useRef<number | null>(null);

  const stopTesting = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    setIsTesting(false);
    setVolumeLevel(0);
  }, []);

  const startTesting = useCallback(async () => {
    stopTesting();
    setMeterError(null);

    try {
      const constraints = buildAudioConstraints(settings);
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: constraints,
      });
      streamRef.current = stream;

      const AudioContextClass =
        window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext })
          .webkitAudioContext;
      const audioCtx = new AudioContextClass();
      audioContextRef.current = audioCtx;
      setHardwareSampleRate(audioCtx.sampleRate);

      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.5;
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const updateMeter = () => {
        analyser.getByteFrequencyData(dataArray);

        // Compute root-mean-square (RMS) level
        let sumSquares = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sumSquares += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sumSquares / dataArray.length);
        // Normalize 0-255 byte level to 0-100 percentage
        const normalized = Math.min(100, Math.round((rms / 128) * 100));
        setVolumeLevel(normalized);

        animFrameRef.current = requestAnimationFrame(updateMeter);
      };

      setIsTesting(true);
      updateMeter();
    } catch (err) {
      setMeterError(
        err instanceof Error ? err.message : "Failed to access audio input device"
      );
      stopTesting();
    }
  }, [settings, stopTesting]);

  // Clean up on unmount or settings change
  useEffect(() => {
    return () => {
      stopTesting();
    };
  }, [stopTesting]);

  return (
    <div className="space-y-3 rounded-lg border border-surface-border bg-surface-muted/40 p-3.5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground">
            Audio Input Meter
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Realtime volume test. No audio data is recorded.
          </p>
        </div>
        <button
          type="button"
          onClick={isTesting ? stopTesting : startTesting}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md border transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 min-h-[44px] ${
            isTesting
              ? "border-red-500 bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300"
              : "border-surface-border bg-surface hover:bg-surface-muted text-foreground"
          }`}
          aria-label={isTesting ? "Stop testing input" : "Start testing input"}
        >
          {isTesting ? (
            <>
              <MicOff className="w-3.5 h-3.5 text-red-500" aria-hidden="true" />
              <span>Stop Test</span>
            </>
          ) : (
            <>
              <Mic className="w-3.5 h-3.5 text-primary" aria-hidden="true" />
              <span>Test Input</span>
            </>
          )}
        </button>
      </div>

      {meterError && (
        <div
          role="alert"
          className="flex items-center gap-2 text-xs text-red-600 dark:text-red-400"
        >
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{meterError}</span>
        </div>
      )}

      {/* Progress meter bar */}
      <div className="space-y-1.5">
        <div
          role="progressbar"
          aria-valuenow={volumeLevel}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Microphone input volume level"
          className="h-3 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700 relative"
        >
          <div
            className={`h-full transition-all duration-75 rounded-full ${
              volumeLevel > 75
                ? "bg-amber-500"
                : volumeLevel > 20
                ? "bg-emerald-500"
                : "bg-primary"
            }`}
            style={{ width: `${volumeLevel}%` }}
          />
        </div>
        <div className="flex justify-between text-[11px] text-slate-400">
          <span>0%</span>
          <span className="font-mono text-foreground font-medium">
            {isTesting ? `${volumeLevel}%` : "Inactive"}
          </span>
          <span>100%</span>
        </div>
      </div>

      {hardwareSampleRate && (
        <div className="text-[11px] text-slate-500">
          Hardware sample rate:{" "}
          <strong className="font-mono text-foreground">
            {hardwareSampleRate.toLocaleString()} Hz
          </strong>
        </div>
      )}
    </div>
  );
}
