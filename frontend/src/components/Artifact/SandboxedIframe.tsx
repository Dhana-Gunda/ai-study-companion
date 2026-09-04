import React, { useMemo } from "react";
import DOMPurify from "dompurify";

interface SandboxedIframeProps {
  content: string;
  title: string;
}

export const SandboxedIframe: React.FC<SandboxedIframeProps> = ({ content, title }) => {
  // Sanitize markup prior to injecting into iframe srcDoc
  const cleanHtml = useMemo(() => {
    if (typeof window === "undefined") return content;
    return DOMPurify.sanitize(content, {
      WHOLE_DOCUMENT: true,
      ADD_TAGS: ["style", "link", "script", "button", "input", "select", "canvas"],
      ADD_ATTR: ["target", "onclick", "id", "class", "style", "type", "value"],
    });
  }, [content]);

  return (
    <div className="flex flex-col h-full w-full rounded-lg overflow-hidden bg-zinc-950 border border-zinc-800 shadow-xl">
      <div className="bg-zinc-900 border-b border-zinc-800 px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-medium text-zinc-300 tracking-wide uppercase">
            {title}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[11px] text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60 font-mono">
            Sandboxed Iframe
          </span>
          <span className="text-[11px] text-zinc-400 bg-zinc-800 px-2 py-0.5 rounded font-mono">
            Isolated Origin
          </span>
        </div>
      </div>
      <div className="flex-1 w-full bg-white relative">
        <iframe
          title={title}
          srcDoc={cleanHtml}
          // Strict security isolation: allow scripts to run for interactivity,
          // but omit allow-same-origin to prevent access to parent cookies, local storage, and DOM.
          sandbox="allow-scripts"
          className="w-full h-full border-none absolute inset-0"
        />
      </div>
    </div>
  );
};
