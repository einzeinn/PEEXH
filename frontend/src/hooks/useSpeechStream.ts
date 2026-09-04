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

export type ConfirmedPhraseSource = "proposal" | "candidate" | "correction";

export type ConfirmationStatus =
  | "idle"
  | "awaiting"
  | "pending"
  | "confirmed"
  | "repeat_requested";

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

export interface CommunicationReadyEvent {
  type: "communication_ready";
  phrase: string;
  source: ConfirmedPhraseSource;
}

export interface RepeatRequestedEvent {
  type: "repeat_requested";
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
  confirmationStatus: ConfirmationStatus;
  confirmedPhrase: string | null;
  confirmedSource: ConfirmedPhraseSource | null;
  confirmPending: boolean;
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
    confirmationStatus: "idle",
    confirmedPhrase: null,
    confirmedSource: null,
    confirmPending: false,
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

  const confirmProposal = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setState((prev) => ({ ...prev, confirmPending: true, error: null }));
      wsRef.current.send(JSON.stringify({ type: "confirm_proposal" }));
    }
  }, []);

  const selectCandidate = useCallback((phrase: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setState((prev) => ({ ...prev, confirmPending: true, error: null }));
      wsRef.current.send(JSON.stringify({ type: "select_candidate", phrase }));
    }
  }, []);

  const submitCorrection = useCallback((phrase: string) => {
    const trimmed = phrase.trim();
    if (!trimmed) return;
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setState((prev) => ({ ...prev, confirmPending: true, error: null }));
      wsRef.current.send(JSON.stringify({ type: "submit_correction", phrase: trimmed }));
    }
  }, []);

  const requestRepeat = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setState((prev) => ({ ...prev, confirmPending: true, error: null }));
      wsRef.current.send(JSON.stringify({ type: "request_repeat" }));
    }
  }, []);

  const resetConfirmation = useCallback(() => {
    setState((prev) => ({
      ...prev,
      confirmationStatus: "idle",
      confirmedPhrase: null,
      confirmedSource: null,
      agentDecision: null,
      confirmPending: false,
    }));
  }, []);

  const startRecording = useCallback(async () => {
    // Clean up any existing connection before starting fresh session
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    cleanupAudio();

    setState({
      status: "connecting",
      partialTranscript: "",
      finalTranscript: "",
      confidence: 0,
      error: null,
      sessionId: null,
      provider: null,
      agentDecision: null,
      confirmationStatus: "idle",
      confirmedPhrase: null,
      confirmedSource: null,
      confirmPending: false,
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
              confirmationStatus: "awaiting",
              confirmPending: false,
            }));
            // Keep WebSocket connection open for user confirmation action (RFC-004)
          } else if (data.type === "communication_ready") {
            setState((prev) => ({
              ...prev,
              confirmationStatus: "confirmed",
              confirmedPhrase: data.phrase,
              confirmedSource: data.source,
              confirmPending: false,
            }));
          } else if (data.type === "repeat_requested") {
            setState((prev) => ({
              ...prev,
              confirmationStatus: "repeat_requested",
              agentDecision: null,
              confirmPending: false,
            }));
          } else if (data.type === "error") {
            setState((prev) => ({
              ...prev,
              status: prev.status === "connecting" ? "error" : prev.status,
              error: data.message || "Speech transcription error",
              confirmPending: false,
            }));
            if (prevStatusNeedsCleanup(data.code)) {
              cleanupAudio();
            }
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
          confirmPending: false,
        }));
        cleanupAudio();
      };

      ws.onclose = () => {
        setState((prev) => {
          if (prev.status !== "error") {
            return { ...prev, status: "idle", confirmPending: false };
          }
          return { ...prev, confirmPending: false };
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
        confirmPending: false,
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
    confirmProposal,
    selectCandidate,
    submitCorrection,
    requestRepeat,
    resetConfirmation,
  };
}

function prevStatusNeedsCleanup(code?: string): boolean {
  // If it's a confirmation error, we keep audio/ws intact
  return code !== "INVALID_AGENT_STATE" && code !== "INVALID_CONTROL_MESSAGE";
}
