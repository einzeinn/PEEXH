"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
} from "react";
import {
  AudioSettings,
  DEFAULT_AUDIO_SETTINGS,
  AUDIO_SETTINGS_STORAGE_KEY,
  parseAudioSettings,
} from "@/types/audioSettings";

interface AudioSettingsContextValue {
  settings: AudioSettings;
  updateSettings: (partial: Partial<AudioSettings>) => void;
  resetToDefaults: () => void;
  isLoaded: boolean;
}

const AudioSettingsContext = createContext<AudioSettingsContextValue | undefined>(
  undefined
);

export function AudioSettingsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [settings, setSettings] = useState<AudioSettings>(DEFAULT_AUDIO_SETTINGS);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage safely after mount
  useEffect(() => {
    try {
      if (typeof window !== "undefined" && window.localStorage) {
        const stored = window.localStorage.getItem(AUDIO_SETTINGS_STORAGE_KEY);
        if (stored) {
          const parsed = JSON.parse(stored);
          setSettings(parseAudioSettings(parsed));
        }
      }
    } catch {
      // Corrupted storage or access denied; fallback to defaults
      setSettings(DEFAULT_AUDIO_SETTINGS);
    } finally {
      setIsLoaded(true);
    }
  }, []);

  // Update settings with local storage sync
  const updateSettings = useCallback((partial: Partial<AudioSettings>) => {
    setSettings((prev) => {
      const next = { ...prev, ...partial };
      try {
        if (typeof window !== "undefined" && window.localStorage) {
          window.localStorage.setItem(
            AUDIO_SETTINGS_STORAGE_KEY,
            JSON.stringify(next)
          );
        }
      } catch {
        // Ignore quota/private mode storage errors
      }
      return next;
    });
  }, []);

  // Reset to defaults action
  const resetToDefaults = useCallback(() => {
    setSettings(DEFAULT_AUDIO_SETTINGS);
    try {
      if (typeof window !== "undefined" && window.localStorage) {
        window.localStorage.removeItem(AUDIO_SETTINGS_STORAGE_KEY);
      }
    } catch {
      // Ignore storage errors
    }
  }, []);

  const value = useMemo(
    () => ({
      settings,
      updateSettings,
      resetToDefaults,
      isLoaded,
    }),
    [settings, updateSettings, resetToDefaults, isLoaded]
  );

  return (
    <AudioSettingsContext.Provider value={value}>
      {children}
    </AudioSettingsContext.Provider>
  );
}

export function useAudioSettings(): AudioSettingsContextValue {
  const ctx = useContext(AudioSettingsContext);
  if (!ctx) {
    // If used outside provider (e.g. in isolated components or tests), return defaults
    return {
      settings: DEFAULT_AUDIO_SETTINGS,
      updateSettings: () => {},
      resetToDefaults: () => {},
      isLoaded: true,
    };
  }
  return ctx;
}
