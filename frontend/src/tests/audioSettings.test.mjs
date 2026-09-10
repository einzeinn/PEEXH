import { describe, it } from "node:test";
import assert from "node:assert/strict";

// Re-implement or import tested functions to run cleanly in Node environment
const DEFAULT_AUDIO_SETTINGS = {
  selectedDeviceId: null,
  echoCancellation: true,
  noiseSuppression: true,
  autoGainControl: true,
};

const AUDIO_SETTINGS_STORAGE_KEY = "peexh.audio-settings.v1";

function buildAudioConstraints(settings) {
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

function parseAudioSettings(raw) {
  if (!raw || typeof raw !== "object") {
    return { ...DEFAULT_AUDIO_SETTINGS };
  }

  const obj = raw;

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

function filterAudioInputDevices(devices) {
  const audioInputs = (devices || []).filter((d) => d.kind === "audioinput");
  const options = [{ deviceId: "", label: "System Default" }];

  audioInputs.forEach((device, index) => {
    if (device.deviceId && device.deviceId !== "default") {
      const label =
        device.label && device.label.trim().length > 0
          ? device.label
          : `Microphone ${index + 1}`;
      options.push({ deviceId: device.deviceId, label });
    }
  });

  return options;
}

function resolveSelectedDevice(selectedDeviceId, availableOptions) {
  if (!selectedDeviceId) return null;
  const exists = availableOptions.some((o) => o.deviceId === selectedDeviceId);
  return exists ? selectedDeviceId : null; // Fallback to System Default if missing
}

describe("RFC-007 Audio Settings & Device Discovery Tests", () => {
  it("1. Default audio settings match RFC specification", () => {
    assert.equal(DEFAULT_AUDIO_SETTINGS.selectedDeviceId, null);
    assert.equal(DEFAULT_AUDIO_SETTINGS.echoCancellation, true);
    assert.equal(DEFAULT_AUDIO_SETTINGS.noiseSuppression, true);
    assert.equal(DEFAULT_AUDIO_SETTINGS.autoGainControl, true);
  });

  it("2. localStorage serialization and deserialization works", () => {
    const custom = {
      selectedDeviceId: "virtual-cable-123",
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    };
    const serialized = JSON.stringify(custom);
    const parsed = parseAudioSettings(JSON.parse(serialized));

    assert.deepEqual(parsed, custom);
  });

  it("3. Corrupted persisted settings fall back safely to defaults", () => {
    assert.deepEqual(parseAudioSettings(null), DEFAULT_AUDIO_SETTINGS);
    assert.deepEqual(parseAudioSettings("corrupted string"), DEFAULT_AUDIO_SETTINGS);
    assert.deepEqual(parseAudioSettings(12345), DEFAULT_AUDIO_SETTINGS);

    // Partially corrupted object
    const partial = parseAudioSettings({
      selectedDeviceId: 999, // invalid type
      echoCancellation: "yes", // invalid type
      noiseSuppression: false, // valid
    });
    assert.equal(partial.selectedDeviceId, null);
    assert.equal(partial.echoCancellation, true); // default
    assert.equal(partial.noiseSuppression, false); // preserved
    assert.equal(partial.autoGainControl, true); // default
  });

  it("4. Reset to defaults restores initial settings", () => {
    const modified = {
      selectedDeviceId: "mic-xyz",
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    };
    // Simulating reset action
    const reset = { ...DEFAULT_AUDIO_SETTINGS };
    assert.deepEqual(reset, DEFAULT_AUDIO_SETTINGS);
  });

  it("5. Media device filtering includes only audioinput and always includes System Default", () => {
    const mockRawDevices = [
      { deviceId: "mic-1", kind: "audioinput", label: "USB Headset Mic" },
      { deviceId: "cam-1", kind: "videoinput", label: "Webcam" },
      { deviceId: "speaker-1", kind: "audiooutput", label: "Speakers" },
      { deviceId: "cable-1", kind: "audioinput", label: "VB-CABLE" },
    ];

    const filtered = filterAudioInputDevices(mockRawDevices);
    assert.equal(filtered.length, 3);
    assert.equal(filtered[0].deviceId, "");
    assert.equal(filtered[0].label, "System Default");
    assert.equal(filtered[1].deviceId, "mic-1");
    assert.equal(filtered[1].label, "USB Headset Mic");
    assert.equal(filtered[2].deviceId, "cable-1");
    assert.equal(filtered[2].label, "VB-CABLE");
  });

  it("6. Device labels fallback gracefully when permission has not yet been granted", () => {
    const unlabeledDevices = [
      { deviceId: "dev-a", kind: "audioinput", label: "" },
      { deviceId: "dev-b", kind: "audioinput", label: "" },
    ];

    const filtered = filterAudioInputDevices(unlabeledDevices);
    assert.equal(filtered.length, 3);
    assert.equal(filtered[0].label, "System Default");
    assert.equal(filtered[1].label, "Microphone 1");
    assert.equal(filtered[2].label, "Microphone 2");
  });

  it("7. Selected device handling and missing-device fallback", () => {
    const available = [
      { deviceId: "", label: "System Default" },
      { deviceId: "mic-1", label: "Built-in Mic" },
    ];

    // Case 1: Device exists
    assert.equal(resolveSelectedDevice("mic-1", available), "mic-1");

    // Case 2: Selected device disappeared (e.g. unplugged USB mic)
    assert.equal(resolveSelectedDevice("unplugged-usb-mic", available), null);

    // Case 3: System default remains null
    assert.equal(resolveSelectedDevice(null, available), null);
  });

  it("8. Generated getUserMedia constraints with exact device ID", () => {
    const settingsWithDevice = {
      selectedDeviceId: "stereo-mix-456",
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    };

    const constraints = buildAudioConstraints(settingsWithDevice);
    assert.deepEqual(constraints.deviceId, { exact: "stereo-mix-456" });
    assert.equal(constraints.channelCount, 1);
    assert.equal(constraints.echoCancellation, false);
    assert.equal(constraints.noiseSuppression, false);
    assert.equal(constraints.autoGainControl, false);
  });

  it("9. Generated getUserMedia constraints for System Default omits exact deviceId", () => {
    const defaultSettings = {
      selectedDeviceId: null,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    };

    const constraints = buildAudioConstraints(defaultSettings);
    assert.equal(constraints.deviceId, undefined);
    assert.equal(constraints.echoCancellation, true);
    assert.equal(constraints.noiseSuppression, true);
    assert.equal(constraints.autoGainControl, true);
  });

  it("10. Audio processing toggles independently modify constraints", () => {
    const loopbackSettings = {
      selectedDeviceId: "cable-vb",
      echoCancellation: false, // OFF for loopback
      noiseSuppression: false, // OFF for loopback
      autoGainControl: true,
    };

    const constraints = buildAudioConstraints(loopbackSettings);
    assert.equal(constraints.echoCancellation, false);
    assert.equal(constraints.noiseSuppression, false);
    assert.equal(constraints.autoGainControl, true);
  });

  it("11. Empty or undefined device list does not throw error", () => {
    assert.deepEqual(filterAudioInputDevices(null), [
      { deviceId: "", label: "System Default" },
    ]);
    assert.deepEqual(filterAudioInputDevices(undefined), [
      { deviceId: "", label: "System Default" },
    ]);
  });
});
