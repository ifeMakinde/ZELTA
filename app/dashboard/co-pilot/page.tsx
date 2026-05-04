"use client";

import React, { useMemo, useState } from "react";
import PageHeader from "@/components/PageHeader";
import { Activity, MessageSquare, Send, Sparkles } from "lucide-react";
import { useWallet, useCopilot, useStress, useBayseSignals } from "@/hooks/zelta";
import type { CopilotMessage, CopilotResponse } from "@/types/zelta";

function page() {
  const wallet = useWallet();
  const stress = useStress();
  const bayse = useBayseSignals();
  const copilot = useCopilot();

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [lastResponse, setLastResponse] = useState<CopilotResponse | null>(null);

  const stats = useMemo(
    () => [
      {
        title: "Free Cash",
        value: wallet.data ? `₦${wallet.data.free_cash.toLocaleString()}` : "Loading...",
        color: "text-gray-800",
      },
      {
        title: "Stress Index",
        value: stress.data ? `${Math.round(stress.data.combined_index)}/100` : "Loading...",
        color: stress.data
          ? stress.data.combined_index > 60
            ? "text-red-500"
            : stress.data.combined_index > 30
            ? "text-yellow-500"
            : "text-emerald-500"
          : "text-gray-500",
      },
      {
        title: "Bayse Fear",
        value: bayse.data ? `${Math.round(bayse.data.stress.raw_crowd_stress)}%` : "Loading...",
        color: "text-orange-400",
      },
    ],
    [wallet.data, stress.data, bayse.data],
  );

  const handleAsk = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) return;

    const userMessage: CopilotMessage = {
      role: "user",
      content: trimmedQuestion,
      timestamp: new Date().toISOString(),
    };

    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setQuestion("");

    const response = await copilot.runCopilot({
      question: trimmedQuestion,
      conversation_history: nextMessages,
      context: {
        free_cash: wallet.data?.free_cash ?? 0,
        stress_index: stress.data?.combined_index ?? 0,
        bayse_fear: bayse.data?.stress?.raw_crowd_stress ?? 0,
      },
    });

    if (response) {
      setLastResponse(response);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.answer,
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  return (
    <div className="px-3 lg:px-0">
      <PageHeader
        title="BQ Co-pilot"
        description="Ask anything about your financial decisions"
      />

      <div className="grid gap-4 lg:grid-cols-[1.3fr_0.9fr] mt-6">
        <section className="bg-white border-2 border-gray-100 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-emerald-100 rounded-full p-3">
              <MessageSquare className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h2 className="text-gray-900 font-bold text-lg md:text-xl">BQ Co-pilot</h2>
              <p className="text-gray-500 text-sm md:text-base">
                Get actionable guidance from ZELTA's behavioral decision engine.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {messages.length === 0 ? (
              <div className="rounded-3xl border-2 border-dashed border-gray-200 p-6 text-center text-sm text-gray-500">
                Ask a question and the co-pilot will respond with your best next move.
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={`rounded-3xl p-4 ${
                      message.role === "assistant"
                        ? "bg-slate-50 border border-slate-200"
                        : "bg-emerald-50 border border-emerald-200 self-end"
                    }`}
                  >
                    <p className="text-xs uppercase tracking-[0.18em] text-gray-400 mb-2">
                      {message.role === "assistant" ? "Co-pilot" : "You"}
                    </p>
                    <p className="text-gray-800 whitespace-pre-line">{message.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <form onSubmit={handleAsk} className="mt-6">
            <label className="sr-only" htmlFor="copilot-question">
              Type your question
            </label>
            <div className="grid gap-3 md:grid-cols-[1fr_auto]">
              <input
                id="copilot-question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What should I do with my savings this month?"
                className="bg-gray-100 w-full h-14 px-4 rounded-2xl outline-none border border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100"
              />
              <button
                type="submit"
                disabled={copilot.loading}
                className="h-14 rounded-2xl bg-emerald-500 px-6 text-white font-semibold transition hover:bg-emerald-400 disabled:opacity-50"
              >
                <Send className="w-4 h-4 inline-block mr-2" />
                Ask
              </button>
            </div>
          </form>

          {copilot.error && (
            <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {copilot.error}
            </div>
          )}

          {lastResponse?.context_pills?.length ? (
            <div className="mt-5 rounded-3xl border border-gray-100 bg-slate-50 p-4">
              <h3 className="text-sm font-semibold text-gray-800 mb-3">Response Summary</h3>
              <div className="grid gap-3 sm:grid-cols-2">
                {lastResponse.context_pills.map((pill, index) => (
                  <div key={index} className="rounded-2xl bg-white border border-gray-200 p-3">
                    <p className="text-xs text-gray-500">{pill.label}</p>
                    <p className="mt-1 text-sm font-semibold text-gray-900">{pill.value}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </section>

        <aside className="space-y-4">
          <div className="bg-white border-2 border-gray-100 rounded-2xl p-5 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-slate-100 rounded-full p-3">
                <Sparkles className="w-5 h-5 text-slate-700" />
              </div>
              <div>
                <h3 className="text-gray-900 font-bold">Your current picture</h3>
                <p className="text-gray-500 text-sm">Live signals that shape your co-pilot answers.</p>
              </div>
            </div>

            <div className="grid gap-3">
              {stats.map((stat) => (
                <div key={stat.title} className="rounded-2xl border border-gray-200 bg-slate-50 p-4">
                  <p className="text-sm text-gray-500">{stat.title}</p>
                  <p className={`mt-1 font-semibold text-lg ${stat.color}`}>{stat.value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border-2 border-gray-100 rounded-2xl p-5 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-slate-100 rounded-full p-3">
                <Activity className="w-5 h-5 text-slate-700" />
              </div>
              <div>
                <h3 className="text-gray-900 font-bold">How Co-pilot works</h3>
              </div>
            </div>
            <p className="text-sm leading-6 text-gray-600">
              ZELTA sends your question to the live BQ Co-pilot endpoint. The answer is generated from your user signals, portfolio context, and historical conversation.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default page;
