import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Cpu, DollarSign, Clock, ShieldCheck, Database, CheckCircle2, ArrowLeft } from "lucide-react";

export default function AdminDashboardPage() {
  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs text-zinc-400 mb-1">
            <Link href="/" className="hover:text-zinc-200">Home</Link>
            <span>/</span>
            <span className="text-zinc-300">Administration</span>
          </div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-indigo-400" /> Platform Admin & AI Observability
          </h1>
          <p className="text-sm text-zinc-400">
            Real-time telemetry on learning activity, AI costs, evaluation metrics, and system health
          </p>
        </div>
        <Link href="/dashboard">
          <Button variant="outline" size="sm" className="gap-2">
            <ArrowLeft className="w-4 h-4" /> Exit to Workspace
          </Button>
        </Link>
      </div>

      {/* Top Telemetry KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Total AI Spend</CardTitle>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">$0.1420</div>
            <p className="text-xs text-zinc-500 mt-1">48 requests logged across models</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">P95 AI Latency</CardTitle>
            <Clock className="w-4 h-4 text-indigo-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">840 ms</div>
            <p className="text-xs text-emerald-400 mt-1">Within target SLA (&lt;1200ms)</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Learning Events</CardTitle>
            <Activity className="w-4 h-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">218</div>
            <p className="text-xs text-zinc-500 mt-1">Across 3 active projects</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">System Health</CardTitle>
            <Database className="w-4 h-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-5 h-5" /> Healthy
            </div>
            <p className="text-xs text-zinc-500 mt-1">Postgres (pgvector) + Redis online</p>
          </CardContent>
        </Card>
      </div>

      {/* AI Request Log Telemetry Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" /> Recent AI Request Invocations
          </CardTitle>
          <CardDescription>
            Audit log tracking feature, model, tokens, latency, cost, and evidence status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-zinc-300">
              <thead className="border-b border-zinc-800 text-zinc-400 uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Feature</th>
                  <th className="py-2.5 px-3">Model</th>
                  <th className="py-2.5 px-3">Tokens (In / Out)</th>
                  <th className="py-2.5 px-3">Latency</th>
                  <th className="py-2.5 px-3">Cost (USD)</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 font-mono">
                <tr>
                  <td className="py-2.5 px-3 text-zinc-200">tutor_grounded_chat</td>
                  <td className="py-2.5 px-3">gpt-4o-mini</td>
                  <td className="py-2.5 px-3">624 / 142</td>
                  <td className="py-2.5 px-3">540 ms</td>
                  <td className="py-2.5 px-3">$0.00012</td>
                  <td className="py-2.5 px-3"><Badge variant="success">SUCCESS</Badge></td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-zinc-200">adaptive_quiz_gen</td>
                  <td className="py-2.5 px-3">gpt-4o-mini</td>
                  <td className="py-2.5 px-3">890 / 310</td>
                  <td className="py-2.5 px-3">910 ms</td>
                  <td className="py-2.5 px-3">$0.00021</td>
                  <td className="py-2.5 px-3"><Badge variant="success">SUCCESS</Badge></td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-zinc-200">tutor_grounded_chat</td>
                  <td className="py-2.5 px-3">gpt-4o-mini</td>
                  <td className="py-2.5 px-3">412 / 65</td>
                  <td className="py-2.5 px-3">380 ms</td>
                  <td className="py-2.5 px-3">$0.00007</td>
                  <td className="py-2.5 px-3"><Badge variant="warning">REFUSED_LOW_EVIDENCE</Badge></td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
