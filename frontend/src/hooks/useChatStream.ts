import { useState, useCallback, useRef } from "react";
import { API_BASE_URL, Message, Citation, Artifact } from "../lib/api";

interface UseChatStreamOptions {
  onArtifactDetected?: (artifact: Artifact) => void;
}

export function useChatStream({ onArtifactDetected }: UseChatStreamOptions = {}) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async ({
      sessionId,
      message,
      mode = "default",
      provider = "ollama",
      onToken,
      onCitations,
      onComplete,
      onError,
    }: {
      sessionId: string;
      message: string;
      mode?: "default" | "ship30" | "artifact";
      provider?: "ollama" | "claude" | "openai";
      onToken: (token: string) => void;
      onCitations: (citations: Citation[]) => void;
      onComplete: () => void;
      onError: (err: string) => void;
    }) => {
      setIsStreaming(true);
      setStatusMessage("Searching Lenny's Podcast transcripts...");

      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            session_id: sessionId,
            message,
            mode,
            provider,
          }),
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error(`Server returned HTTP ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("Response body is not readable");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith("data: ")) continue;

            const dataStr = trimmed.replace("data: ", "").trim();
            if (dataStr === "[DONE]") {
              setStatusMessage(null);
              break;
            }

            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.type === "status") {
                setStatusMessage(parsed.content);
              } else if (parsed.type === "citations") {
                onCitations(parsed.citations);
                setStatusMessage(null);
              } else if (parsed.type === "token") {
                onToken(parsed.content);
              } else if (parsed.type === "artifact") {
                if (onArtifactDetected) {
                  onArtifactDetected(parsed.artifact);
                }
              } else if (parsed.type === "error") {
                onError(parsed.content);
              }
            } catch (err) {
              console.warn("Failed to parse SSE line:", dataStr);
            }
          }
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          onError(err.message || "Failed to stream message");
        }
      } finally {
        setIsStreaming(false);
        setStatusMessage(null);
        abortControllerRef.current = null;
        onComplete();
      }
    },
    [onArtifactDetected]
  );

  const abortStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  return {
    isStreaming,
    statusMessage,
    sendMessage,
    abortStream,
  };
}
