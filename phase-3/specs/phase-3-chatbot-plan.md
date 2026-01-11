# Implementation Plan: Phase-3 AI Chatbot with MCP Server

**Spec Reference**: `specs/phase-3-chatbot-spec.md`
**Created**: 2026-01-10
**Status**: Ready for Implementation

---

## Implementation Overview

Phase-3 will be implemented in **5 sequential steps**, each building on the previous. This ensures a stable, testable progression.

### Implementation Order

```
Step 1: Database & Models (Foundation)
    ↓
Step 2: MCP Tools (Core Business Logic)
    ↓
Step 3: AI Agent (OpenAI Integration)
    ↓
Step 4: Chat API (REST Endpoint)
    ↓
Step 5: Frontend Chat UI (User Interface)
```

---

## Step 1: Database & Models

**Goal**: Create the database schema and SQLModel for conversation persistence.

### Files to Create

| File | Purpose |
|------|---------|
| `backend/app/models/conversation.py` | Conversation SQLModel |
| `backend/app/schemas/chat.py` | Pydantic schemas for chat API |
| `backend/app/migrations/002_add_conversations.py` | Database migration |

### Implementation Details

#### 1.1 Conversation Model (`backend/app/models/conversation.py`)

```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, UTC
from typing import Optional, List
from uuid import uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    messages: List[dict] = Field(default=[], sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

#### 1.2 Chat Schemas (`backend/app/schemas/chat.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

class ConversationSummary(BaseModel):
    id: str
    preview: str
    created_at: datetime

class ConversationListResponse(BaseModel):
    conversations: List[ConversationSummary]
```

### Dependencies
- None (foundation layer)

### Validation Criteria
- [ ] Conversation model can be created and saved to database
- [ ] Messages are stored as JSONB array
- [ ] User isolation is enforced (foreign key to users.id)

---

## Step 2: MCP Tools

**Goal**: Implement stateless MCP tools that perform task operations on the database.

### Files to Create

| File | Purpose |
|------|---------|
| `backend/app/mcp/__init__.py` | MCP module initialization |
| `backend/app/mcp/tools/__init__.py` | Tools module initialization |
| `backend/app/mcp/tools/add_task.py` | add_task tool |
| `backend/app/mcp/tools/list_tasks.py` | list_tasks tool |
| `backend/app/mcp/tools/complete_task.py` | complete_task tool |
| `backend/app/mcp/tools/update_task.py` | update_task tool |
| `backend/app/mcp/tools/delete_task.py` | delete_task tool |
| `backend/app/mcp/tools/base.py` | Base tool response class |

### Implementation Details

#### 2.1 Tool Response Base (`backend/app/mcp/tools/base.py`)

```python
from pydantic import BaseModel
from typing import Optional, Any

class ToolResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
```

#### 2.2 Add Task Tool (`backend/app/mcp/tools/add_task.py`)

```python
from sqlmodel import Session
from app.models.task import Task, TaskStatus
from app.mcp.tools.base import ToolResponse
from datetime import datetime, UTC

def add_task(
    session: Session,
    user_id: int,
    title: str,
    description: str = None,
    status: str = "pending"
) -> ToolResponse:
    """Create a new task for the user."""
    try:
        # Validate status
        task_status = TaskStatus(status.lower().replace(" ", "_"))
    except ValueError:
        return ToolResponse(
            success=False,
            message=f"Invalid status '{status}'. Use: pending, in_progress, completed"
        )

    task = Task(
        title=title,
        description=description,
        status=task_status,
        user_id=user_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return ToolResponse(
        success=True,
        message=f"Task '{title}' created successfully",
        data={"id": task.id, "title": task.title, "status": task.status}
    )
```

#### 2.3 List Tasks Tool (`backend/app/mcp/tools/list_tasks.py`)

```python
from sqlmodel import Session, select
from app.models.task import Task, TaskStatus
from app.mcp.tools.base import ToolResponse
from typing import Optional

def list_tasks(
    session: Session,
    user_id: int,
    status_filter: Optional[str] = None
) -> ToolResponse:
    """List all tasks for the user, optionally filtered by status."""
    query = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None
    )

    if status_filter and status_filter != "all":
        try:
            task_status = TaskStatus(status_filter.lower().replace(" ", "_"))
            query = query.where(Task.status == task_status)
        except ValueError:
            return ToolResponse(
                success=False,
                message=f"Invalid status filter '{status_filter}'"
            )

    tasks = session.exec(query).all()

    if not tasks:
        return ToolResponse(
            success=True,
            message="You have no active tasks",
            data={"tasks": [], "count": 0}
        )

    task_list = [
        {"id": t.id, "title": t.title, "status": t.status, "description": t.description}
        for t in tasks
    ]

    return ToolResponse(
        success=True,
        message=f"Found {len(tasks)} task(s)",
        data={"tasks": task_list, "count": len(tasks)}
    )
