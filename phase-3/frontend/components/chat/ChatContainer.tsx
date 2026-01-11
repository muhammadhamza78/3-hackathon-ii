/**
 * ChatContainer Component
 * Main chat interface with messages and input - Professional UI.
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { ChatMessage } from "./ChatMessage"; // Component for rendering a single message
import { ChatInput } from "./ChatInput"; // Input box component
import { sendChatMessage } from "@/lib/chat-api"; // API call helper
import type { Message as ChatMessageType } from "@/types/chat"; // Correct type import

interface ChatContainerProps {
  userId: number;
  isOpen: boolean;
  onClose: () => void;
  onTaskUpdate?: () => void;
}

// Quick action suggestions for the user
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

  // Handle sending a message
  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    // Add user message immediately to UI
    const userMessage: ChatMessageType = {
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Use env variable for backend URL (production-safe)
      const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

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

      // Update task list if chatbot affects tasks
      if (onTaskUpdate) onTaskUpdate();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to send message";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Start a new chat
  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  // Handle quick action button clicks
  const handleQuickAction = (prompt: string) => {
    if (prompt.endsWith(": ")) {
      // For "Add Task" type actions
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
      {/* Header */}
      <div
        className="flex items-center justify-between px-5 py-4 flex-shrink-0"
        style={{
          background: "linear-gradient(135deg, #e08b3d 0%, #d17a2f 100%)",
        }}
      >
        <div className="flex items-center gap-3">
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
          <button onClick={handleNewChat} className="p-2 rounded-xl hover:bg-white/20 transition-colors" title="New Chat">
            {/* Icon */}
          </button>
          <button onClick={onClose} className="p-2 rounded-xl hover:bg-white/20 transition-colors" title="Close">
            {/* Icon */}
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ background: "var(--background)" }}>
        {messages.length === 0 && (
          <div className="text-center py-6">
            <h3 className="font-bold text-lg mb-2">Hello! I&apos;m your Task Assistant</h3>
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: "linear-gradient(135deg, #e08b3d 0%, #d17a2f 100%)" }}>
                {/* Typing indicator */}
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="mx-auto max-w-[80%] rounded-xl p-3 text-center" style={{ background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.3)" }}>
            <p className="text-sm text-red-500 font-medium">{error}</p>
            <button onClick={() => setError(null)} className="text-xs text-red-400 hover:text-red-300 mt-1 underline">Dismiss</button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
