"use client";

import Link from "next/link";
import { ArrowLeft, Play, Sparkles, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function DemoVideoPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Navigation & Header */}
        <div className="flex items-center justify-between">
          <Link href="/">
            <Button variant="ghost" size="sm" className="gap-2 text-zinc-400 hover:text-zinc-100">
              <ArrowLeft className="w-4 h-4" /> Back to App
            </Button>
          </Link>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-indigo-950/60 border border-indigo-800/60 text-indigo-300">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            PRD Section 20 Walkthrough
          </div>
        </div>

        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            AI Study Companion — Full System Walkthrough
          </h1>
          <p className="mt-2 text-sm text-zinc-400">
            Automated demonstration of the complete 13-stage connected learning loop (Space creation, PDF ingestion, Grounded AI Tutor, Refusal guardrails, Adaptive Quiz, EMA mastery, and Admin Telemetry).
          </p>
        </div>

        {/* Video Player Card */}
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-2 sm:p-4 shadow-2xl overflow-hidden">
          <div className="relative aspect-video rounded-xl overflow-hidden bg-black flex items-center justify-center">
            <video
              src="/demo_video.webm"
              controls
              autoPlay
              playsInline
              className="w-full h-full object-contain"
            >
              Your browser does not support the video tag.
            </video>
          </div>
        </div>

        {/* Chapters Covered in Video */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
          <div className="p-4 rounded-xl border border-zinc-800/80 bg-zinc-900/30 space-y-2">
            <h3 className="font-semibold text-sm text-zinc-200 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Core Learning Loop (Steps 1–7)
            </h3>
            <ul className="text-xs text-zinc-400 space-y-1.5 list-disc list-inside">
              <li>Live Stack Connectivity Probe (PostgreSQL 16 + pgvector, Redis)</li>
              <li>Space Creation & Project Boundary Initialization</li>
              <li>PDF Learning Material Upload & Ingestion</li>
              <li>PyMuPDF Chunking & 1536-dim Vector Embeddings</li>
              <li>Grounded AI Tutor Chat via Server-Sent Events (SSE)</li>
              <li>Accurate Page Attribution Citations (<code className="text-indigo-300">[Source: ... — Page X]</code>)</li>
            </ul>
          </div>

          <div className="p-4 rounded-xl border border-zinc-800/80 bg-zinc-900/30 space-y-2">
            <h3 className="font-semibold text-sm text-zinc-200 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Evaluation & Observability (Steps 8–13)
            </h3>
            <ul className="text-xs text-zinc-400 space-y-1.5 list-disc list-inside">
              <li>Low-Evidence Refusal Guardrail on Out-of-Domain Queries</li>
              <li>Adaptive Quiz Targeting Weak Learner Concepts</li>
              <li>Immediate MCQ & Open-Ended Rubric Grading</li>
              <li>Exponential Moving Average (EMA) Concept Mastery Tracking</li>
              <li>Active Growth & Next Action Recommendation Engine</li>
              <li>Admin Telemetry Dashboard (Tokens, Latency, Spend USD)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
