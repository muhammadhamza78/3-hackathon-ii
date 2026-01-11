# Feature Specification: Todo AI Chatbot with MCP Server

**Feature Branch**: `003-ai-chatbot-mcp`
**Created**: 2026-01-10
**Status**: Draft
**Input**: User description: "Add an AI-powered natural language chatbot for task management using MCP server architecture. Users can add, list, complete, update, and delete tasks via natural language. Backend uses FastAPI + SQLModel + Neon PostgreSQL. Frontend uses ChatKit with domain allowlist."

## Overview

Phase-3 adds an AI-powered chatbot interface that allows users to manage their tasks through natural language conversations. The system uses Model Context Protocol (MCP) server architecture to expose task management tools to an AI agent powered by OpenAI Agents SDK.

### Architecture Components

1. **MCP Server**: Exposes task management tools (add_task, list_tasks, complete_task, update_task, delete_task) as stateless functions that interact with the database
2. **AI Agent**: OpenAI Agents SDK-based agent that interprets user intent and calls appropriate MCP tools
3. **Chat API**: New endpoint `POST /api/{user_id}/chat` for processing chat messages
4. **Conversation Persistence**: Database storage for chat history (stateless server, persistent state)
5. **ChatKit Frontend**: Chat interface integrated into the dashboard

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Task via Natural Language (Priority: P1)

Users need to create tasks by describing them in natural language, without using structured forms or specific syntax.

**Why this priority**: Task creation is the most fundamental operation. Users should be able to quickly add tasks by simply typing what they need to do.

**Independent Test**: Can be fully tested by opening the chat interface, typing a natural language request like "add task Title: Read book description: Daily 10 pages status: in progress", and verifying the task appears in the Personal tasks list.

**Acceptance Scenarios**:

1. **Given** user is on the dashboard with chat open, **When** user types "add task Title: Read book description: Daily 10 pages status: in progress", **Then** a new task is created with title "Read book", description "Daily 10 pages", and status "in_progress"
2. **Given** user types "create a task to buy groceries", **When** the message is sent, **Then** a task with title "buy groceries" is created with default status "pending"
3. **Given** user types "add task: finish project report by Friday", **When** processed, **Then** task is created with title "finish project report by Friday"
4. **Given** user adds a task via chat, **When** task creation succeeds, **Then** the chatbot confirms creation with task details
5. **Given** user tries to add a task with empty title, **When** processed, **Then** chatbot asks for clarification on what task to create

---

### User Story 2 - List Tasks via Natural Language (Priority: P1)

Users need to view their tasks by asking the chatbot, receiving a formatted list of their active tasks.

**Why this priority**: Viewing tasks is essential for task management and complements task creation.

**Independent Test**: Can be tested by having existing tasks, opening chat, typing "show my tasks" or "list all tasks", and verifying the chatbot returns a formatted list of active tasks.

**Acceptance Scenarios**:

1. **Given** user has active tasks, **When** user types "show my tasks", **Then** chatbot displays all active tasks with titles and statuses
2. **Given** user has no active tasks, **When** user types "list tasks", **Then** chatbot responds with "You have no active tasks"
3. **Given** user types "what are my pending tasks?", **When** processed, **Then** chatbot lists only tasks with pending status
4. **Given** user types "show completed tasks", **When** processed, **Then** chatbot lists tasks with completed status
5. **Given** user types "how many tasks do I have?", **When** processed, **Then** chatbot responds with task count

---

### User Story 3 - Complete Task via Natural Language (Priority: P2)

Users need to mark tasks as complete by referencing them in natural language.

**Why this priority**: Completing tasks is a core workflow action that users will perform frequently.

**Independent Test**: Can be tested by having a task "Read book", typing "complete the Read book task", and verifying the task status changes to completed.

**Acceptance Scenarios**:

1. **Given** task "Read book" exists, **When** user types "mark Read book as complete", **Then** task status changes to "completed" and chatbot confirms
2. **Given** task "Buy groceries" exists, **When** user types "I finished buying groceries", **Then** task status changes to "completed"
3. **Given** user types "complete task that doesn't exist", **When** processed, **Then** chatbot responds that task was not found
4. **Given** multiple tasks with similar names exist, **When** user tries to complete one, **Then** chatbot asks for clarification or completes the closest match
5. **Given** task is already completed, **When** user tries to complete it again, **Then** chatbot informs user task is already completed

