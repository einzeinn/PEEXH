/**
 * Types and defaults for runtime audio input settings and device discovery.
 */

export interface AudioSettings {
  /** Specific MediaDeviceInfo deviceId, or null for system default */
  selectedDeviceId: string | null;
  /** Browser acoustic echo cancellation */
  echoCancellation: boolean;
  /** Browser background noise suppression */
  noiseSuppression: boolean;
  /** Browser automatic input gain leveling */
  autoGainControl: boolean;
}

export const DEFAULT_AUDIO_SETTINGS: AudioSettings = {
  selectedDeviceId: null,
  echoCancellation: true,
  noiseSuppression: true,
  autoGainControl: true,
};

export const AUDIO_SETTINGS_STORAGE_KEY = "peexh.audio-settings.v1";

export interface AudioDeviceOption {
  deviceId: string;
  label: string;
}

/**
 * Construct MediaTrackConstraints from AudioSettings.
 */
export function buildAudioConstraints(settings: AudioSettings): MediaTrackConstraints {
  return {
    deviceId: settings.selectedDeviceId
      ? { exact: settings.selectedDeviceId }
      : undefined,
    channelCount: 1,
    echoCancellation: settings.echoCancellation,
    noiseSuppression: settings.noiseSuppression,
    autoGainControl: settings.autoGainControl,
  };
}

/**
 * Validate and sanitize an unknown object into AudioSettings.
 * Falls back to DEFAULT_AUDIO_SETTINGS on corruption.
 */
export function parseAudioSettings(raw: unknown): AudioSettings {
  if (!raw || typeof raw !== "object") {
    return { ...DEFAULT_AUDIO_SETTINGS };
  }

  const obj = raw as Record<string, unknown>;

  const selectedDeviceId =
    typeof obj.selectedDeviceId === "string" && obj.selectedDeviceId.trim().length > 0
      ? obj.selectedDeviceId.trim()
      : null;

  const echoCancellation =
    typeof obj.echoCancellation === "boolean"
      ? obj.echoCancellation
      : DEFAULT_AUDIO_SETTINGS.echoCancellation;

  const noiseSuppression =
    typeof obj.noiseSuppression === "boolean"
      ? obj.noiseSuppression
      : DEFAULT_AUDIO_SETTINGS.noiseSuppression;

  const autoGainControl =
    typeof obj.autoGainControl === "boolean"
      ? obj.autoGainControl
      : DEFAULT_AUDIO_SETTINGS.autoGainControl;

  return {
    selectedDeviceId,
    echoCancellation,
    noiseSuppression,
    autoGainControl,
  };
}
