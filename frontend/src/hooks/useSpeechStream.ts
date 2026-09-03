"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { downsampleTo16k } from "@/lib/audio/pcm";

export type StreamStatus = "idle" | "connecting" | "listening" | "stopping" | "error";

export type ConfidenceLevel = "HIGH" | "MEDIUM" | "LOW";

export type AgentAction =
  | "PROPOSE_PHRASE"
  | "SHOW_CANDIDATES"
  | "REQUEST_REPEAT"
  | "COMMUNICATE"
  | "LEARN_CORRECTION";

export interface PhraseCandidate {
  text: string;
  confidence: number;
  explanation?: string;
}

export interface AgentDecision {
  type: "agent_decision";
  action: AgentAction;
  confidence_level: ConfidenceLevel;
  overall_confidence: number;
  primary_phrase: string | null;
  candidates: PhraseCandidate[];
  reason: string;
}

export interface SpeechStreamState {
  status: StreamStatus;
  partialTranscript: string;
  finalTranscript: string;
  confidence: number;
  error: string | null;
  sessionId: string | null;
  provider: string | null;
  agentDecision: AgentDecision | null;
}

export function useSpeechStream() {
  const [state, setState] = useState<SpeechStreamState>({
    status: "idle",
    partialTranscript: "",
    finalTranscript: "",
    confidence: 0,
    error: null,
    sessionId: null,
    provider: null,
    agentDecision: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);

  const cleanupAudio = useCallback(() => {
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
  }, []);

  const stopRecording = useCallback(() => {
    setState((prev) => ({ ...prev, status: "stopping" }));

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "stop" }));
    }

    cleanupAudio();
  }, [cleanupAudio]);

  const startRecording = useCallback(async () => {
    setState({
      status: "connecting",
      partialTranscript: "",
      finalTranscript: "",
      confidence: 0,
      error: null,
      sessionId: null,
      provider: null,
      agentDecision: null,
    });

    try {
      // 1. Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;

      // 2. Determine WebSocket URL
      const apiBaseUrl =
        process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const wsUrl = `${apiBaseUrl.replace(/^http/, "ws")}/ws/speech`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        // Send start command
        ws.send(JSON.stringify({ type: "start", sample_rate: 16000 }));

        // Setup AudioContext
        const AudioContextClass =
          window.AudioContext ||
          (window as unknown as { webkitAudioContext: typeof AudioContext })
            .webkitAudioContext;
        const audioCtx = new AudioContextClass();
        audioContextRef.current = audioCtx;

        const source = audioCtx.createMediaStreamSource(stream);
        sourceRef.current = source;

        // Use ScriptProcessorNode for wide browser compatibility
        const bufferSize = 4096;
        const processor = audioCtx.createScriptProcessor(bufferSize, 1, 1);
        processorRef.current = processor;

        processor.onaudioprocess = (e) => {
          if (ws.readyState !== WebSocket.OPEN) return;
          const inputData = e.inputBuffer.getChannelData(0);
          const pcm16 = downsampleTo16k(inputData, audioCtx.sampleRate, 16000);
          ws.send(pcm16.buffer);
        };

        source.connect(processor);
        processor.connect(audioCtx.destination);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === "session_started") {
            setState((prev) => ({
              ...prev,
              status: "listening",
              sessionId: data.session_id,
              provider: data.provider,
            }));
          } else if (data.type === "transcript") {
            if (data.is_final) {
              setState((prev) => ({
                ...prev,
                finalTranscript: data.text,
                partialTranscript: "",
                confidence: data.confidence || 0,
              }));
            } else {
              setState((prev) => ({
                ...prev,
                partialTranscript: data.text,
              }));
            }
          } else if (data.type === "speech_stopped") {
            setState((prev) => ({
              ...prev,
              status: "idle",
            }));
          } else if (data.type === "agent_decision") {
            setState((prev) => ({
              ...prev,
              agentDecision: data,
            }));
            // After receiving decision, close connection cleanly
            if (wsRef.current) {
              wsRef.current.close();
              wsRef.current = null;
            }
          } else if (data.type === "error") {
            setState((prev) => ({
              ...prev,
              status: "error",
              error: data.message || "Speech transcription error",
            }));
            cleanupAudio();
          }
        } catch (err) {
          console.error("Error parsing WebSocket message:", err);
        }
      };

      ws.onerror = () => {
        setState((prev) => ({
          ...prev,
          status: "error",
          error: "WebSocket connection error. Is the backend running?",
        }));
        cleanupAudio();
      };

      ws.onclose = () => {
        setState((prev) => {
          if (prev.status !== "error") {
            return { ...prev, status: "idle" };
          }
          return prev;
        });
        cleanupAudio();
      };
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Microphone access denied or unavailable";
      setState((prev) => ({
        ...prev,
        status: "error",
        error: message,
      }));
      cleanupAudio();
    }
  }, [cleanupAudio]);

  useEffect(() => {
    return () => {
      cleanupAudio();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [cleanupAudio]);

  return {
    ...state,
    startRecording,
    stopRecording,
  };
}
