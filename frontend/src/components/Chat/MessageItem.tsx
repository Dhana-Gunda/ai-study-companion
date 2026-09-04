import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Sparkles, User, FileCode, Clock, BookOpen } from "lucide-react";
import { Message, Citation, Artifact } from "../../lib/api";

interface MessageItemProps {
  message: Message;
  onOpenArtifact?: (artifact: Artifact) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, onOpenArtifact }) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-5`}>
      <div className={`flex max-w-[88%] space-x-3 ${isUser ? "flex-row-reverse space-x-reverse" : "flex-row"}`}>
        {/* Avatar Icon */}
        <div
          className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
            isUser
              ? "bg-zinc-700 text-zinc-200"
              : "bg-indigo-600/30 border border-indigo-500/40 text-indigo-400"
          }`}
        >
          {isUser ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
        </div>

        {/* Message Bubble Body */}
        <div className="flex flex-col space-y-2">
          <div
            className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              isUser
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-zinc-900 border border-zinc-800 text-zinc-100 shadow-md"
            }`}
          >
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              <div className="prose prose-invert prose-sm max-w-none space-y-2">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>

          {/* Assistant Metadata: Citations & Artifact Badges */}
          {!isUser && (
            <div className="flex flex-col space-y-2 px-1">
              {/* Citations Badges */}
              {message.sources && message.sources.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <span className="text-[11px] font-medium text-zinc-400 flex items-center mr-1">
                    <BookOpen className="w-3 h-3 mr-1 text-emerald-400" />
                    Sources:
                  </span>
                  {message.sources.map((src: Citation, idx: number) => (
                    <span
                      key={idx}
                      className="inline-flex items-center space-x-1 text-[11px] bg-emerald-950/40 border border-emerald-800/40 text-emerald-300 px-2 py-0.5 rounded-full"
                      title={`${src.episode} | Match: ${(src.score * 100).toFixed(0)}%`}
                    >
                      <span className="font-semibold">{src.guest}</span>
                      {src.timestamp && src.timestamp !== "General Discussion" && (
                        <span className="text-emerald-400/80 flex items-center">
                          <Clock className="w-2.5 h-2.5 inline mr-0.5" />
                          {src.timestamp}
                        </span>
                      )}
                    </span>
                  ))}
                </div>
              )}

              {/* Artifact Trigger Button */}
              {message.artifacts && message.artifacts.length > 0 && (
                <div className="pt-1">
                  {message.artifacts.map((art: Artifact, idx: number) => (
                    <button
                      key={idx}
                      onClick={() => onOpenArtifact && onOpenArtifact(art)}
                      className="inline-flex items-center space-x-2 text-xs bg-indigo-950/60 border border-indigo-700/60 hover:border-indigo-500 text-indigo-200 px-3 py-1.5 rounded-lg transition shadow-sm group"
                    >
                      <FileCode className="w-3.5 h-3.5 text-indigo-400 group-hover:scale-110 transition" />
                      <span className="font-medium">Open Artifact: {art.title}</span>
                      <span className="text-[10px] text-zinc-400 uppercase">({art.artifact_type})</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
