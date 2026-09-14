"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { checkBackendHealth, HealthCheckResponse } from "@/lib/api";
import {
  Sparkles,
  Layers,
  BookOpen,
  HelpCircle,
  BarChart2,
  Shield,
  Activity,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Database,
  Cpu
} from "lucide-react";

export default function HomePage() {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function loadHealth() {
      try {
        const res = await checkBackendHealth();
        if (mounted) setHealth(res);
      } catch {
        if (mounted) setHealth(null);
      } finally {
        if (mounted) setLoadingHealth(false);
      }
    }
    loadHealth();
    const interval = setInterval(loadHealth, 6000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10 space-y-12">
      {/* Hero Section */}
      <section className="text-center space-y-4 max-w-3xl mx-auto pt-6">
        <Badge variant="secondary" className="px-3 py-1 text-xs gap-1.5 border border-zinc-700/80">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          Prototype Architecture Skeleton v1.0
        </Badge>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
          AI-Powered Learning &amp; Growth Workspace
        </h1>
        <p className="text-base sm:text-lg text-zinc-400">
          A persistent, contextual, and measurable AI companion grounded in your uploaded materials,
          with adaptive quizzes, concept mastery tracking, and event-driven analytics.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link href="/dashboard">
            <Button size="lg" className="gap-2">
              Enter Workspace <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
          <Link href="/spaces/space-1/projects/project-ml">
            <Button size="lg" variant="outline" className="gap-2">
              <BookOpen className="w-4 h-4 text-indigo-400" /> Open Sample Project
            </Button>
          </Link>
          <Link href="/demo">
            <Button size="lg" variant="outline" className="gap-2 border-indigo-500/40 text-indigo-300 hover:bg-indigo-950/40">
              <Sparkles className="w-4 h-4 text-indigo-400" /> Watch Demo Video
            </Button>
          </Link>
          <Link href="/admin">
            <Button size="lg" variant="secondary" className="gap-2">
              <Shield className="w-4 h-4 text-zinc-300" /> Admin Dashboard
            </Button>
          </Link>
        </div>
      </section>

      {/* Real-time Stack Verification Probe */}
      <section className="max-w-4xl mx-auto">
        <Card className="border-zinc-800 bg-zinc-900/60 shadow-xl">
          <CardHeader className="pb-3 border-b border-zinc-800/60">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-indigo-400" />
                <CardTitle className="text-base font-semibold">Live Stack Connectivity Probe</CardTitle>
              </div>
              {loadingHealth ? (
                <Badge variant="secondary">Probing Backend...</Badge>
              ) : health?.status === "healthy" ? (
                <Badge variant="success" className="gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" /> All Services Connected
                </Badge>
              ) : health?.status === "degraded" ? (
                <Badge variant="warning" className="gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5" /> Degraded
                </Badge>
              ) : (
                <Badge variant="destructive" className="gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5" /> Backend Unreachable
                </Badge>
              )}
            </div>
            <CardDescription>
              Continuous probe testing FastAPI backend, PostgreSQL (pgvector extension), and Redis connection
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm font-mono">
            {/* Database / pgvector */}
            <div className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80 space-y-1">
              <div className="flex items-center justify-between text-xs text-zinc-400">
                <span className="flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-blue-400" /> Database
                </span>
                <span className={health?.services?.database?.status === "connected" ? "text-emerald-400" : "text-zinc-500"}>
                  {health?.services?.database?.status || "offline"}
                </span>
              </div>
              <div className="text-xs text-zinc-300 font-sans">
                PostgreSQL 16 + <strong className="text-indigo-300 font-mono">pgvector</strong>
              </div>
              <div className="text-[11px] text-zinc-500 font-mono">
                {health?.services?.database?.pgvector_enabled ? "✓ Vector extension ready" : "Awaiting DB connection"}
              </div>
            </div>

            {/* Redis / Queue */}
            <div className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80 space-y-1">
              <div className="flex items-center justify-between text-xs text-zinc-400">
                <span className="flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-amber-400" /> Queue &amp; Cache
                </span>
                <span className={health?.services?.redis?.status === "connected" ? "text-emerald-400" : "text-zinc-500"}>
                  {health?.services?.redis?.status || "offline"}
                </span>
              </div>
              <div className="text-xs text-zinc-300 font-sans">
                Redis 7 (ARQ Workers)
              </div>
              <div className="text-[11px] text-zinc-500 font-mono">
                {health?.services?.redis?.status === "connected" ? "✓ Ping latency < 2ms" : "Awaiting Redis connection"}
              </div>
            </div>

            {/* AI Providers */}
            <div className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/80 space-y-1">
              <div className="flex items-center justify-between text-xs text-zinc-400">
                <span className="flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-indigo-400" /> AI Provider
                </span>
                <span className="text-indigo-300 font-mono">
                  {health?.services?.ai_providers?.default_provider || "mock/local"}
                </span>
              </div>
              <div className="text-xs text-zinc-300 font-sans">
                LLM Abstraction Layer
              </div>
              <div className="text-[11px] text-zinc-500 font-mono">
                OpenAI / Anthropic / Ollama
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Primary Learning Loop Section */}
      <section className="space-y-6">
        <div className="text-center space-y-1">
          <h2 className="text-2xl font-bold text-white">The Connected Learning Loop</h2>
          <p className="text-sm text-zinc-400">
            A cohesive architecture connecting study materials to measurable growth
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 text-center">
          {[
            { step: "1. Space", desc: "Broad study domain", icon: Layers },
            { step: "2. Project", desc: "Focused learning goal", icon: BookOpen },
            { step: "3. Materials", desc: "PDF async parsing & RAG", icon: BookOpen },
            { step: "4. AI Tutor", desc: "Grounded with citations", icon: Sparkles },
            { step: "5. Quiz", desc: "Adaptive MCQ & Rubrics", icon: HelpCircle },
            { step: "6. Mastery", desc: "EMA score & trend tracking", icon: BarChart2 },
            { step: "7. Growth", desc: "Targeted next action", icon: Activity },
          ].map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={index}
                className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-2 hover:border-zinc-700 transition-colors"
              >
                <div className="w-8 h-8 rounded-lg bg-zinc-800 text-indigo-400 flex items-center justify-center mx-auto">
                  <Icon className="w-4 h-4" />
                </div>
                <div className="text-xs font-semibold text-zinc-200">{item.step}</div>
                <div className="text-[11px] text-zinc-500 leading-tight">{item.desc}</div>
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
