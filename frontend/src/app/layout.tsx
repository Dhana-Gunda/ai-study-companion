import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { Sparkles, Shield, Layers, LayoutDashboard } from "lucide-react";

export const metadata: Metadata = {
  title: "AI Study Companion",
  description: "AI-powered learning workspace with grounded RAG tutor, adaptive assessments, concept mastery, and growth tracking.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-zinc-950 text-zinc-100 antialiased min-h-screen flex flex-col font-sans selection:bg-indigo-500/30">
        {/* Top Global Navigation Bar */}
        <header className="sticky top-0 z-50 border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md px-6 py-3.5">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/30 group-hover:scale-105 transition-transform">
                <Sparkles className="w-4 h-4" />
              </div>
              <span className="font-bold tracking-tight text-white text-base">
                AI Study Companion
              </span>
            </Link>

            <nav className="flex items-center gap-4 text-sm font-medium">
              <Link
                href="/dashboard"
                className="flex items-center gap-1.5 text-zinc-400 hover:text-zinc-100 transition-colors"
              >
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </Link>
              <Link
                href="/spaces"
                className="flex items-center gap-1.5 text-zinc-400 hover:text-zinc-100 transition-colors"
              >
                <Layers className="w-4 h-4" />
                Spaces
              </Link>
              <Link
                href="/admin"
                className="flex items-center gap-1.5 text-zinc-400 hover:text-zinc-100 transition-colors"
              >
                <Shield className="w-4 h-4" />
                Admin
              </Link>
            </nav>
          </div>
        </header>

        {/* Viewport Content */}
        <div className="flex-1 flex flex-col">{children}</div>

        {/* Minimal Footer */}
        <footer className="border-t border-zinc-900 bg-zinc-950 py-4 px-6 text-center text-xs text-zinc-500">
          AI Study Companion • Persistent, Contextual, Measurable Learning
        </footer>
      </body>
    </html>
  );
}
