/**
 * ChatInput Component
 * Text input for sending chat messages - Professional style.
 */

"use client";

import { useState, KeyboardEvent, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Listen for quick action events from ChatContainer
  useEffect(() => {
    const handleQuickAction = (event: CustomEvent<string>) => {
      setInput(event.detail);
      textareaRef.current?.focus();
    };

    window.addEventListener("chatQuickAction", handleQuickAction as EventListener);
    return () => {
      window.removeEventListener("chatQuickAction", handleQuickAction as EventListener);
    };
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 100) + "px";
    }
  }, [input]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      className="p-4 border-t"
      style={{
        borderColor: "var(--card-border)",
        background: "var(--card-bg)",
      }}
    >
      <div
        className="flex gap-3 items-end rounded-2xl p-2 transition-all"
        style={{
          background: "var(--input-bg)",
          border: "2px solid transparent",
        }}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={disabled}
          rows={1}
          maxLength={2000}
          className="flex-1 px-3 py-2 bg-transparent resize-none focus:outline-none min-h-[40px] text-sm"
          style={{
            color: "var(--input-text)",
          }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="p-3 rounded-xl text-white transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 flex-shrink-0"
          style={{
            background: input.trim()
              ? "linear-gradient(135deg, #e08b3d 0%, #d17a2f 100%)"
              : "var(--accent-bg)",
          }}
          aria-label="Send message"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            style={{ color: input.trim() ? "white" : "var(--foreground)" }}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>
      <p
        className="text-xs text-center mt-2"
        style={{ color: "var(--foreground)", opacity: 0.4 }}
      >
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
