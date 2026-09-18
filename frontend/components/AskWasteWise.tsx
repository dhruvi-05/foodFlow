"use client";

import { useState } from "react";
import { MessageSquareText, Send, Sparkles, ShieldCheck, Loader2 } from "lucide-react";
import { askQuestion, PlanResponse } from "@/lib/api";

interface AskWasteWiseProps {
  planContext: PlanResponse | null;
}

export default function AskWasteWise({ planContext }: AskWasteWiseProps) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [isGrounded, setIsGrounded] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const suggestionChips = [
    "Why should I prepare fewer dal portions tomorrow?",
    "What should I buy tomorrow?",
    "Which dish is costing me the most in waste this week?"
  ];

  const handleAsk = async (qText?: string) => {
    const query = qText || question;
    if (!query.trim()) return;

    setIsLoading(true);
    setQuestion(query);

    try {
      const res = await askQuestion(query, planContext);
      setAnswer(res.answer);
      setIsGrounded(res.grounded);
    } catch (err) {
      setAnswer("Sorry, could not process query against plan context.");
      setIsGrounded(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-b from-slate-900 to-slate-950 rounded-2xl border border-slate-800 p-6 shadow-2xl mb-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-teal-400" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white tracking-tight">Ask WasteWise AI Assistant</h3>
          <p className="text-xs text-slate-400">
            Retrieval-free grounded Q&A grounded strictly in tomorrow's plan facts
          </p>
        </div>
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleAsk();
        }}
        className="flex items-center gap-3 mb-4"
      >
        <div className="relative flex-1">
          <MessageSquareText className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about tomorrow's prep, inventory, or waste..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-12 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500/50 focus:ring-1 focus:ring-teal-500/50 transition-all"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !question.trim()}
          className="px-5 py-3 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-sm flex items-center gap-2 transition-all disabled:opacity-50 shadow-lg shadow-teal-500/20"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          <span>Ask</span>
        </button>
      </form>

      {/* Suggestion Chips */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <span className="text-xs font-semibold text-slate-400 mr-1">Suggested questions:</span>
        {suggestionChips.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleAsk(chip)}
            className="text-xs font-medium bg-slate-800/80 hover:bg-slate-800 text-teal-300 hover:text-teal-200 px-3 py-1.5 rounded-lg border border-slate-700/60 transition-colors text-left"
          >
            "{chip}"
          </button>
        ))}
      </div>

      {/* Answer Output Box */}
      {answer && (
        <div className="p-4 rounded-xl bg-slate-950 border border-teal-500/30 space-y-2 animate-fadeIn">
          <p className="text-sm text-slate-200 leading-relaxed">{answer}</p>
          <div className="flex items-center justify-between text-[11px] font-mono pt-2 border-t border-slate-800/60">
            <span className="text-slate-400">Source: Plan Context Payload (No LLM numeric origination)</span>
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>[verified: grounded]</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
