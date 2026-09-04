import React, { useState, useRef, useEffect } from "react";
import { Send, StopCircle, Sparkles, Feather, Code2 } from "lucide-react";
import { MessageItem } from "./MessageItem";
import { Message, Artifact } from "../../lib/api";

interface ChatPaneProps {
  messages: Message[];
  isStreaming: boolean;
  statusMessage: string | null;
  onSendMessage: (text: string, mode: "default" | "ship30" | "artifact") => void;
  onStopStreaming: () => void;
  onOpenArtifact: (artifact: Artifact) => void;
}

export const ChatPane: React.FC<ChatPaneProps> = ({
  messages,
  isStreaming,
  statusMessage,
  onSendMessage,
  onStopStreaming,
  onOpenArtifact,
}) => {
  const [input, setInput] = useState("");
  const [activeMode, setActiveMode] = useState<"default" | "ship30" | "artifact">("default");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, statusMessage, isStreaming]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim(), activeMode);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const suggestionPrompts = [
    {
      title: "Elena Verna on PLG Loops",
      query: "What does Elena Verna say about B2B Product-Led Growth, Product-Led Sales, and freemium retention?",
      mode: "default" as const,
    },
    {
      title: "Ship 30 for 30: Shreyas LNO Framework",
      query: "Write a Ship 30 for 30 essay on Shreyas Doshi's LNO Framework and Product Leadership.",
      mode: "ship30" as const,
    },
    {
      title: "Interactive PLG ROI Calculator (Artifact)",
      query: "Create an interactive HTML/CSS ROI calculator for PLG adoption and self-serve conversion.",
      mode: "artifact" as const,
    },
    {
      title: "Brian Chesky on Founder Mode",
      query: "What does Brian Chesky mean by 'Founder Mode' and how did Airbnb redesign product management?",
      mode: "default" as const,
    },
  ];

  return (
    <div className="flex flex-col h-full w-full bg-zinc-950 overflow-hidden">
      {/* Scrollable Message List */}
      <div className="flex-1 overflow-y-auto px-4 py-6 md:px-8 max-w-4xl mx-auto w-full">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full min-h-[420px] text-center space-y-6">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <div className="space-y-2 max-w-md">
              <h2 className="text-xl font-bold text-zinc-100 tracking-tight">
                The Lenny Growth Assistant
              </h2>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Enterprise growth copilot grounded in transcripts from 200+ Lenny's Podcast episodes.
                Features Claude-style Artifacts and the Ship 30 for 30 Content Engine.
              </p>
            </div>

            {/* Suggestion Prompt Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-2xl pt-2">
              {suggestionPrompts.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setActiveMode(s.mode);
                    onSendMessage(s.query, s.mode);
                  }}
                  className="flex flex-col items-start p-3 bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 rounded-xl transition text-left space-y-1 group"
                >
                  <div className="flex items-center space-x-1.5 text-xs font-semibold text-zinc-200 group-hover:text-indigo-400">
                    {s.mode === "ship30" ? (
                      <Feather className="w-3.5 h-3.5 text-amber-400" />
                    ) : s.mode === "artifact" ? (
                      <Code2 className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    )}
                    <span>{s.title}</span>
                  </div>
                  <p className="text-[11px] text-zinc-400 line-clamp-2 leading-normal">
                    {s.query}
                  </p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageItem
              key={index}
              message={msg}
              onOpenArtifact={onOpenArtifact}
            />
          ))
        )}

        {/* Live Status Indicator */}
        {statusMessage && (
          <div className="flex items-center space-x-2 text-xs text-indigo-400 bg-indigo-950/40 border border-indigo-900/50 rounded-lg px-3 py-2 my-2 animate-pulse w-fit">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
            <span>{statusMessage}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box Footer */}
      <div className="border-t border-zinc-800/80 bg-zinc-900/60 p-4 shrink-0">
        <div className="max-w-4xl mx-auto w-full flex flex-col space-y-2">
          {/* Mode Selector Chips */}
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-zinc-500 font-medium">Mode:</span>
            <button
              onClick={() => setActiveMode("default")}
              className={`px-2.5 py-1 rounded-md transition font-medium ${
                activeMode === "default"
                  ? "bg-zinc-700 text-white"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Grounded Chat
            </button>
            <button
              onClick={() => setActiveMode("ship30")}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-md transition font-medium ${
                activeMode === "ship30"
                  ? "bg-amber-600/30 text-amber-300 border border-amber-500/50"
                  : "text-zinc-400 hover:text-amber-300"
              }`}
            >
              <Feather className="w-3 h-3" />
              <span>Ship 30 for 30 Skill</span>
            </button>
            <button
              onClick={() => setActiveMode("artifact")}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-md transition font-medium ${
                activeMode === "artifact"
                  ? "bg-emerald-600/30 text-emerald-300 border border-emerald-500/50"
                  : "text-zinc-400 hover:text-emerald-300"
              }`}
            >
              <Code2 className="w-3 h-3" />
              <span>Artifact Tool</span>
            </button>
          </div>

          {/* Main Textarea & Buttons */}
          <div className="relative flex items-end bg-zinc-900 border border-zinc-800 focus-within:border-indigo-500 rounded-xl p-2 transition">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                activeMode === "ship30"
                  ? "Describe the topic to transform into a ~1,250-word Ship 30 for 30 essay..."
                  : activeMode === "artifact"
                  ? "Describe the interactive HTML/CSS tool, calculator, or document to build..."
                  : "Ask anything about product management, growth, pricing, or retention..."
              }
              rows={2}
              className="flex-1 bg-transparent resize-none outline-none text-sm text-zinc-100 placeholder-zinc-500 px-2 py-1 max-h-36 overflow-y-auto"
            />

            <div className="flex items-center space-x-1 pl-2">
              {isStreaming ? (
                <button
                  type="button"
                  onClick={onStopStreaming}
                  className="p-2 rounded-lg bg-rose-600/20 text-rose-400 hover:bg-rose-600 hover:text-white transition"
                  title="Stop generation"
                >
                  <StopCircle className="w-4 h-4" />
                </button>
              ) : (
                <button
                  type="button"
                  disabled={!input.trim()}
                  onClick={() => handleSubmit()}
                  className="p-2 rounded-lg bg-indigo-600 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-indigo-500 transition"
                  title="Send message"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