---

### User Story 4 - Update Task via Natural Language (Priority: P2)

Users need to modify existing tasks by describing the changes in natural language.

**Why this priority**: Users need to update task details as requirements change.

**Independent Test**: Can be tested by having a task, typing "change the title of Read book to Read 2 chapters", and verifying the task title is updated.

**Acceptance Scenarios**:

1. **Given** task "Read book" exists, **When** user types "update Read book task title to Read daily", **Then** task title changes and chatbot confirms
2. **Given** task exists, **When** user types "change status of Read book to in progress", **Then** task status updates to "in_progress"
3. **Given** task exists, **When** user types "add description 'Must finish by Monday' to Read book task", **Then** task description is updated
4. **Given** task doesn't exist, **When** user tries to update it, **Then** chatbot responds that task was not found
5. **Given** user provides invalid status, **When** processed, **Then** chatbot asks for valid status (pending, in_progress, completed)

---

### User Story 5 - Delete Task via Natural Language (Priority: P2)

Users need to delete tasks by referencing them in natural language.

**Why this priority**: Users need to remove tasks that are no longer relevant.

**Independent Test**: Can be tested by having a task "Read book", typing "delete task Title: Read book description: Daily 10 pages status: in progress", and verifying the task is soft-deleted (moved to history).

**Acceptance Scenarios**:

1. **Given** task "Read book" exists, **When** user types "delete task Title: Read book description: Daily 10 pages status: in progress", **Then** task is soft-deleted and appears in History
2. **Given** task exists, **When** user types "remove the grocery task", **Then** task is soft-deleted
3. **Given** task doesn't exist, **When** user tries to delete it, **Then** chatbot responds that task was not found
4. **Given** user deletes a task, **When** deletion succeeds, **Then** chatbot confirms deletion and mentions it can be restored from History
5. **Given** user types "delete all my tasks", **When** processed, **Then** chatbot asks for confirmation before proceeding

---

### User Story 6 - Conversation Context (Priority: P3)

Users need the chatbot to understand context from the conversation for follow-up questions.

**Why this priority**: Natural conversations require context awareness for usability.

**Independent Test**: Can be tested by creating a task, then immediately typing "now mark it as complete" and verifying the chatbot understands the reference.

**Acceptance Scenarios**:

1. **Given** user just created task "Read book", **When** user types "mark it as complete", **Then** chatbot understands "it" refers to "Read book" and completes it
2. **Given** user asked "show my tasks", **When** user types "delete the first one", **Then** chatbot either completes the action or asks for clarification
3. **Given** conversation history exists, **When** user returns to chat later, **Then** previous conversation is visible
4. **Given** user starts new topic, **When** context is unclear, **Then** chatbot asks for clarification

---

### Edge Cases

- **Ambiguous Task Reference**: When user says "complete my task" but has multiple tasks, chatbot should list tasks and ask which one
- **Empty Message**: When user sends empty or whitespace-only message, chatbot should prompt for input
- **Very Long Message**: Messages over 2000 characters should be handled gracefully with appropriate error message
- **Rate Limiting**: Multiple rapid requests should be rate-limited to prevent abuse (10 requests/minute)
- **Invalid Status Values**: When user provides invalid status, chatbot should suggest valid options
- **Special Characters in Task Title**: Titles with special characters should be handled properly
- **Concurrent Modifications**: If task is modified via UI while chatbot processes, return current state
- **Network Timeout**: If AI agent times out, return graceful error message
- **Malformed Natural Language**: If intent cannot be determined, chatbot should ask for clarification

---

## Requirements *(mandatory)*

### Functional Requirements

#### MCP Server & Tools

