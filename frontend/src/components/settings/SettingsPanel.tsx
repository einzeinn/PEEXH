"use client";

import React, { useEffect, useRef, useState } from "react";
import { X, RotateCcw, Check, AlertCircle, CheckCircle2 } from "lucide-react";
import { useAudioSettings } from "@/context/AudioSettingsContext";
import { useAudioDevices } from "@/hooks/useAudioDevices";
import { AudioInputMeter } from "@/components/settings/AudioInputMeter";

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  activeProvider?: string | null;
}

export function SettingsPanel({
  isOpen,
  onClose,
  activeProvider,
}: SettingsPanelProps) {
  const { settings, updateSettings, resetToDefaults } = useAudioSettings();
  const { devices, permissionState, isLoading: devicesLoading } = useAudioDevices();

  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [backendEnv, setBackendEnv] = useState<string>("");

  const modalRef = useRef<HTMLDivElement | null>(null);

  // Check backend health
  useEffect(() => {
    if (!isOpen) return;

    let mounted = true;
    setBackendStatus("checking");

    const checkHealth = async () => {
      try {
        const apiBaseUrl =
          process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
        const res = await fetch(`${apiBaseUrl}/health`, { cache: "no-store" });
        if (res.ok) {
          const data = await res.json();
          if (mounted) {
            setBackendStatus("online");
            setBackendEnv(data.environment || "development");
          }
        } else {
          if (mounted) setBackendStatus("offline");
        }
      } catch {
        if (mounted) setBackendStatus("offline");
      }
    };

    checkHealth();

    return () => {
      mounted = false;
    };
  }, [isOpen]);

  // Handle ESC key to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Trap focus inside modal
  useEffect(() => {
    if (isOpen && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-150"
      role="presentation"
    >
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="settings-dialog-title"
        tabIndex={-1}
        className="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl bg-surface border border-surface-border p-6 shadow-2xl space-y-6 focus:outline-none"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-surface-border pb-4">
          <div>
            <h2
              id="settings-dialog-title"
              className="text-lg font-bold text-foreground tracking-tight"
            >
              Audio & Runtime Settings
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Configure microphone input, acoustic preprocessing, and diagnostics.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-slate-400 hover:text-foreground hover:bg-surface-muted transition-colors focus:outline-none focus:ring-2 focus:ring-primary min-w-[48px] min-h-[48px] flex items-center justify-center"
            aria-label="Close Settings"
          >
            <X className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>

        {/* 1. Audio Input Device */}
        <section aria-labelledby="heading-device" className="space-y-2">
          <label
            id="heading-device"
            htmlFor="audio-device-select"
            className="block text-xs font-semibold uppercase tracking-wider text-foreground"
          >
            Audio Input Device
          </label>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Select physical microphone, headset, or loopback (Stereo Mix / VB-CABLE).
          </p>
          <select
            id="audio-device-select"
            value={settings.selectedDeviceId ?? ""}
            disabled={devicesLoading}
            onChange={(e) => {
              const val = e.target.value;
              updateSettings({ selectedDeviceId: val === "" ? null : val });
            }}
            className="w-full px-3.5 py-2.5 rounded-lg border border-surface-border bg-surface text-foreground font-medium text-sm focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
          >
            {devices.map((d) => (
              <option key={d.deviceId || "default"} value={d.deviceId}>
                {d.label}
              </option>
            ))}
          </select>
        </section>

        {/* 2. Input Preprocessing Toggles */}
        <section aria-labelledby="heading-preprocessing" className="space-y-3">
          <div>
            <h3
              id="heading-preprocessing"
              className="text-xs font-semibold uppercase tracking-wider text-foreground"
            >
              Input Preprocessing
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Disable preprocessing when using loopback/virtual audio cables for testing.
            </p>
          </div>

          <div className="space-y-2">
            {/* Echo Cancellation */}
            <label className="flex items-center justify-between p-3 rounded-lg border border-surface-border bg-surface hover:bg-surface-muted/30 transition-colors cursor-pointer min-h-[48px]">
              <div>
                <span className="text-sm font-medium text-foreground block">
                  Echo Cancellation
                </span>
                <span className="text-xs text-slate-500">
                  Prevents speaker feedback
                </span>
              </div>
              <input
                type="checkbox"
                checked={settings.echoCancellation}
                onChange={(e) =>
                  updateSettings({ echoCancellation: e.target.checked })
                }
                className="w-5 h-5 rounded border-slate-300 text-primary focus:ring-primary cursor-pointer accent-primary"
                aria-label="Toggle Echo Cancellation"
              />
            </label>

            {/* Noise Suppression */}
            <label className="flex items-center justify-between p-3 rounded-lg border border-surface-border bg-surface hover:bg-surface-muted/30 transition-colors cursor-pointer min-h-[48px]">
              <div>
                <span className="text-sm font-medium text-foreground block">
                  Noise Suppression
                </span>
                <span className="text-xs text-slate-500">
                  Filters ambient background noise
                </span>
              </div>
              <input
                type="checkbox"
                checked={settings.noiseSuppression}
                onChange={(e) =>
                  updateSettings({ noiseSuppression: e.target.checked })
                }
                className="w-5 h-5 rounded border-slate-300 text-primary focus:ring-primary cursor-pointer accent-primary"
                aria-label="Toggle Noise Suppression"
              />
            </label>

            {/* Auto Gain Control */}
            <label className="flex items-center justify-between p-3 rounded-lg border border-surface-border bg-surface hover:bg-surface-muted/30 transition-colors cursor-pointer min-h-[48px]">
              <div>
                <span className="text-sm font-medium text-foreground block">
                  Auto Gain Control
                </span>
                <span className="text-xs text-slate-500">
                  Automatically adjusts mic volume
                </span>
              </div>
              <input
                type="checkbox"
                checked={settings.autoGainControl}
                onChange={(e) =>
                  updateSettings({ autoGainControl: e.target.checked })
                }
                className="w-5 h-5 rounded border-slate-300 text-primary focus:ring-primary cursor-pointer accent-primary"
                aria-label="Toggle Auto Gain Control"
              />
            </label>
          </div>
        </section>

        {/* 3. Audio Input Level Diagnostic */}
        <section aria-label="Input level diagnostic">
          <AudioInputMeter />
        </section>

        {/* 4. Diagnostics Overview */}
        <section aria-labelledby="heading-diagnostics" className="space-y-2">
          <h3
            id="heading-diagnostics"
            className="text-xs font-semibold uppercase tracking-wider text-foreground"
          >
            System Diagnostics
          </h3>
          <div className="rounded-lg border border-surface-border bg-surface-muted/20 p-3 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Microphone Permission:</span>
              <span className="font-medium text-foreground capitalize">
                {permissionState}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">PEEXH Stream Target:</span>
              <span className="font-mono text-foreground">16,000 Hz (16-bit PCM)</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Backend Connectivity:</span>
              <span className="flex items-center gap-1 font-medium">
                {backendStatus === "online" && (
                  <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Online ({backendEnv})
                  </span>
                )}
                {backendStatus === "offline" && (
                  <span className="text-amber-600 dark:text-amber-400 flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" /> Offline
                  </span>
                )}
                {backendStatus === "checking" && (
                  <span className="text-slate-400">Checking...</span>
                )}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Active Speech Provider:</span>
              <span className="font-mono text-foreground">
                {activeProvider ?? "Not started"}
              </span>
            </div>
          </div>
        </section>

        {/* Footer Actions */}
        <div className="flex items-center justify-between border-t border-surface-border pt-4">
          <button
            type="button"
            onClick={resetToDefaults}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:text-foreground hover:bg-surface-muted rounded-lg border border-surface-border transition-colors min-h-[48px]"
            aria-label="Reset all audio settings to default"
          >
            <RotateCcw className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Reset to Defaults</span>
          </button>

          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center gap-1.5 px-5 py-2.5 text-xs font-semibold text-white bg-primary hover:bg-primary/90 rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
          >
            <Check className="w-4 h-4" aria-hidden="true" />
            <span>Done</span>
          </button>
        </div>
      </div>
    </div>
  );
}
