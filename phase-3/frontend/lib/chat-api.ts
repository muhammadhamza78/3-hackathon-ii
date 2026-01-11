/**
 * Chat API Client
 * Functions for interacting with the chat API.
 *
 * Spec Reference: specs/phase-3-chatbot-spec.md
 */

import { apiGet, apiPost, apiDelete } from "@/lib/api";
import type {
  ChatRequest,
  ChatResponse,
  Conversation,
  ConversationListResponse,
} from "@/types/chat";

/**
 * Send a chat message to the AI assistant.
 */
export async function sendChatMessage(
  userId: number,
  request: ChatRequest
): Promise<ChatResponse> {
  const response = await apiPost(`/api/v1/chat`, request);

  if (!response.ok) {
    if (response.status === 429) {
      throw new Error("Rate limit exceeded. Please wait a moment.");
    }
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to send message");
  }

  return response.json();
}

/**
 * Get list of user's conversations.
 */
export async function getConversations(
  userId: number
): Promise<ConversationListResponse> {
  const response = await apiGet(`/api/v1/conversations`);

  if (!response.ok) {
    throw new Error("Failed to load conversations");
  }

  return response.json();
}

/**
 * Get a specific conversation with all messages.
 */
export async function getConversation(
  userId: number,
  conversationId: string
): Promise<Conversation> {
  const response = await apiGet(
    `/api/v1/conversations/${conversationId}`
  );

  if (!response.ok) {
    throw new Error("Failed to load conversation");
  }

  return response.json();
}

/**
 * Delete a conversation.
 */
export async function deleteConversation(
  userId: number,
  conversationId: string
): Promise<void> {
  const response = await apiDelete(
    `/api/v1/conversations/${conversationId}`
  );

  if (!response.ok) {
    throw new Error("Failed to delete conversation");
  }
}