- **FR-001**: System MUST implement an MCP server that exposes task management tools
- **FR-002**: MCP server MUST expose `add_task` tool accepting title (required), description (optional), status (optional, default: pending)
- **FR-003**: MCP server MUST expose `list_tasks` tool accepting optional status filter parameter
- **FR-004**: MCP server MUST expose `complete_task` tool accepting task identifier (title or id)
- **FR-005**: MCP server MUST expose `update_task` tool accepting task identifier and fields to update (title, description, status)
- **FR-006**: MCP server MUST expose `delete_task` tool accepting task identifier for soft delete
- **FR-007**: All MCP tools MUST be stateless and interact only with the database
- **FR-008**: All MCP tools MUST enforce user isolation (user can only access own tasks)
- **FR-009**: MCP tools MUST validate all inputs before database operations
- **FR-010**: MCP tools MUST return structured responses with success/failure status and relevant data

#### AI Agent

- **FR-011**: System MUST implement an AI agent using OpenAI Agents SDK
- **FR-012**: AI agent MUST be able to interpret natural language task management requests
- **FR-013**: AI agent MUST call appropriate MCP tools based on user intent
- **FR-014**: AI agent MUST handle ambiguous requests by asking clarifying questions
- **FR-015**: AI agent MUST provide human-readable responses summarizing actions taken
- **FR-016**: AI agent MUST handle multi-turn conversations with context awareness
- **FR-017**: AI agent MUST gracefully handle tool execution failures
- **FR-018**: AI agent MUST support the following intents: add_task, list_tasks, complete_task, update_task, delete_task, general_query

#### Chat API Endpoint

- **FR-019**: System MUST provide `POST /api/{user_id}/chat` endpoint for chat messages
- **FR-020**: Chat endpoint MUST accept JSON body with `message` field (string, required)
- **FR-021**: Chat endpoint MUST require JWT authentication
- **FR-022**: Chat endpoint MUST validate that authenticated user matches `user_id` in path
- **FR-023**: Chat endpoint MUST return JSON response with `response` field (string) and `conversation_id` (string)
- **FR-024**: Chat endpoint MUST be stateless (no server-side session state)
- **FR-025**: Chat endpoint MUST support optional `conversation_id` parameter to continue existing conversation
- **FR-026**: Chat endpoint MUST handle AI agent errors gracefully with user-friendly error messages

#### Conversation Persistence

- **FR-027**: System MUST persist conversations in the database
- **FR-028**: Conversation storage MUST include: id, user_id, messages (JSON array), created_at, updated_at
- **FR-029**: Each message in conversation MUST include: role (user/assistant), content (string), timestamp
- **FR-030**: Conversations MUST be isolated per user (user can only access own conversations)
- **FR-031**: System MUST support retrieving conversation history for context in multi-turn conversations
- **FR-032**: Conversation context window MUST be limited to last 20 messages to manage token usage

#### ChatKit Frontend Integration

- **FR-033**: Dashboard MUST include a chat interface component using ChatKit
- **FR-034**: Chat interface MUST display conversation history with user and assistant messages
- **FR-035**: Chat interface MUST allow typing and sending messages
- **FR-036**: Chat interface MUST show loading indicator while waiting for response
- **FR-037**: Chat interface MUST display error messages when requests fail
- **FR-038**: Chat interface MUST support scrolling through message history
- **FR-039**: Chat interface MUST auto-scroll to latest message
- **FR-040**: ChatKit MUST be configured with domain allowlist for security
- **FR-041**: Chat interface MUST be responsive and work on mobile devices
- **FR-042**: Chat interface MUST integrate with existing theme (light/dark mode)

#### Security & Performance

- **FR-043**: All chat endpoints MUST require authentication
- **FR-044**: Chat endpoint MUST implement rate limiting (10 requests per minute per user)
- **FR-045**: AI agent MUST NOT expose sensitive system information in responses
- **FR-046**: Message content MUST be sanitized before storage and display
- **FR-047**: Chat responses MUST complete within 30 seconds (timeout)
- **FR-048**: System MUST log chat interactions for debugging (excluding sensitive content)

---

### Key Entities

- **Conversation**: Represents a chat conversation between user and AI
  - Attributes: id (UUID), user_id (FK), messages (JSON), created_at, updated_at
  - Relationships: belongs to one User
  - Messages Array: [{role: "user"|"assistant", content: string, timestamp: datetime}]

