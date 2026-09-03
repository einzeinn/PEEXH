/**
 * Utilities for converting Web Audio Float32 samples into 16kHz 16-bit linear PCM.
 */

/**
 * Convert Float32Array (-1.0 to 1.0) to Int16Array (-32768 to 32767).
 */
export function floatToInt16(buffer: Float32Array): Int16Array {
  const l = buffer.length;
  const output = new Int16Array(l);
  for (let i = 0; i < l; i++) {
    const s = Math.max(-1, Math.min(1, buffer[i]));
    output[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return output;
}

/**
 * Resample Float32 audio buffer from input sample rate to target sample rate (default 16000 Hz)
 * and return as 16-bit Linear PCM Int16Array.
 */
export function downsampleTo16k(
  buffer: Float32Array,
  inputSampleRate: number,
  targetSampleRate: number = 16000
): Int16Array {
  if (targetSampleRate === inputSampleRate) {
    return floatToInt16(buffer);
  }

  const sampleRateRatio = inputSampleRate / targetSampleRate;
  const newLength = Math.round(buffer.length / sampleRateRatio);
  const result = new Int16Array(newLength);

  let offsetResult = 0;
  let offsetBuffer = 0;

  while (offsetResult < result.length) {
    const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
    let accum = 0;
    let count = 0;

    for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
      accum += buffer[i];
      count++;
    }

    const avg = count > 0 ? accum / count : 0;
    const s = Math.max(-1, Math.min(1, avg));
    result[offsetResult] = s < 0 ? s * 0x8000 : s * 0x7fff;

    offsetResult++;
    offsetBuffer = nextOffsetBuffer;
  }

  return result;
}
