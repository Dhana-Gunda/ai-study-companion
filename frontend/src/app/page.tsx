"use client";

import React, { useState, useEffect } from "react";
import { Plus, MessageSquare, Trash2, Sidebar as SidebarIcon, Sparkles, Database } from "lucide-react";
import { ChatPane } from "../components/Chat/ChatPane";
import { ModelSelector } from "../components/Chat/ModelSelector";
import { ArtifactViewer } from "../components/Artifact/ArtifactViewer";
import { useChatStream } from "../hooks/useChatStream";
import {
  Session,
  Message,
  Artifact,
  Citation,
  fetchSessions,
  createNewSession,
  fetchSessionDetails,
  deleteSession,
  fetchHealth,
  HealthData,
} from "../lib/api";

export default function Home() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<"ollama" | "claude" | "openai">("ollama");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [health, setHealth] = useState<HealthData | null>(null);

  // Hook for SSE streaming
  const { isStreaming, statusMessage, sendMessage, abortStream } = useChatStream({
    onArtifactDetected: (artifact) => {
      setActiveArtifact(artifact);
    },
  });

  // Load health and sessions on mount
  useEffect(() => {
    async function loadInitialData() {
      try {
        const h = await fetchHealth();
        setHealth(h);
      } catch (err) {
        console.warn("Could not reach backend health probe:", err);
      }

      try {
        const list = await fetchSessions();
        setSessions(list);
        if (list.length > 0) {
          handleSelectSession(list[0].id);
        } else {
          handleNewSession();
        }
      } catch (err) {
        // Initialize default session if DB is empty
        handleNewSession();
      }
    }
    loadInitialData();
  }, []);

  const handleSelectSession = async (sessionId: string) => {
    setCurrentSessionId(sessionId);
    try {
      const details = await fetchSessionDetails(sessionId);
      setMessages(details.messages || []);
      // If last message has an artifact, set it active
      for (const m of (details.messages || []).slice().reverse()) {
        if (m.artifacts && m.artifacts.length > 0) {
          setActiveArtifact(m.artifacts[0]);
          break;
        }
      }
    } catch (err) {
      console.error("Failed to load session details:", err);
    }
  };

  const handleNewSession = async () => {
    try {
      const newSess = await createNewSession("New Conversation");
      setSessions((prev) => [newSess, ...prev]);
      setCurrentSessionId(newSess.id);
      setMessages([]);
      setActiveArtifact(null);
    } catch (err) {
      // Offline fallback UUID
      const fakeId = "session-" + Date.now();
      setCurrentSessionId(fakeId);
      setMessages([]);
      setActiveArtifact(null);
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (currentSessionId === id) {
        const remaining = sessions.filter((s) => s.id !== id);
        if (remaining.length > 0) {
          handleSelectSession(remaining[0].id);
        } else {
          handleNewSession();
        }
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
    }
  };

  const handleSendMessage = (text: string, mode: "default" | "ship30" | "artifact") => {
    if (!currentSessionId) return;

    // 1. Append user message optimistically
    const userMsg: Message = {
      role: "user",
      content: text,
    };

    // 2. Prepare placeholder assistant message
    const placeholderAssistant: Message = {
      role: "assistant",
      content: "",
      sources: [],
      artifacts: [],
    };

    setMessages((prev) => [...prev, userMsg, placeholderAssistant]);

    let accumulatedTokens = "";
    let capturedCitations: Citation[] = [];

    sendMessage({
      sessionId: currentSessionId,
      message: text,
      mode,
      provider: selectedProvider,
      onToken: (token) => {
        accumulatedTokens += token;
        setMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: accumulatedTokens,
              sources: capturedCitations,
            };
          }
          return updated;
        });
      },
      onCitations: (citations) => {
        capturedCitations = citations;
        setMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
            updated[lastIdx] = {
              ...updated[lastIdx],
              sources: citations,
            };
          }
          return updated;
        });
      },
      onComplete: () => {
        // Refresh session list title if needed
        fetchSessions().then(setSessions).catch(() => {});
      },
      onError: (errText) => {
        setMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: updated[lastIdx].content + `\n\n> [!WARNING]\n> **Error**: ${errText}`,
            };
          }
          return updated;
        });
      },
    });
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-zinc-950 text-zinc-100 overflow-hidden select-none">
      {/* Top Navbar */}
      <header className="h-14 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur px-4 flex items-center justify-between shrink-0 z-10">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition"
            title="Toggle Sidebar"
          >
            <SidebarIcon className="w-5 h-5" />
          </button>
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-sm">
              L
            </div>
            <span className="font-semibold text-sm tracking-tight text-zinc-100 hidden sm:inline">
              The Lenny Growth Assistant
            </span>
          </div>
        </div>

        {/* Center/Right: Model Selector & Health status */}
        <div className="flex items-center space-x-3">
          {health && (
            <div className="hidden md:flex items-center space-x-1.5 text-[11px] text-zinc-400 bg-zinc-900 border border-zinc-800 px-2.5 py-1 rounded-md">
              <Database className="w-3 h-3 text-emerald-400" />
              <span>{health.indexed_chunks} chunks indexed</span>
            </div>
          )}

          <ModelSelector
            currentProvider={selectedProvider}
            onProviderChange={setSelectedProvider}
            disabled={isStreaming}
          />
        </div>
      </header>

      {/* Main 3-Pane Body */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar */}
        <nav
          aria-label="Chat sessions"
          className={`${
            isSidebarOpen ? "w-64" : "w-0 -ml-64"
          } transition-all duration-200 border-r border-zinc-800 bg-zinc-950 flex flex-col shrink-0 overflow-hidden z-20`}
        >
          <div className="p-3 border-b border-zinc-800/80">
            <button
              onClick={handleNewSession}
              className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold py-2 px-3 rounded-lg transition shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>New Conversation</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            <div className="px-2 py-1 text-[11px] font-medium text-zinc-500 uppercase tracking-wider">
              Recent Sessions
            </div>
            {sessions.map((sess) => (
              <div
                key={sess.id}
                onClick={() => handleSelectSession(sess.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-lg text-xs cursor-pointer transition ${
                  currentSessionId === sess.id
                    ? "bg-zinc-800/90 text-white font-medium border border-zinc-700/50"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
                }`}
              >
                <div className="flex items-center space-x-2 truncate">
                  <MessageSquare className="w-3.5 h-3.5 shrink-0 text-zinc-500 group-hover:text-indigo-400" />
                  <span className="truncate">{sess.title}</span>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(e, sess.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 text-zinc-500 hover:text-rose-400 rounded transition"
                  title="Delete conversation"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          {/* Sidebar Footer */}
          <div className="p-3 border-t border-zinc-800/80 bg-zinc-950/50 text-[11px] text-zinc-500 flex items-center justify-between">
            <span>Lenny Assistant v1.0</span>
            <span className="flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>Online</span>
            </span>
          </div>
        </nav>

        {/* Center Chat Pane */}
        <main className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
          <ChatPane
            messages={messages}
            isStreaming={isStreaming}
            statusMessage={statusMessage}
            onSendMessage={handleSendMessage}
            onStopStreaming={abortStream}
            onOpenArtifact={(art) => setActiveArtifact(art)}
          />
        </main>

        {/* Right Artifact Viewer (Claude Artifacts style) */}
        {activeArtifact && (
          <div className="w-full md:w-[48%] lg:w-[50%] h-full shrink-0 z-10">
            <ArtifactViewer
              artifact={activeArtifact}
              onClose={() => setActiveArtifact(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
}
