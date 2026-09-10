"use client";

import { useState, useEffect, useCallback } from "react";
import { AudioDeviceOption } from "@/types/audioSettings";
import { useAudioSettings } from "@/context/AudioSettingsContext";

export type PermissionState = "granted" | "prompt" | "denied" | "unavailable";

export function useAudioDevices() {
  const { settings, updateSettings } = useAudioSettings();
  const [devices, setDevices] = useState<AudioDeviceOption[]>([
    { deviceId: "", label: "System Default" },
  ]);
  const [permissionState, setPermissionState] = useState<PermissionState>("prompt");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check microphone permission state via Permissions API if available
  const checkPermission = useCallback(async () => {
    if (typeof navigator === "undefined" || !navigator.permissions) {
      setPermissionState("unavailable");
      return;
    }

    try {
      // Note: 'microphone' permission name may throw on some browsers (e.g. Safari / Firefox)
      const status = await navigator.permissions.query({
        name: "microphone" as PermissionName,
      });
      setPermissionState(status.state as PermissionState);

      status.onchange = () => {
        setPermissionState(status.state as PermissionState);
        refreshDevices();
      };
    } catch {
      // Permissions API query for microphone not supported in this browser
      setPermissionState("unavailable");
    }
  }, []);

  // Enumerate audio input devices
  const refreshDevices = useCallback(async () => {
    if (
      typeof navigator === "undefined" ||
      !navigator.mediaDevices ||
      !navigator.mediaDevices.enumerateDevices
    ) {
      setError("MediaDevices API is not supported in this browser");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const allDevices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = allDevices.filter((d) => d.kind === "audioinput");

      const options: AudioDeviceOption[] = [
        { deviceId: "", label: "System Default" },
      ];

      audioInputs.forEach((device, index) => {
        // Only add non-default specific device IDs to avoid duplicating the default entry
        if (device.deviceId && device.deviceId !== "default") {
          const label =
            device.label && device.label.trim().length > 0
              ? device.label
              : `Microphone ${index + 1}`;

          options.push({
            deviceId: device.deviceId,
            label,
          });
        }
      });

      setDevices(options);

      // Verify currently selected device still exists
      if (settings.selectedDeviceId) {
        const exists = options.some(
          (o) => o.deviceId === settings.selectedDeviceId
        );
        if (!exists) {
          // Device disconnected; fall back gracefully to system default
          updateSettings({ selectedDeviceId: null });
        }
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to enumerate audio devices"
      );
    } finally {
      setIsLoading(false);
    }
  }, [settings.selectedDeviceId, updateSettings]);

  useEffect(() => {
    checkPermission();
    refreshDevices();

    if (
      typeof navigator !== "undefined" &&
      navigator.mediaDevices &&
      navigator.mediaDevices.addEventListener
    ) {
      const handler = () => {
        refreshDevices();
      };
      navigator.mediaDevices.addEventListener("devicechange", handler);
      return () => {
        navigator.mediaDevices.removeEventListener("devicechange", handler);
      };
    }
  }, [checkPermission, refreshDevices]);

  return {
    devices,
    permissionState,
    isLoading,
    error,
    refreshDevices,
  };
}
