/**
 * ChatContainer Component
 * Main chat interface with messages and input - Professional UI.
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { sendChatMessage } from "@/lib/chat-api";
import type { ChatMessage as ChatMessageType } from "@/types/chat";

interface ChatContainerProps {
  userId: number;
  isOpen: boolean;
  onClose: () => void;
  onTaskUpdate?: () => void;
}

// Quick action suggestions
const quickActions = [
  { label: "Add Task", prompt: "Add a task: " },
  { label: "Show All", prompt: "Show all my tasks" },
  { label: "Pending", prompt: "Show pending tasks" },
  { label: "Completed", prompt: "Show completed tasks" },
];

export function ChatContainer({ userId, isOpen, onClose, onTaskUpdate }: ChatContainerProps) {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    // Add user message immediately
    const userMessage: ChatMessageType = {
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(userId, {
        message: content,
        conversation_id: conversationId || undefined,
      });

      setConversationId(response.conversation_id);

      // Add assistant response
      const assistantMessage: ChatMessageType = {
        role: "assistant",
        content: response.response,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Refresh task list after every message (chatbot may have added/edited/deleted tasks)
      if (onTaskUpdate) {
        onTaskUpdate();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to send message";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  const handleQuickAction = (prompt: string) => {
    if (prompt.endsWith(": ")) {
      // For "Add Task", just populate input - handled in ChatInput
      const event = new CustomEvent("chatQuickAction", { detail: prompt });
      window.dispatchEvent(event);
    } else {
      handleSendMessage(prompt);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed bottom-20 right-4 w-[400px] h-[550px] rounded-3xl shadow-2xl flex flex-col overflow-hidden z-50 sm:w-[380px]"
      style={{
        background: "var(--card-bg)",
        border: "1px solid var(--card-border)",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(0, 0, 0, 0.05)",
      }}
    >
      {/* Header - Gradient Style */}
      <div
        className="flex items-center justify-between px-5 py-4 flex-shrink-0"
        style={{
          background: "linear-gradient(135deg, #e08b3d 0%, #d17a2f 100%)",
        }}
      >
        <div className="flex items-center gap-3">
          {/* Bot Avatar */}
          <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <span className="font-bold text-white text-base">Task Assistant</span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
              <span className="text-white/80 text-xs">Online</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleNewChat}
            className="p-2 rounded-xl hover:bg-white/20 transition-colors"
            title="New Chat"
          >
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-white/20 transition-colors"
            title="Close"
          >
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ background: "var(--background)" }}>
        {messages.length === 0 && (
          <div className="text-center py-6">
            {/* Welcome Icon */}
            <div
              className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center mb-4"
              style={{ background: "linear-gradient(135deg, #e08b3d 0%, #d17a2f 100%)" }}
            >
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 className="font-bold text-lg mb-2" style={{ color: "var(--foreground)" }}>
              Hello! I&apos;m your Task Assistant
            </h3>
            <p className="text-sm mb-6" style={{ color: "var(--foreground)", opacity: 0.6 }}>
              I can help you manage your tasks. Try these:
            </p>

            {/* Quick Actions */}
            <div className="flex flex-wrap gap-2 justify-center">
              {quickActions.map((action) => (
                <button
                  key={action.label}
                  onClick={() => handleQuickAction(action.prompt)}
                  className="px-4 py-2 rounded-full text-sm font-medium transition-all hover:scale-105"
                  style={{
                    background: "var(--accent-bg)",
                    color: "#e08b3d",
                    border: "1px solid #e08b3d40",
                  }}
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2">
              {/* Bot Avatar Mini */}
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ background: "linear-gradient(135deg, #e08b3d 0%, #d17a2f 100%)" }}
              >
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div
                className="px-4 py-3 rounded-2xl rounded-tl-sm"
                style={{ background: "var(--accent-bg)" }}
              >
                <div className="flex space-x-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#e08b3d] animate-bounce" style={{ animationDelay: "0ms" }}></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-[#e08b3d] animate-bounce" style={{ animationDelay: "150ms" }}></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-[#e08b3d] animate-bounce" style={{ animationDelay: "300ms" }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div
            className="mx-auto max-w-[80%] rounded-xl p-3 text-center"
            style={{ background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.3)" }}
          >
            <p className="text-sm text-red-500 font-medium">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-xs text-red-400 hover:text-red-300 mt-1 underline"
            >
              Dismiss
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
