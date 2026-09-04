import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, Download, X, Eye, Code, FileText, Globe } from "lucide-react";
import { SandboxedIframe } from "./SandboxedIframe";
import { Artifact } from "../../lib/api";

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [viewMode, setViewMode] = useState<"preview" | "code">("preview");
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code:", err);
    }
  };

  const handleDownload = () => {
    const ext = artifact.artifact_type === "html" ? "html" : "md";
    const filename = `${artifact.title.toLowerCase().replace(/[^a-z0-9]/g, "_")}.${ext}`;
    const blob = new Blob([artifact.content], {
      type: artifact.artifact_type === "html" ? "text/html" : "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <aside aria-label="Artifact side panel" className="flex flex-col h-full w-full bg-zinc-900 border-l border-zinc-800 animate-in slide-in-from-right duration-200">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-950/60">
        <div className="flex items-center space-x-2.5 overflow-hidden pr-2">
          {artifact.artifact_type === "html" ? (
            <Globe className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
          )}
          <h2 className="text-sm font-semibold text-zinc-200 truncate">
            {artifact.title}
          </h2>
        </div>

        <div className="flex items-center space-x-1.5 shrink-0">
          {/* Toggle Preview / Code */}
          <div className="flex bg-zinc-800 rounded-md p-0.5 mr-2">
            <button
              onClick={() => setViewMode("preview")}
              className={`flex items-center space-x-1 px-2.5 py-1 text-xs rounded font-medium transition ${
                viewMode === "preview"
                  ? "bg-zinc-700 text-white shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
              title="Rendered Preview"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setViewMode("code")}
              className={`flex items-center space-x-1 px-2.5 py-1 text-xs rounded font-medium transition ${
                viewMode === "code"
                  ? "bg-zinc-700 text-white shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
              title="Source Code"
            >
              <Code className="w-3.5 h-3.5" />
              <span>Code</span>
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="p-1.5 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 rounded transition"
            title="Copy to clipboard"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={handleDownload}
            className="p-1.5 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 rounded transition"
            title="Download file"
          >
            <Download className="w-4 h-4" />
          </button>

          <button
            onClick={onClose}
            className="p-1.5 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 rounded transition ml-1"
            title="Close viewer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden p-4">
        {viewMode === "code" ? (
          <div className="h-full w-full overflow-auto rounded-lg bg-zinc-950 p-4 border border-zinc-800 font-mono text-xs text-zinc-300">
            <pre className="whitespace-pre-wrap">{artifact.content}</pre>
          </div>
        ) : artifact.artifact_type === "html" ? (
          <SandboxedIframe content={artifact.content} title={artifact.title} />
        ) : (
          <div className="h-full w-full overflow-auto rounded-lg bg-zinc-950 p-6 border border-zinc-800 prose prose-invert prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </aside>
  );
};
