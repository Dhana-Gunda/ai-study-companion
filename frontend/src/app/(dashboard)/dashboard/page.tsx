import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, Compass, Sparkles, ArrowRight, Activity, AlertCircle } from "lucide-react";

export default function UserDashboardPage() {
  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      {/* Hero / Orientation Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-zinc-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Learner Workspace</h1>
          <p className="text-zinc-400 mt-1">
            Where was I, how am I doing, and what should I do next?
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/spaces">
            <Button variant="outline">Browse Spaces</Button>
          </Link>
          <Link href="/spaces/space-1/projects/project-ml">
            <Button className="gap-2">
              <Sparkles className="w-4 h-4" /> Continue Learning
            </Button>
          </Link>
        </div>
      </div>

      {/* Triad Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 1. What am I learning? */}
        <Card className="border-indigo-500/20 bg-gradient-to-b from-indigo-950/20 to-zinc-900/60">
          <CardHeader className="pb-2">
            <Badge variant="secondary" className="w-fit mb-2">What am I learning?</Badge>
            <CardTitle className="text-xl">Deep Learning Fundamentals</CardTitle>
            <CardDescription>In Space: AI & Machine Learning Engineering</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 pt-2">
            <p className="text-sm text-zinc-300">
              <span className="text-zinc-400">Current Goal:</span> Master gradient descent and backpropagation mathematics.
            </p>
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <BookOpen className="w-4 h-4 text-indigo-400" /> 3 Uploaded Materials Indexed
            </div>
          </CardContent>
        </Card>

        {/* 2. How well am I learning it? */}
        <Card className="border-emerald-500/20 bg-gradient-to-b from-emerald-950/20 to-zinc-900/60">
          <CardHeader className="pb-2">
            <Badge variant="success" className="w-fit mb-2">How well am I learning it?</Badge>
            <CardTitle className="text-xl">68% Average Mastery</CardTitle>
            <CardDescription>Based on 4 quiz sessions & 18 questions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 pt-2">
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">Linear Algebra</span>
                <span className="text-emerald-400 font-semibold">88% (Improving)</span>
              </div>
              <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: "88%" }} />
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">Backpropagation</span>
                <span className="text-amber-400 font-semibold">42% (Attention)</span>
              </div>
              <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 rounded-full" style={{ width: "42%" }} />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 3. What should I do next? */}
        <Card className="border-amber-500/20 bg-gradient-to-b from-amber-950/20 to-zinc-900/60">
          <CardHeader className="pb-2">
            <Badge variant="warning" className="w-fit mb-2">Recommended Next Action</Badge>
            <CardTitle className="text-xl">Targeted Practice Drill</CardTitle>
            <CardDescription>Personalized recommendation from your growth trend</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 pt-2">
            <p className="text-sm text-zinc-300">
              Your understanding of <strong className="text-amber-300">Backpropagation</strong> has gaps in chain rule derivations. Review Page 14 of your notes and take a 3-question drill.
            </p>
            <Link href="/spaces/space-1/projects/project-ml" className="block">
              <Button size="sm" className="w-full gap-2">
                Start Drill <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recent Projects Table / List */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" /> Active Learning Projects
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle className="text-base font-semibold">Deep Learning Fundamentals</CardTitle>
                <CardDescription>AI & Machine Learning Space</CardDescription>
              </div>
              <Badge variant="success">Active</Badge>
            </CardHeader>
            <CardContent className="text-sm text-zinc-400 flex items-center justify-between pt-2">
              <span>Goal: Master mathematical foundations</span>
              <Link href="/spaces/space-1/projects/project-ml" className="text-indigo-400 hover:underline flex items-center gap-1">
                Open Workspace <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle className="text-base font-semibold">Distributed Systems Architecture</CardTitle>
                <CardDescription>System Design & Cloud Space</CardDescription>
              </div>
              <Badge variant="secondary">In Progress</Badge>
            </CardHeader>
            <CardContent className="text-sm text-zinc-400 flex items-center justify-between pt-2">
              <span>Goal: Raft consensus and partition tolerance</span>
              <Link href="/spaces/space-2/projects/project-dist" className="text-indigo-400 hover:underline flex items-center gap-1">
                Open Workspace <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