```

#### 2.4 Complete Task Tool (`backend/app/mcp/tools/complete_task.py`)

```python
from sqlmodel import Session, select
from app.models.task import Task, TaskStatus
from app.mcp.tools.base import ToolResponse
from datetime import datetime, UTC

def complete_task(
    session: Session,
    user_id: int,
    task_identifier: str
) -> ToolResponse:
    """Mark a task as completed by title or ID."""
    # Try to find by ID first, then by title
    task = None

    if task_identifier.isdigit():
        task = session.exec(
            select(Task).where(
                Task.id == int(task_identifier),
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).first()

    if not task:
        # Search by title (case-insensitive partial match)
        tasks = session.exec(
            select(Task).where(
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).all()

        matching = [t for t in tasks if task_identifier.lower() in t.title.lower()]

        if len(matching) == 1:
            task = matching[0]
        elif len(matching) > 1:
            titles = [t.title for t in matching]
            return ToolResponse(
                success=False,
                message=f"Multiple tasks match '{task_identifier}': {titles}. Please be more specific."
            )

    if not task:
        return ToolResponse(
            success=False,
            message=f"Task '{task_identifier}' not found"
        )

    if task.status == TaskStatus.COMPLETED:
        return ToolResponse(
            success=True,
            message=f"Task '{task.title}' is already completed"
        )

    task.status = TaskStatus.COMPLETED
    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()

    return ToolResponse(
        success=True,
        message=f"Task '{task.title}' marked as completed",
        data={"id": task.id, "title": task.title, "status": "completed"}
    )
```

#### 2.5 Update Task Tool (`backend/app/mcp/tools/update_task.py`)

```python
from sqlmodel import Session, select
from app.models.task import Task, TaskStatus
from app.mcp.tools.base import ToolResponse
from datetime import datetime, UTC
from typing import Optional

def update_task(
    session: Session,
    user_id: int,
    task_identifier: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None
) -> ToolResponse:
    """Update an existing task."""
    # Find task by ID or title
    task = None

    if task_identifier.isdigit():
        task = session.exec(
            select(Task).where(
                Task.id == int(task_identifier),
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).first()

    if not task:
        tasks = session.exec(
            select(Task).where(
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).all()

        matching = [t for t in tasks if task_identifier.lower() in t.title.lower()]

        if len(matching) == 1:
            task = matching[0]
        elif len(matching) > 1:
            titles = [t.title for t in matching]
            return ToolResponse(
                success=False,
                message=f"Multiple tasks match '{task_identifier}': {titles}. Please be more specific."
            )

    if not task:
        return ToolResponse(
            success=False,
            message=f"Task '{task_identifier}' not found"
        )

    # Apply updates
    updates = []

    if title:
        task.title = title
        updates.append(f"title to '{title}'")

    if description is not None:
        task.description = description
        updates.append("description")

    if status:
        try:
            task.status = TaskStatus(status.lower().replace(" ", "_"))
            updates.append(f"status to '{status}'")
        except ValueError:
            return ToolResponse(
                success=False,
                message=f"Invalid status '{status}'. Use: pending, in_progress, completed"
            )

    if not updates:
        return ToolResponse(
            success=False,
            message="No updates provided"
        )

    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()

    return ToolResponse(
        success=True,
        message=f"Updated task: {', '.join(updates)}",
        data={"id": task.id, "title": task.title, "status": task.status}
    )
```

#### 2.6 Delete Task Tool (`backend/app/mcp/tools/delete_task.py`)

```python
from sqlmodel import Session, select
from app.models.task import Task
from app.mcp.tools.base import ToolResponse
from datetime import datetime, UTC

def delete_task(
    session: Session,
    user_id: int,
    task_identifier: str
) -> ToolResponse:
    """Soft delete a task (move to history)."""
    # Find task by ID or title
    task = None

    if task_identifier.isdigit():
        task = session.exec(
            select(Task).where(
                Task.id == int(task_identifier),
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).first()

    if not task:
        tasks = session.exec(
            select(Task).where(
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).all()

        matching = [t for t in tasks if task_identifier.lower() in t.title.lower()]

        if len(matching) == 1:
            task = matching[0]
        elif len(matching) > 1:
            titles = [t.title for t in matching]
            return ToolResponse(
                success=False,
                message=f"Multiple tasks match '{task_identifier}': {titles}. Please be more specific."
            )

    if not task:
        return ToolResponse(
            success=False,
            message=f"Task '{task_identifier}' not found"
        )

    # Soft delete
    task.deleted_at = datetime.now(UTC)
    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()

    return ToolResponse(
        success=True,
        message=f"Task '{task.title}' deleted. You can restore it from History.",
        data={"id": task.id, "title": task.title}
    )
```

### Dependencies
- Step 1 (Database & Models)

### Validation Criteria
- [ ] All 5 tools can be called independently
- [ ] Tools enforce user isolation
- [ ] Tools return consistent ToolResponse format
- [ ] Tools handle edge cases (not found, duplicates, invalid input)

---

## Step 3: AI Agent

**Goal**: Implement the OpenAI Agents SDK-based agent that interprets user intent and calls MCP tools.

### Files to Create

| File | Purpose |
|------|---------|
| `backend/app/agents/__init__.py` | Agents module initialization |
| `backend/app/agents/task_agent.py` | Main AI agent implementation |

### New Dependencies (requirements.txt)

```
# Add to requirements.txt
openai>=1.0.0
```

### Implementation Details

#### 3.1 Task Agent (`backend/app/agents/task_agent.py`)

```python
from openai import OpenAI
from sqlmodel import Session
from typing import Optional
import json

from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.complete_task import complete_task
from app.mcp.tools.update_task import update_task
from app.mcp.tools.delete_task import delete_task
from app.config import settings

# Tool definitions for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the task"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Status of the task, defaults to pending"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the user, optionally filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["all", "pending", "in_progress", "completed"],
                        "description": "Filter tasks by status"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "Task title or ID to complete"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task's title, description, or status",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "Task title or ID to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "New status for the task"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task (moves to history, can be restored)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "Task title or ID to delete"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their todo tasks through natural language.

You can:
- Add new tasks (with title, optional description, and status)
- List tasks (all or filtered by status: pending, in_progress, completed)
- Mark tasks as complete
- Update task details (title, description, status)
- Delete tasks (soft delete - they go to history)

When users reference tasks, try to match by title. If multiple tasks match, ask for clarification.

For the "add task" format like:
"add task Title: X description: Y status: Z"
Parse and extract the title, description, and status fields.

Always confirm actions taken and provide helpful responses.
Keep responses concise but informative."""


class TaskAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL or "gpt-4-turbo-preview"

    def _execute_tool(
        self,
        session: Session,
        user_id: int,
        tool_name: str,
        arguments: dict
    ) -> str:
        """Execute an MCP tool and return the result."""
        tool_map = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "update_task": update_task,
            "delete_task": delete_task
        }

        tool_func = tool_map.get(tool_name)
        if not tool_func:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        result = tool_func(session, user_id, **arguments)
        return json.dumps(result.model_dump())

    def chat(
        self,
        session: Session,
        user_id: int,
        message: str,
        conversation_history: list = None
    ) -> str:
        """Process a chat message and return the response."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history (limited to last 20 messages)
        if conversation_history:
            messages.extend(conversation_history[-20:])

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=500
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        if assistant_message.tool_calls:
            # Execute each tool call
            tool_results = []
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                result = self._execute_tool(session, user_id, tool_name, arguments)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": result
                })

            # Add assistant message with tool calls
            messages.append(assistant_message)

            # Add tool results
            messages.extend(tool_results)

            # Get final response
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500
            )

            return final_response.choices[0].message.content

        return assistant_message.content
```

### Environment Variables (add to .env)

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
```

### Dependencies
- Step 2 (MCP Tools)

### Validation Criteria
- [ ] Agent correctly interprets natural language requests
- [ ] Agent calls appropriate tools based on user intent
- [ ] Agent handles multi-turn conversations
- [ ] Agent provides helpful error messages

---

## Step 4: Chat API

**Goal**: Create the REST API endpoint for chat interactions.

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/api/v1/chat.py` | Create | Chat API router |
| `backend/app/main.py` | Modify | Register chat router |
| `backend/app/config.py` | Modify | Add chat config settings |

### Implementation Details

#### 4.1 Chat Router (`backend/app/api/v1/chat.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, UTC
from typing import List
import time

from app.db.session import get_session
from app.auth.dependencies import get_current_user_id
from app.models.conversation import Conversation
from app.schemas.chat import (
    ChatRequest, ChatResponse,
    ConversationSummary, ConversationListResponse
)
from app.agents.task_agent import TaskAgent
from app.config import settings

router = APIRouter()

# Simple in-memory rate limiter (for production, use Redis)
_rate_limit_cache = {}

def check_rate_limit(user_id: int) -> bool:
    """Check if user has exceeded rate limit (10 requests/minute)."""
    now = time.time()
    key = f"chat:{user_id}"

    if key not in _rate_limit_cache:
        _rate_limit_cache[key] = []

    # Remove old entries
    _rate_limit_cache[key] = [t for t in _rate_limit_cache[key] if now - t < 60]

    if len(_rate_limit_cache[key]) >= settings.CHAT_RATE_LIMIT:
        return False

    _rate_limit_cache[key].append(now)
    return True


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: int,
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Process a chat message and return AI response."""
    # Verify user owns the resource
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    # Rate limiting
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before sending more messages."
        )

    # Get or create conversation
    conversation = None
    if request.conversation_id:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id, messages=[])
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Build conversation history for context
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in conversation.messages
    ]

    # Process message with AI agent
    agent = TaskAgent()
    try:
        response_text = agent.chat(
            session=session,
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_history
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message. Please try again."
        )

    # Update conversation with new messages
    now = datetime.now(UTC).isoformat()
    conversation.messages.append({
        "role": "user",
        "content": request.message,
        "timestamp": now
    })
    conversation.messages.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": now
    })
    conversation.updated_at = datetime.now(UTC)

    session.add(conversation)
    session.commit()

    return ChatResponse(
        response=response_text,
        conversation_id=conversation.id
    )


@router.get("/{user_id}/conversations", response_model=ConversationListResponse)
async def list_conversations(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """List all conversations for a user."""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    summaries = []
    for conv in conversations:
        preview = ""
        if conv.messages:
            # Get first user message as preview
            for msg in conv.messages:
                if msg["role"] == "user":
                    preview = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                    break

        summaries.append(ConversationSummary(
            id=conv.id,
            preview=preview or "New conversation",
            created_at=conv.created_at
        ))

    return ConversationListResponse(conversations=summaries)


@router.get("/{user_id}/conversations/{conversation_id}")
async def get_conversation(
    user_id: int,
    conversation_id: str,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Get a specific conversation with all messages."""
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return {
        "id": conversation.id,
        "messages": conversation.messages,
        "created_at": conversation.created_at
    }


@router.delete("/{user_id}/conversations/{conversation_id}")
async def delete_conversation(
    user_id: int,
    conversation_id: str,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Delete a conversation."""
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    session.delete(conversation)
    session.commit()

    return {"status": "deleted"}
```

#### 4.2 Register Router in main.py

Add to `backend/app/main.py`:
```python
from app.api.v1 import chat

# Add with other routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
```

#### 4.3 Config Updates (`backend/app/config.py`)

Add these settings:
```python
# Chat settings
OPENAI_API_KEY: str = ""
OPENAI_MODEL: str = "gpt-4-turbo-preview"
CHAT_RATE_LIMIT: int = 10  # requests per minute
CHAT_TIMEOUT_SECONDS: int = 30
CHAT_MAX_MESSAGE_LENGTH: int = 2000
CHAT_CONTEXT_MESSAGES: int = 20
```

### Dependencies
- Step 3 (AI Agent)

### Validation Criteria
- [ ] POST /api/{user_id}/chat works with JWT auth
- [ ] Rate limiting enforced (10/min)
- [ ] Conversation persisted to database
- [ ] User isolation enforced
- [ ] Error handling returns friendly messages

---

## Step 5: Frontend Chat UI

**Goal**: Build the ChatKit-based chat interface in the dashboard.

### Files to Create

| File | Purpose |
|------|---------|
| `frontend/components/chat/ChatContainer.tsx` | Main chat container |
| `frontend/components/chat/ChatMessage.tsx` | Message bubble component |
| `frontend/components/chat/ChatInput.tsx` | Input field component |
| `frontend/lib/chat-api.ts` | Chat API client functions |
| `frontend/types/chat.ts` | TypeScript types |

### Files to Modify

| File | Change |
|------|--------|
| `frontend/app/dashboard/page.tsx` | Add chat toggle button and container |

### Implementation Details

#### 5.1 Chat Types (`frontend/types/chat.ts`)

```typescript
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
}

export interface Conversation {
  id: string;
  messages: ChatMessage[];
  created_at: string;
}

export interface ConversationSummary {
  id: string;
  preview: string;
  created_at: string;
}
```

#### 5.2 Chat API Client (`frontend/lib/chat-api.ts`)

```typescript
import { apiGet, apiPost, apiDelete } from "@/lib/api";
import type { ChatRequest, ChatResponse, Conversation, ConversationSummary } from "@/types/chat";

export async function sendChatMessage(
  userId: number,
  request: ChatRequest
): Promise<ChatResponse> {
  const response = await apiPost(`/api/${userId}/chat`, request);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to send message");
  }

  return response.json();
}

export async function getConversations(
  userId: number
): Promise<{ conversations: ConversationSummary[] }> {
  const response = await apiGet(`/api/${userId}/conversations`);

  if (!response.ok) {
    throw new Error("Failed to load conversations");
  }

  return response.json();
}

export async function getConversation(
  userId: number,
  conversationId: string
): Promise<Conversation> {
  const response = await apiGet(`/api/${userId}/conversations/${conversationId}`);

  if (!response.ok) {
    throw new Error("Failed to load conversation");
  }

  return response.json();
}

export async function deleteConversation(
  userId: number,
  conversationId: string
): Promise<void> {
  const response = await apiDelete(`/api/${userId}/conversations/${conversationId}`);

  if (!response.ok) {
    throw new Error("Failed to delete conversation");
  }
}
```

#### 5.3 Chat Container (`frontend/components/chat/ChatContainer.tsx`)

```typescript
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
}

export function ChatContainer({ userId, isOpen, onClose }: ChatContainerProps) {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

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

      const assistantMessage: ChatMessageType = {
        role: "assistant",
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed bottom-4 right-4 w-96 h-[500px] rounded-2xl shadow-2xl flex flex-col overflow-hidden z-50"
      style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b"
        style={{ borderColor: 'var(--card-border)', background: 'var(--accent-bg)' }}
      >
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500"></div>
          <span className="font-semibold" style={{ color: 'var(--foreground)' }}>
            Task Assistant
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleNewChat}
            className="p-1 hover:opacity-70 transition-opacity"
            title="New Chat"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-1 hover:opacity-70 transition-opacity"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8" style={{ color: 'var(--foreground)', opacity: 0.6 }}>
            <p className="text-sm">Hi! I can help you manage your tasks.</p>
            <p className="text-xs mt-2">Try: "Add a task to buy groceries"</p>
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div
              className="px-4 py-2 rounded-2xl max-w-[80%]"
              style={{ background: 'var(--accent-bg)' }}
            >
              <div className="flex space-x-1">
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="text-center py-2">
            <p className="text-sm text-red-500">{error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
```

#### 5.4 Chat Message (`frontend/components/chat/ChatMessage.tsx`)

```typescript
import type { ChatMessage as ChatMessageType } from "@/types/chat";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`px-4 py-2 rounded-2xl max-w-[80%] ${
          isUser ? "rounded-br-sm" : "rounded-bl-sm"
        }`}
        style={{
          background: isUser ? "#6db9d4" : "var(--accent-bg)",
          color: isUser ? "white" : "var(--foreground)",
        }}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}
```

#### 5.5 Chat Input (`frontend/components/chat/ChatInput.tsx`)

```typescript
"use client";

import { useState, KeyboardEvent } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
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
      style={{ borderColor: 'var(--card-border)' }}
    >
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          disabled={disabled}
          rows={1}
          className="flex-1 px-4 py-2 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-[#6db9d4] transition-all"
          style={{
            background: 'var(--input-bg)',
            color: 'var(--input-text)',
          }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="px-4 py-2 rounded-xl text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
          style={{ background: '#6db9d4' }}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </div>
  );
}
```

#### 5.6 Dashboard Integration

Add to `frontend/app/dashboard/page.tsx`:

```typescript
// Add import at top
import { ChatContainer } from "@/components/chat/ChatContainer";

// Add state for chat
const [isChatOpen, setIsChatOpen] = useState(false);
const [userId, setUserId] = useState<number | null>(null);

// Get user ID from token (in useEffect)
useEffect(() => {
  const token = localStorage.getItem("jwt_token");
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUserId(parseInt(payload.sub));
    } catch {}
  }
}, []);

// Add chat button and container at end of JSX (before closing div)
{userId && (
  <>
    {/* Chat Toggle Button */}
    <button
      onClick={() => setIsChatOpen(!isChatOpen)}
      className="fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-lg flex items-center justify-center hover:opacity-90 transition-opacity z-40"
      style={{ background: '#e08b3d' }}
    >
      <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    </button>

    {/* Chat Container */}
    <ChatContainer
      userId={userId}
      isOpen={isChatOpen}
      onClose={() => setIsChatOpen(false)}
    />
  </>
)}
```

### Dependencies
- Step 4 (Chat API)

### Validation Criteria
- [ ] Chat button visible on dashboard
- [ ] Chat opens/closes correctly
- [ ] Messages display correctly (user right, assistant left)
- [ ] Loading state shown while waiting
- [ ] Error messages displayed
- [ ] Auto-scroll to new messages
- [ ] Theme support (light/dark)
- [ ] Mobile responsive

---

## Summary: Implementation Checklist

### Step 1: Database & Models
- [ ] Create `backend/app/models/conversation.py`
- [ ] Create `backend/app/schemas/chat.py`
- [ ] Run database migration
- [ ] Test: Conversation model CRUD works

### Step 2: MCP Tools
- [ ] Create `backend/app/mcp/` directory structure
- [ ] Implement all 5 tools (add, list, complete, update, delete)
- [ ] Test: Each tool works independently

### Step 3: AI Agent
- [ ] Add `openai` to requirements.txt
- [ ] Create `backend/app/agents/task_agent.py`
- [ ] Add OpenAI config to settings
- [ ] Test: Agent interprets natural language correctly

### Step 4: Chat API
- [ ] Create `backend/app/api/v1/chat.py`
- [ ] Register router in main.py
- [ ] Test: POST /api/{user_id}/chat works
- [ ] Test: Rate limiting enforced

### Step 5: Frontend Chat UI
- [ ] Create chat components
- [ ] Create chat API client
- [ ] Integrate into dashboard
- [ ] Test: Full chat flow works

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OpenAI API rate limits | Implement client-side rate limiting |
| Slow AI responses | Show loading indicator, set 30s timeout |
| Token cost overruns | Limit context to 20 messages, cap response to 500 tokens |
| User data exposure | Strict user_id validation on all endpoints |
| JSONB performance | Index on user_id, limit message history |

---

## Rollback Plan

Each step can be rolled back independently:
1. **Database**: Drop conversations table
2. **MCP Tools**: Delete mcp/ directory
3. **AI Agent**: Delete agents/ directory
4. **Chat API**: Remove router from main.py
5. **Frontend**: Remove chat components and dashboard integration

Phase-2 functionality remains completely unaffected as no existing code is modified (except adding imports in main.py and dashboard).
