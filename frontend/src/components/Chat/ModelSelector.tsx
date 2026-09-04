import React from "react";
import { Cpu, Cloud, ChevronDown } from "lucide-react";

interface ModelSelectorProps {
  currentProvider: "ollama" | "claude" | "openai";
  onProviderChange: (provider: "ollama" | "claude" | "openai") => void;
  disabled?: boolean;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  currentProvider,
  onProviderChange,
  disabled = false,
}) => {
  return (
    <div className="relative inline-flex items-center">
      <label htmlFor="model-select" className="sr-only">Select Model Provider</label>
      <div className="flex items-center space-x-2 bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-700 transition">
        {currentProvider === "ollama" ? (
          <span className="flex items-center text-emerald-400 font-medium space-x-1.5">
            <Cpu className="w-3.5 h-3.5" />
            <span>Ollama: llama3.2:3b (Local)</span>
          </span>
        ) : currentProvider === "claude" ? (
          <span className="flex items-center text-indigo-400 font-medium space-x-1.5">
            <Cloud className="w-3.5 h-3.5" />
            <span>Claude 3.5 Sonnet (Cloud)</span>
          </span>
        ) : (
          <span className="flex items-center text-sky-400 font-medium space-x-1.5">
            <Cloud className="w-3.5 h-3.5" />
            <span>OpenAI GPT-4o (Cloud)</span>
          </span>
        )}

        <select
          id="model-select"
          disabled={disabled}
          value={currentProvider}
          onChange={(e) => onProviderChange(e.target.value as any)}
          className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
          aria-label="Switch Model Provider"
        >
          <option value="ollama">Ollama (Local - llama3.2:3b)</option>
          <option value="claude">Anthropic Claude (Cloud)</option>
          <option value="openai">OpenAI GPT-4o (Cloud)</option>
        </select>
        <ChevronDown className="w-3.5 h-3.5 text-zinc-500 pointer-events-none" />
      </div>
    </div>
  );
};
