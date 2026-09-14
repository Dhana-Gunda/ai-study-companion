"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  BookOpen,
  MessageSquare,
  HelpCircle,
  TrendingUp,
  BarChart2,
  Sparkles,
  Upload,
  ArrowLeft,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Send,
  Loader2,
  RefreshCw,
  Award
} from "lucide-react";
import {
  getProjectDashboard,
  getProjectMaterials,
  uploadMaterial,
  streamTutorChat,
  startQuiz,
  submitQuizAnswer,
  completeQuiz,
  getProjectMastery,
  Citation,
  ProjectDashboard,
  Material,
  QuizSession,
  ConceptMastery
} from "@/lib/api";

export default function ProjectWorkspacePage({
  params,
}: {
  params: { spaceId: string; projectId: string };
}) {
  const [activeTab, setActiveTab] = useState<"overview" | "materials" | "tutor" | "quiz" | "mastery">("overview");
  const [dashboard, setDashboard] = useState<ProjectDashboard | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [masteryList, setMasteryList] = useState<ConceptMastery[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Tutor chat state
  const [chatMessages, setChatMessages] = useState<Array<{
    role: "user" | "assistant";
    content: string;
    citations?: Citation[];
    refused?: boolean;
  }>>([]);
  const [inputQuery, setInputQuery] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Quiz state
  const [currentQuiz, setCurrentQuiz] = useState<QuizSession | null>(null);
  const [quizLoading, setQuizLoading] = useState<boolean>(false);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [submittedAnswers, setSubmittedAnswers] = useState<Record<string, { score: number; feedback: string }>>({});

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadData();
  }, [params.projectId]);

  async function loadData() {
    setLoading(true);
    try {
      const [dash, mats, mast] = await Promise.all([
        getProjectDashboard(params.projectId).catch(() => null),
        getProjectMaterials(params.projectId).catch(() => []),
        getProjectMastery(params.projectId).catch(() => []),
      ]);
      setDashboard(dash);
      setMaterials(mats);
      setMasteryList(mast);
    } catch (err) {
      console.error("Error loading project workspace data", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    try {
      await uploadMaterial(params.projectId, file);
      // Refresh materials list
      const mats = await getProjectMaterials(params.projectId);
      setMaterials(mats);
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload file");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleSendTutorMessage() {
    if (!inputQuery.trim() || isStreaming) return;

    const query = inputQuery.trim();
    setInputQuery("");
    setIsStreaming(true);

    // Add user query immediately
    setChatMessages((prev) => [...prev, { role: "user", content: query }]);

    // Prepare assistant placeholder
    setChatMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    await streamTutorChat(
      params.projectId,
      query,
      conversationId,
      (token) => {
        setChatMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: updated[lastIdx].content + token,
            };
          }
          return updated;
        });
      },
      (doneData) => {
        setIsStreaming(false);
        if (doneData.conversation_id) setConversationId(doneData.conversation_id);
        setChatMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
            updated[lastIdx] = {
              ...updated[lastIdx],
              citations: doneData.citations,
              refused: doneData.refused,
            };
          }
          return updated;
        });
      },
      (error) => {
        setIsStreaming(false);
        setChatMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: `Error: ${error.message}. Please verify the backend is running.`,
            };
          }
          return updated;
        });
      }
    );
  }

  async function handleStartQuiz() {
    setQuizLoading(true);
    try {
      const quiz = await startQuiz(params.projectId, 3);
      setCurrentQuiz(quiz);
      setUserAnswers({});
      setSubmittedAnswers({});
    } catch (err: any) {
      alert("Failed to start quiz: " + err.message);
    } finally {
      setQuizLoading(false);
    }
  }

  async function handleSubmitAnswer(questionId: string) {
    if (!currentQuiz) return;
    const answer = userAnswers[questionId];
    if (!answer || !answer.trim()) return;

    try {
      const result = await submitQuizAnswer(currentQuiz.id, questionId, answer.trim());
      setSubmittedAnswers((prev) => ({
        ...prev,
        [questionId]: { score: result.score, feedback: result.feedback },
      }));
    } catch (err: any) {
      alert("Error submitting answer: " + err.message);
    }
  }

  async function handleCompleteQuiz() {
    if (!currentQuiz) return;
    setQuizLoading(true);
    try {
      const finished = await completeQuiz(currentQuiz.id);
      setCurrentQuiz(finished);
      // Reload dashboard and mastery scores
      await loadData();
    } catch (err: any) {
      alert("Error finalizing quiz: " + err.message);
    } finally {
      setQuizLoading(false);
    }
  }

  const projectName = dashboard?.project?.name || "Intro to ML";
  const learningGoal = dashboard?.project?.learning_goal || "Master linear models, loss functions, and gradient descent";
  const overallMastery = dashboard?.overall_mastery_percentage ?? 65;

  return (
    <div className="flex flex-col min-h-screen bg-zinc-950 text-zinc-100">
      {/* Top Project Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <Link href="/dashboard" className="hover:text-zinc-200">Home</Link>
              <span>/</span>
              <Link href="/spaces" className="hover:text-zinc-200">Spaces</Link>
              <span>/</span>
              <span className="text-zinc-300 font-medium">{projectName}</span>
            </div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              {projectName}
              <Badge variant="success">Active Workspace</Badge>
            </h1>
            <p className="text-sm text-zinc-400">
              <strong className="text-zinc-300">Goal:</strong> {learningGoal}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setActiveTab("materials")}>
              <Upload className="w-4 h-4 mr-1.5" /> Upload Material
            </Button>
            <Button size="sm" onClick={() => setActiveTab("tutor")}>
              <MessageSquare className="w-4 h-4 mr-1.5" /> Ask Tutor
            </Button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="max-w-7xl mx-auto flex items-center gap-2 mt-4 pt-2 border-t border-zinc-800/60 overflow-x-auto">
          {[
            { id: "overview", label: "Overview", icon: TrendingUp },
            { id: "materials", label: `Materials (${materials.length})`, icon: BookOpen },
            { id: "tutor", label: "AI Tutor (Grounded)", icon: MessageSquare },
            { id: "quiz", label: "Adaptive Quiz", icon: HelpCircle },
            { id: "mastery", label: "Mastery & Growth", icon: BarChart2 },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${
                  isActive
                    ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/40"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60"
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Workspace Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Recommendation Banner */}
            <div className="p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <span className="text-xs uppercase tracking-wider text-indigo-400 font-semibold">Recommended Next Action</span>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  {dashboard?.active_recommendation?.headline || "Reinforce Gradient Descent & Step Sizing"}
                </h3>
                <p className="text-sm text-zinc-300 mt-1">
                  {dashboard?.active_recommendation?.description ||
                    "Your mastery in Gradient Descent is at 45% (ATTENTION). Take a targeted diagnostic quiz to master convergence criteria."}
                </p>
              </div>
              <Button onClick={() => setActiveTab("quiz")} className="whitespace-nowrap gap-1.5">
                <Sparkles className="w-4 h-4" /> {dashboard?.active_recommendation?.cta_label || "Start Targeted Drill"}
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Concept Mastery Card */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-base">Concept Mastery Breakdown</CardTitle>
                      <CardDescription>Grounded continuous estimation with EMA smoothing</CardDescription>
                    </div>
                    <Badge variant="outline">{overallMastery}% Overall</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {(masteryList.length > 0 ? masteryList : [
                    { concept_id: "c1", name: "Linear Regression", mastery_score: 0.85, trend: "IMPROVING" },
                    { concept_id: "c2", name: "Cost Functions (MSE)", mastery_score: 0.70, trend: "STABLE" },
                    { concept_id: "c3", name: "Gradient Descent", mastery_score: 0.45, trend: "ATTENTION" },
                    { concept_id: "c4", name: "Learning Rate Tuning", mastery_score: 0.55, trend: "STABLE" },
                  ]).map((c) => {
                    const scorePct = Math.round(c.mastery_score * 100);
                    const isAttention = c.trend === "ATTENTION" || scorePct < 50;
                    return (
                      <div key={c.concept_id} className="space-y-1">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="text-zinc-300">{c.name}</span>
                          <span className={isAttention ? "text-amber-400" : "text-emerald-400"}>
                            {scorePct}% • {c.trend}
                          </span>
                        </div>
                        <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              isAttention ? "bg-amber-500" : "bg-emerald-500"
                            }`}
                            style={{ width: `${scorePct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>

              {/* Uploaded Materials Summary Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Uploaded Materials</CardTitle>
                  <CardDescription>Documents chunked and indexed with pgvector for grounded retrieval</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {materials.length === 0 ? (
                    <div className="p-4 text-center text-sm text-zinc-500 border border-dashed border-zinc-800 rounded-lg">
                      No materials uploaded yet. Upload a PDF below to ground the tutor.
                    </div>
                  ) : (
                    materials.map((m) => (
                      <div key={m.id} className="flex items-center justify-between p-3 rounded-lg border border-zinc-800 bg-zinc-900/40">
                        <div className="flex items-center gap-3">
                          <FileText className="w-5 h-5 text-indigo-400" />
                          <div>
                            <div className="text-sm font-medium text-zinc-200">{m.filename}</div>
                            <div className="text-xs text-zinc-500">
                              {m.page_count} pages • {(m.file_size_bytes / 1024).toFixed(1)} KB
                            </div>
                          </div>
                        </div>
                        <Badge variant={m.status === "READY" ? "success" : m.status === "PROCESSING" ? "warning" : "default"}>
                          {m.status}
                        </Badge>
                      </div>
                    ))
                  )}
                  <Button variant="outline" className="w-full text-xs" onClick={() => setActiveTab("materials")}>
                    Manage All Materials
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {activeTab === "materials" && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Project Learning Materials</CardTitle>
                <CardDescription>Upload PDF documents. Text extraction and pgvector 1536d embeddings run automatically.</CardDescription>
              </div>
              <div>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".pdf"
                  className="hidden"
                  id="pdf-file-input"
                />
                <Button
                  size="sm"
                  className="gap-2"
                  disabled={uploading}
                  onClick={() => fileInputRef.current?.click()}
                >
                  {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                  {uploading ? "Processing PDF..." : "Upload New PDF"}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {uploadError && (
                <div className="p-3 bg-red-950/40 border border-red-800 rounded-lg text-sm text-red-300">
                  {uploadError}
                </div>
              )}

              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-zinc-800 rounded-xl p-8 text-center space-y-2 hover:border-zinc-700 cursor-pointer transition-colors"
              >
                <Upload className="w-8 h-8 text-zinc-500 mx-auto" />
                <div className="text-sm text-zinc-300 font-medium">Click to select or drag and drop a PDF file</div>
                <div className="text-xs text-zinc-500">PDF documents with page provenance and semantic chunking</div>
              </div>

              <div className="space-y-2 pt-2">
                <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Indexed Documents</h4>
                {materials.length === 0 ? (
                  <p className="text-sm text-zinc-500">No documents uploaded yet.</p>
                ) : (
                  materials.map((m) => (
                    <div key={m.id} className="flex items-center justify-between p-3 rounded-lg border border-zinc-800 bg-zinc-900/40">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-indigo-400" />
                        <div>
                          <div className="text-sm font-medium text-zinc-200">{m.filename}</div>
                          <div className="text-xs text-zinc-500">
                            {m.page_count} pages • {(m.file_size_bytes / 1024).toFixed(1)} KB • Uploaded {new Date(m.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <Badge variant={m.status === "READY" ? "success" : m.status === "PROCESSING" ? "warning" : "destructive"}>
                        {m.status}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === "tutor" && (
          <Card className="min-h-[550px] flex flex-col">
            <CardHeader className="border-b border-zinc-800 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-indigo-400" /> Grounded AI Tutor
                  </CardTitle>
                  <CardDescription>Strictly answers based on your uploaded project materials with page citations</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">Grounded RAG</Badge>
                  <Badge variant="secondary">Citations Active</Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex-1 p-4 flex flex-col justify-between space-y-4">
              <div className="space-y-4 overflow-y-auto max-h-[450px]">
                {chatMessages.length === 0 && (
                  <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800 space-y-2">
                    <div className="text-xs font-semibold text-indigo-400">AI TUTOR</div>
                    <p className="text-sm text-zinc-300">
                      Welcome! Ask any question about your project notes. Every answer is grounded directly in your uploaded materials and accompanied by page citations.
                    </p>
                    <div className="flex flex-wrap gap-2 pt-2">
                      {[
                        "Why does gradient descent overshoot when the learning rate is too high?",
                        "What is the formula for Mean Squared Error?",
                        "Explain normal equations vs gradient descent.",
                      ].map((hint) => (
                        <button
                          key={hint}
                          onClick={() => setInputQuery(hint)}
                          className="text-xs text-zinc-400 bg-zinc-800 hover:bg-zinc-700 px-2.5 py-1 rounded-full border border-zinc-700 transition-colors"
                        >
                          {hint}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {chatMessages.map((msg, i) => (
                  <div
                    key={i}
                    className={`p-4 rounded-lg space-y-2 ${
                      msg.role === "user"
                        ? "bg-zinc-800/80 ml-12 border border-zinc-700/60"
                        : "bg-indigo-950/20 mr-12 border border-indigo-500/30"
                    }`}
                  >
                    <div className="text-xs font-semibold text-zinc-400">
                      {msg.role === "user" ? "YOU" : "AI TUTOR"}
                    </div>
                    <p className="text-sm text-zinc-100 whitespace-pre-wrap">{msg.content}</p>

                    {/* Low-Evidence Refusal Alert */}
                    {msg.refused && (
                      <div className="flex items-center gap-2 p-2 bg-amber-950/40 border border-amber-800/60 rounded text-xs text-amber-300">
                        <AlertTriangle className="w-4 h-4 shrink-0" />
                        <span>Low-evidence guardrail triggered: insufficient grounding in project materials.</span>
                      </div>
                    )}

                    {/* Citation Chips */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="pt-2 flex flex-wrap gap-2 border-t border-zinc-800">
                        {msg.citations.map((c, cIdx) => (
                          <div
                            key={cIdx}
                            className="flex items-center gap-1.5 text-xs bg-zinc-900 border border-zinc-700 text-indigo-300 px-2 py-1 rounded"
                          >
                            <FileText className="w-3.5 h-3.5" />
                            <span>
                              {c.filename} • Page {c.page_number}
                            </span>
                            {c.similarity && (
                              <span className="text-[10px] text-zinc-500">
                                ({Math.round(c.similarity * 100)}%)
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Chat Input Bar */}
              <div className="flex items-center gap-2 pt-2 border-t border-zinc-800">
                <input
                  type="text"
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendTutorMessage()}
                  placeholder="Ask a question grounded in your course materials..."
                  className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                  disabled={isStreaming}
                />
                <Button onClick={handleSendTutorMessage} disabled={isStreaming || !inputQuery.trim()} size="sm">
                  {isStreaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === "quiz" && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Adaptive Assessment Engine</CardTitle>
                <CardDescription>Generates questions dynamically weighted toward weak concepts with rubric grading</CardDescription>
              </div>
              <Button onClick={handleStartQuiz} disabled={quizLoading} size="sm" className="gap-2">
                {quizLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                {currentQuiz ? "Start New Drill" : "Start Diagnostic Quiz"}
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              {!currentQuiz ? (
                <div className="text-center p-8 border border-dashed border-zinc-800 rounded-xl space-y-3">
                  <Sparkles className="w-8 h-8 text-indigo-400 mx-auto" />
                  <h4 className="text-base font-semibold text-white">No Quiz in Progress</h4>
                  <p className="text-sm text-zinc-400 max-w-md mx-auto">
                    Click "Start Diagnostic Quiz" above. The adaptive engine will select concepts marked for attention (like Gradient Descent) and present diagnostic questions.
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-zinc-900 border border-zinc-800">
                    <span className="text-sm text-zinc-300">
                      Status: <strong className="text-white">{currentQuiz.status}</strong>
                    </span>
                    {currentQuiz.status === "COMPLETED" && (
                      <Badge variant="success">Final Score: {Math.round((currentQuiz.score || 0) * 100)}%</Badge>
                    )}
                  </div>

                  {currentQuiz.questions.map((q, idx) => {
                    const answered = submittedAnswers[q.id];
                    return (
                      <div key={q.id} className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
                        <div className="flex items-center justify-between">
                          <Badge variant="outline">
                            Question {idx + 1} of {currentQuiz.questions.length} • {q.question_type}
                          </Badge>
                          {answered && (
                            <span className={answered.score >= 0.7 ? "text-xs text-emerald-400 font-medium" : "text-xs text-amber-400 font-medium"}>
                              Score: {Math.round(answered.score * 100)}%
                            </span>
                          )}
                        </div>
                        <p className="text-sm font-medium text-zinc-100">{q.prompt}</p>

                        {/* MCQ Options */}
                        {q.question_type === "MCQ" && q.options && (
                          <div className="space-y-2 pt-1">
                            {q.options.map((opt, oIdx) => (
                              <label
                                key={oIdx}
                                className={`flex items-start gap-3 p-3 rounded-lg border text-sm cursor-pointer transition-colors ${
                                  userAnswers[q.id] === opt
                                    ? "bg-indigo-950/30 border-indigo-500/50 text-indigo-200"
                                    : "bg-zinc-900 border-zinc-800 text-zinc-300 hover:bg-zinc-800/60"
                                }`}
                              >
                                <input
                                  type="radio"
                                  name={`question-${q.id}`}
                                  checked={userAnswers[q.id] === opt}
                                  onChange={() => setUserAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                                  className="mt-0.5"
                                  disabled={currentQuiz.status === "COMPLETED"}
                                />
                                <span>{opt}</span>
                              </label>
                            ))}
                          </div>
                        )}

                        {/* Open-Ended Textarea */}
                        {q.question_type === "OPEN_ENDED" && (
                          <textarea
                            rows={3}
                            value={userAnswers[q.id] || ""}
                            onChange={(e) => setUserAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                            placeholder="Type your explanation here..."
                            className="w-full rounded-md border border-zinc-700 bg-zinc-900 p-3 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                            disabled={currentQuiz.status === "COMPLETED"}
                          />
                        )}

                        {/* Submit single answer button */}
                        {currentQuiz.status !== "COMPLETED" && !answered && (
                          <Button size="sm" onClick={() => handleSubmitAnswer(q.id)} disabled={!userAnswers[q.id]}>
                            Submit Answer
                          </Button>
                        )}

                        {/* Feedback Banner */}
                        {answered && (
                          <div className="p-3 bg-zinc-900/80 border border-zinc-800 rounded-lg text-xs space-y-1">
                            <div className="font-semibold text-zinc-300">Feedback:</div>
                            <p className="text-zinc-400">{answered.feedback}</p>
                          </div>
                        )}
                      </div>
                    );
                  })}

                  {currentQuiz.status !== "COMPLETED" && (
                    <Button onClick={handleCompleteQuiz} className="w-full" disabled={quizLoading}>
                      {quizLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Award className="w-4 h-4 mr-2" />}
                      Finalize Quiz & Update Mastery
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {activeTab === "mastery" && (
          <Card>
            <CardHeader>
              <CardTitle>Mastery & Growth Trajectory</CardTitle>
              <CardDescription>Continuous estimation computed across all assessments and study interactions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-zinc-800/30 border border-zinc-800 text-center">
                  <div className="text-2xl font-bold text-emerald-400">
                    {masteryList.filter((m) => m.trend === "IMPROVING").length}
                  </div>
                  <div className="text-xs text-zinc-400 mt-1">Concepts Improving</div>
                </div>
                <div className="p-4 rounded-lg bg-zinc-800/30 border border-zinc-800 text-center">
                  <div className="text-2xl font-bold text-blue-400">
                    {masteryList.filter((m) => m.trend === "STABLE").length}
                  </div>
                  <div className="text-xs text-zinc-400 mt-1">Concepts Stable</div>
                </div>
                <div className="p-4 rounded-lg bg-zinc-800/30 border border-zinc-800 text-center">
                  <div className="text-2xl font-bold text-amber-400">
                    {masteryList.filter((m) => m.trend === "ATTENTION").length}
                  </div>
                  <div className="text-xs text-zinc-400 mt-1">Requiring Attention</div>
                </div>
              </div>

              <div className="space-y-4 pt-4">
                <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Concept Cards</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {masteryList.map((m) => {
                    const scorePct = Math.round(m.mastery_score * 100);
                    return (
                      <div key={m.concept_id} className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
                        <div className="flex items-center justify-between">
                          <h5 className="font-semibold text-white text-sm">{m.name}</h5>
                          <Badge variant={m.trend === "IMPROVING" ? "success" : m.trend === "ATTENTION" ? "warning" : "secondary"}>
                            {m.trend}
                          </Badge>
                        </div>
                        {m.description && <p className="text-xs text-zinc-400">{m.description}</p>}
                        <div className="space-y-1">
                          <div className="flex justify-between text-xs text-zinc-400">
                            <span>Mastery Level</span>
                            <span className="font-bold text-white">{scorePct}%</span>
                          </div>
                          <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                m.trend === "ATTENTION" ? "bg-amber-500" : "bg-emerald-500"
                              }`}
                              style={{ width: `${scorePct}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
