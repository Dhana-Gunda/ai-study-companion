import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "destructive";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-indigo-600 text-white",
    secondary: "border-transparent bg-zinc-800 text-zinc-300",
    outline: "text-zinc-300 border-zinc-700",
    success: "border-transparent bg-emerald-950 text-emerald-400 border border-emerald-800/50",
    warning: "border-transparent bg-amber-950 text-amber-400 border border-amber-800/50",
    destructive: "border-transparent bg-red-950 text-red-400 border border-red-800/50",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge };
