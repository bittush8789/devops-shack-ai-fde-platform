import React, { useState, useEffect, useRef } from "react";
import { request, URLs } from "./api.js";
import "./AIWidget.css";

const QUICK_PROMPTS = [
  "What switches does the AI Mechanical Keyboard use?",
  "How much for 3 CloudOps Headsets with promo DEVOPS10?",
  "Which microservice is built in Java and what does it do?",
  "What kubectl commands are printed on the desk mat?",
  "What are the return and warranty policies?",
];

function formatText(text) {
  if (!text) return "";
  // Simple markdown conversion for bold, code, headers, and breaks
  return text
    .replace(/### (.*)/g, "<h3>$1</h3>")
    .replace(/#### (.*)/g, "<h4>$1</h4>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`(.*?)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br/>");
}

export default function AIWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I am your **AI Assistant**, powered by **FastAPI, OpenAI & Chroma DB RAG**.\n\nAsk me about internal product specs, pricing quotes, discount codes, or system architecture!",
      tag: "Ready • Chroma DB RAG",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (open) {
      scrollToBottom();
    }
  }, [messages, open]);

  async function handleSend(textToSend) {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // Build history payload (last 6 messages)
      const history = messages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await request(`${URLs.assistant}/assistant/chat`, {
        method: "POST",
        body: JSON.stringify({ message: text, history }),
      });

      let tag = res.mode === "openai" ? `Live OpenAI (${res.model})` : "Chroma DB RAG";
      if (res.guardrails?.blocked) {
        tag = `🛡️ Guardrail Blocked (Risk: ${(res.guardrails.risk_score * 100).toFixed(0)}%)`;
      } else if (res.guardrails?.flagged) {
        tag = `🔒 PII Redacted • Protected`;
      } else if (res.tools_called && res.tools_called.length > 0) {
        tag += ` • Tool: ${res.tools_called[0].tool}`;
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.reply || "I couldn't process that request.",
          tag,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `⚠️ Unable to connect to AI Assistant service (${err.message}). Ensure the AI service is running on port 8088.`,
          tag: "Connection Error",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function clearChat() {
    setMessages([
      {
        role: "assistant",
        content: "Chat history cleared. How can I help you with products or pricing?",
        tag: "Chroma DB RAG",
      },
    ]);
  }

  return (
    <>
      {/* Floating Widget Trigger Button */}
      <button
        className="ai-widget-trigger"
        onClick={() => setOpen(!open)}
        title="Open AI Assistant"
        aria-label="Open AI Assistant"
      >
        <span className="bot-avatar">🤖</span>
        <span>Ask AI Assistant</span>
        <span className="ai-widget-badge"></span>
      </button>

      {/* Floating Chat Panel */}
      {open && (
        <div className="ai-widget-panel">
          {/* Header */}
          <div className="ai-widget-header">
            <div className="ai-header-left">
              <div className="ai-header-icon">🤖</div>
              <div className="ai-header-titles">
                <strong>DevOps Shack AI Assistant</strong>
                <small>Product Specs, Pricing & RAG</small>
              </div>
            </div>
            <div className="ai-header-actions">
              <button
                className="ai-icon-btn"
                onClick={clearChat}
                title="Clear Chat"
              >
                ↺
              </button>
              <button
                className="ai-icon-btn"
                onClick={() => setOpen(false)}
                title="Close"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Quick Prompt Chips */}
          <div className="ai-quick-chips">
            {QUICK_PROMPTS.map((q) => (
              <button
                key={q}
                className="ai-chip"
                onClick={() => handleSend(q)}
              >
                {q}
              </button>
            ))}
          </div>

          {/* Messages */}
          <div className="ai-messages-list">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`ai-msg ${m.role === "user" ? "user" : "bot"}`}
              >
                <div className="ai-msg-avatar">
                  {m.role === "user" ? "👤" : "🤖"}
                </div>
                <div className="ai-bubble">
                  <div
                    dangerouslySetInnerHTML={{ __html: formatText(m.content) }}
                  />
                  {m.tag && <span className="ai-tag">{m.tag}</span>}
                </div>
              </div>
            ))}

            {loading && (
              <div className="ai-msg bot">
                <div className="ai-msg-avatar">🤖</div>
                <div className="ai-typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <form
            className="ai-input-wrap"
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
          >
            <input
              type="text"
              placeholder="Ask about products, pricing, specs..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}
