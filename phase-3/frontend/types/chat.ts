// types/chat.ts

/**
 * Chat request payload
 */
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

/**
 * Chat response from the API
 */
export interface ChatResponse {
  response: string;
  conversation_id: string;
}

/**
 * Individual message in a conversation
 */
export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

/**
 * ChatMessage alias for Message (for backward compatibility)
 */
export type ChatMessage = Message;

/**
 * Full conversation with all messages
 */
export interface Conversation {
  id: string;
  messages: Message[];
  created_at: string;
}

/**
 * Conversation summary for list view
 */
export interface ConversationSummary {
  id: string;
  preview: string;
  created_at: string;
}

/**
 * Response from list conversations endpoint
 */
export interface ConversationListResponse {
  conversations: ConversationSummary[];
}