- **ChatMessage** (Schema): Request/Response schemas for chat API
  - ChatRequest: message (string, required), conversation_id (string, optional)
  - ChatResponse: response (string), conversation_id (string), tool_calls (array, optional)

- **MCP Tool Schemas**:
  - AddTaskInput: title (string, required), description (string, optional), status (enum, optional)
  - ListTasksInput: status_filter (enum, optional)
  - CompleteTaskInput: task_identifier (string, required - title or id)
  - UpdateTaskInput: task_identifier (string, required), title (string, optional), description (string, optional), status (enum, optional)
  - DeleteTaskInput: task_identifier (string, required)
  - ToolResponse: success (boolean), message (string), data (object, optional)

---

## Technical Design

### Database Schema Changes

```sql
-- New table for conversation persistence
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    messages JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

### API Endpoints

| Method | Endpoint | Auth | Request Body | Response |
|--------|----------|------|--------------|----------|
| POST | /api/{user_id}/chat | JWT | `{message: string, conversation_id?: string}` | `{response: string, conversation_id: string}` |
| GET | /api/{user_id}/conversations | JWT | - | `{conversations: [{id, created_at, preview}]}` |
| GET | /api/{user_id}/conversations/{id} | JWT | - | `{id, messages, created_at}` |
| DELETE | /api/{user_id}/conversations/{id} | JWT | - | 204 |

### MCP Tool Definitions

```python
# Tool: add_task
{
    "name": "add_task",
    "description": "Create a new task for the user",
    "parameters": {
        "title": {"type": "string", "required": True},
        "description": {"type": "string", "required": False},
        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "default": "pending"}
    }
}

# Tool: list_tasks
{
    "name": "list_tasks",
    "description": "List all tasks for the user, optionally filtered by status",
    "parameters": {
        "status_filter": {"type": "string", "enum": ["pending", "in_progress", "completed", "all"], "default": "all"}
    }
}

# Tool: complete_task
{
    "name": "complete_task",
    "description": "Mark a task as completed",
    "parameters": {
        "task_identifier": {"type": "string", "required": True, "description": "Task title or ID"}
    }
}

# Tool: update_task
{
    "name": "update_task",
    "description": "Update an existing task",
    "parameters": {
        "task_identifier": {"type": "string", "required": True},
        "title": {"type": "string", "required": False},
        "description": {"type": "string", "required": False},
        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "required": False}
    }
}

# Tool: delete_task
{
    "name": "delete_task",
    "description": "Delete a task (soft delete - moves to history)",
    "parameters": {
        "task_identifier": {"type": "string", "required": True}
    }
}
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    ChatKit Component                      │    │
│  │  - Message display                                        │    │
│  │  - Input field                                            │    │
│  │  - Loading states                                         │    │
│  │  - Theme integration                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ POST /api/{user_id}/chat
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Chat API Router                         │    │
│  │  - JWT Authentication                                     │    │
│  │  - Rate Limiting                                          │    │
│  │  - Request Validation                                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                OpenAI Agents SDK Agent                    │    │
│  │  - Intent Recognition                                     │    │
│  │  - Tool Selection                                         │    │
│  │  - Response Generation                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     MCP Server                            │    │
│  │  ┌─────────┐ ┌───────────┐ ┌──────────────┐             │    │
│  │  │add_task │ │list_tasks │ │complete_task │             │    │
│  │  └─────────┘ └───────────┘ └──────────────┘             │    │
│  │  ┌───────────┐ ┌───────────┐                            │    │
│  │  │update_task│ │delete_task│                            │    │
│  │  └───────────┘ └───────────┘                            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              PostgreSQL (Neon)                            │    │
│  │  - tasks table (existing)                                 │    │
│  │  - users table (existing)                                 │    │
│  │  - conversations table (new)                              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks via chat with 95% intent recognition accuracy
- **SC-002**: Chat responses complete within 5 seconds for 95% of requests
- **SC-003**: All 5 MCP tools (add, list, complete, update, delete) work correctly via chat
- **SC-004**: Conversation history persists across browser sessions
- **SC-005**: Chat interface renders correctly on mobile (320px) and desktop (1920px)
- **SC-006**: Rate limiting prevents abuse (max 10 requests/minute enforced)
- **SC-007**: 100% of chat operations maintain user isolation (no cross-user data access)
- **SC-008**: Chat handles edge cases gracefully (empty input, long messages, network errors)
- **SC-009**: Theme toggle affects chat interface (light/dark mode support)
- **SC-010**: Zero regressions in existing Phase-2 functionality

