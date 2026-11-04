"use client";

import React, { useState } from "react";
import { Sparkles, X, Send, Bot, User, ArrowRight, CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolUsed?: string;
  suggestedActions?: string[];
}

interface AiAdvisorDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AiAdvisorDrawer: React.FC<AiAdvisorDrawerProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Welcome to the **Carbonomics v3 AI Carbon Advisor**. I have real-time access to your fleet telemetry, physics models, ML forecaster, and cloud emission matrix.\n\nHow can I help optimize your carbon footprint today?",
      suggestedActions: [
        "What is our total carbon footprint?",
        "Which device produces the most emissions?",
        "Why did emissions spike today?",
        "How much carbon can we save?",
        "Which cloud region has the cleanest electricity?",
      ],
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: Message = { role: "user", content: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await api.advisorChat(textToSend);
      const assistantMsg: Message = {
        role: "assistant",
        content: res.answer,
        toolUsed: res.tool_used,
        suggestedActions: res.suggested_actions,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Unable to complete query: ${err.message || "Backend unreachable"}.`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-lg h-full bg-carbon-subtle border-l border-carbon-border flex flex-col shadow-2xl">
        {/* Drawer Header */}
        <div className="p-4 border-b border-carbon-border flex items-center justify-between bg-carbon-card/70">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-carbon-primary/20 border border-carbon-primary/30 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-carbon-primary" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-carbon-text">AI Carbon Advisor</h2>
              <p className="text-[11px] text-carbon-muted">Data-Grounded Copilot • GSF-SCI v2.1</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-carbon-border text-carbon-muted hover:text-carbon-text transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Conversation Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 text-sm ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.role === "assistant" && (
                <div className="w-7 h-7 rounded-lg bg-carbon-primary/20 border border-carbon-primary/40 flex-shrink-0 flex items-center justify-center mt-0.5">
                  <Bot className="w-4 h-4 text-carbon-primary" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 leading-relaxed ${
                  msg.role === "user"
                    ? "bg-carbon-primary text-carbon-bg font-medium"
                    : "bg-carbon-card border border-carbon-border text-carbon-text"
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {msg.toolUsed && (
                  <div className="mt-2.5 pt-2 border-t border-carbon-border/50 text-[10px] text-carbon-dim flex items-center gap-1.5 font-mono">
                    <CheckCircle2 className="w-3 h-3 text-carbon-primary" />
                    Verified via `{msg.toolUsed}()`
                  </div>
                )}

                {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                  <div className="mt-3 pt-2 space-y-1.5">
                    <div className="text-[11px] font-semibold text-carbon-muted uppercase tracking-wider">
                      Suggested Questions:
                    </div>
                    {msg.suggestedActions.map((action, actIdx) => (
                      <button
                        key={actIdx}
                        onClick={() => handleSend(action)}
                        className="w-full text-left text-xs px-2.5 py-1.5 rounded-lg bg-carbon-subtle hover:bg-carbon-card border border-carbon-border/70 text-carbon-primary flex items-center justify-between transition-colors"
                      >
                        <span>{action}</span>
                        <ArrowRight className="w-3 h-3 opacity-60" />
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {msg.role === "user" && (
                <div className="w-7 h-7 rounded-lg bg-carbon-card border border-carbon-border flex-shrink-0 flex items-center justify-center mt-0.5">
                  <User className="w-4 h-4 text-carbon-muted" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 text-sm">
              <div className="w-7 h-7 rounded-lg bg-carbon-primary/20 flex-shrink-0 flex items-center justify-center">
                <Bot className="w-4 h-4 text-carbon-primary" />
              </div>
              <div className="bg-carbon-card border border-carbon-border px-4 py-2.5 rounded-2xl text-xs text-carbon-muted flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-carbon-primary animate-ping" />
                Querying database telemetry and computing SCI physics models...
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-carbon-border bg-carbon-card/50">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about fleet emissions, models, or cloud..."
              className="flex-1 bg-carbon-bg border border-carbon-border rounded-xl px-4 py-2.5 text-sm text-carbon-text placeholder:text-carbon-dim focus:outline-none focus:border-carbon-primary transition-colors"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-4 py-2.5 rounded-xl bg-carbon-primary text-carbon-bg font-semibold text-sm hover:bg-carbon-primaryHover disabled:opacity-50 transition-colors flex items-center justify-center shadow-md shadow-carbon-primary/20"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