---

## Assumptions

- OpenAI API key is available and configured for the AI agent
- Users have modern browsers supporting Fetch API and WebSocket (for ChatKit)
- Maximum conversation length is 100 messages before auto-archiving
- AI agent model: GPT-4 or equivalent for best intent recognition
- Response token limit: 500 tokens per response
- Conversation context: Last 20 messages included for context
- ChatKit npm package is available and compatible with Next.js 15

---

## Dependencies

- **OpenAI Agents SDK**: For AI agent implementation
- **ChatKit**: Frontend chat UI component library
- **Existing Auth**: Phase-2 JWT authentication system
- **Existing Database**: Phase-2 PostgreSQL with users and tasks tables
- **Existing Task API**: Phase-2 task CRUD endpoints (used as reference, MCP tools interact directly with DB)

---

## Out of Scope

- Voice input for chat
- File attachments in chat
- Real-time collaborative chat
- Chat export functionality
- Custom AI personality configuration
- Multi-language support
- Task scheduling via chat ("remind me tomorrow")
- Integration with external calendars
- Chat analytics dashboard
- Conversation summarization
- Push notifications for chat

---

## Environment Variables (New)

```
# OpenAI Configuration
OPENAI_API_KEY=sk-...                    # Required for AI agent
OPENAI_MODEL=gpt-4-turbo-preview         # Model for intent recognition

# Chat Configuration
CHAT_RATE_LIMIT=10                       # Requests per minute per user
CHAT_TIMEOUT_SECONDS=30                  # Max response time
CHAT_MAX_MESSAGE_LENGTH=2000             # Max characters per message
CHAT_CONTEXT_MESSAGES=20                 # Messages to include for context
```

---

## File Structure (New Files)

```
backend/
├── app/
│   ├── api/v1/
│   │   └── chat.py                 # NEW: Chat API router
│   ├── mcp/
│   │   ├── __init__.py             # NEW: MCP module init
│   │   ├── server.py               # NEW: MCP server implementation
│   │   └── tools/
│   │       ├── __init__.py         # NEW: Tools module init
│   │       ├── add_task.py         # NEW: add_task tool
│   │       ├── list_tasks.py       # NEW: list_tasks tool
│   │       ├── complete_task.py    # NEW: complete_task tool
│   │       ├── update_task.py      # NEW: update_task tool
│   │       └── delete_task.py      # NEW: delete_task tool
│   ├── agents/
│   │   ├── __init__.py             # NEW: Agents module init
│   │   └── task_agent.py           # NEW: OpenAI Agents SDK agent
│   ├── models/
│   │   └── conversation.py         # NEW: Conversation SQLModel
│   └── schemas/
│       └── chat.py                 # NEW: Chat request/response schemas

frontend/
├── app/
│   └── dashboard/
│       └── page.tsx                # MODIFIED: Add chat component
├── components/
│   └── chat/
│       ├── ChatContainer.tsx       # NEW: Main chat container
│       ├── ChatMessage.tsx         # NEW: Single message component
│       └── ChatInput.tsx           # NEW: Message input component
├── lib/
│   └── chat-api.ts                 # NEW: Chat API client
└── types/
    └── chat.ts                     # NEW: Chat TypeScript types
```

---

## Migration Plan

1. **Database Migration**: Add `conversations` table without affecting existing tables
2. **Backend Deployment**: Add new routes without modifying existing endpoints
3. **Frontend Deployment**: Add chat component to dashboard without removing existing features
4. **Feature Flag**: Optional flag to enable/disable chat feature during rollout
5. **Rollback Plan**: Chat feature can be disabled independently without affecting Phase-2 functionality
