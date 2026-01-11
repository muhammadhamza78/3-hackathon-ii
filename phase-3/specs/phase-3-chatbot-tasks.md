# Implementation Tasks: Phase-3 AI Chatbot

**Spec**: `specs/phase-3-chatbot-spec.md`
**Plan**: `specs/phase-3-chatbot-plan.md`
**Created**: 2026-01-10

---

## Task Overview

| Step | Tasks | Description |
|------|-------|-------------|
| 1 | T1.1 - T1.4 | Database & Models |
| 2 | T2.1 - T2.7 | MCP Tools |
| 3 | T3.1 - T3.3 | AI Agent |
| 4 | T4.1 - T4.4 | Chat API |
| 5 | T5.1 - T5.7 | Frontend Chat UI |

**Total Tasks**: 25

---

## Step 1: Database & Models

### T1.1: Create Conversation Model

**File**: `backend/app/models/conversation.py`

**Action**: Create new file

**Code**:
```python
"""
Conversation Model
Stores chat conversations between users and the AI assistant.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-027 to FR-032)
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, UTC
from typing import Optional, List
from uuid import uuid4


class Conversation(SQLModel, table=True):
    """
    Conversation model for storing chat history.

    User Isolation: All queries MUST filter by user_id.
    Messages stored as JSONB array for flexibility.
    """
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="UUID for conversation"
    )
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of this conversation"
    )
    messages: List[dict] = Field(
        default=[],
        sa_column=Column(JSONB, nullable=False, default=[]),
        description="Array of {role, content, timestamp} objects"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When conversation started"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last message timestamp"
    )
```

**Validation**:
- [ ] File created at correct path
- [ ] Model imports work
- [ ] JSONB column configured correctly

---

### T1.2: Create Chat Schemas

**File**: `backend/app/schemas/chat.py`

**Action**: Create new file

**Code**:
```python
"""
Chat Schemas
Pydantic models for chat API request/response validation.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-019 to FR-026)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual message in a conversation."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When message was sent")


class ChatRequest(BaseModel):
    """Request body for POST /api/{user_id}/chat"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Continue existing conversation, or None for new"
    )


class ChatResponse(BaseModel):
    """Response from POST /api/{user_id}/chat"""
    response: str = Field(..., description="Assistant's response")
    conversation_id: str = Field(..., description="Conversation ID for continuity")


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing."""
    id: str
    preview: str = Field(..., description="First 50 chars of first user message")
    created_at: datetime


class ConversationListResponse(BaseModel):
    """Response from GET /api/{user_id}/conversations"""
    conversations: List[ConversationSummary]


class ConversationDetail(BaseModel):
    """Full conversation with all messages."""
    id: str
    messages: List[ChatMessage]
    created_at: datetime
```

**Validation**:
- [ ] All schemas have proper validation
- [ ] Max length enforced on message (2000 chars)

---

### T1.3: Update Models __init__.py

**File**: `backend/app/models/__init__.py`

**Action**: Modify existing file - add Conversation import

**Code to Add**:
```python
from app.models.conversation import Conversation
```

**Validation**:
- [ ] Import added without breaking existing imports

---

### T1.4: Update Config with Chat Settings

**File**: `backend/app/config.py`

**Action**: Modify existing file - add chat configuration

**Code to Add** (in Settings class):
```python
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Chat Configuration
    CHAT_RATE_LIMIT: int = 10  # requests per minute per user
    CHAT_TIMEOUT_SECONDS: int = 30
    CHAT_MAX_MESSAGE_LENGTH: int = 2000
    CHAT_CONTEXT_MESSAGES: int = 20  # messages to include for context
```

**Validation**:
- [ ] Settings load from environment variables
- [ ] Default values work correctly

---

## Step 2: MCP Tools

### T2.1: Create MCP Module Structure

**Files**:
- `backend/app/mcp/__init__.py`
- `backend/app/mcp/tools/__init__.py`

**Action**: Create directories and init files

**Code** (`backend/app/mcp/__init__.py`):
```python
"""
MCP (Model Context Protocol) Module
Exposes task management tools for the AI agent.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-001 to FR-010)
"""
```

**Code** (`backend/app/mcp/tools/__init__.py`):
```python
"""
MCP Tools Package
Stateless tools that interact with the database.
"""

from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.complete_task import complete_task
from app.mcp.tools.update_task import update_task
from app.mcp.tools.delete_task import delete_task

__all__ = [
    "add_task",
    "list_tasks",
    "complete_task",
    "update_task",
    "delete_task"
]
```

**Validation**:
- [ ] Directories created
- [ ] Init files created

---

### T2.2: Create Tool Response Base

**File**: `backend/app/mcp/tools/base.py`

**Action**: Create new file

**Code**:
```python
"""
Base Tool Response
Consistent response format for all MCP tools.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-010)
"""

from pydantic import BaseModel
from typing import Optional, Any


class ToolResponse(BaseModel):
    """
    Standard response format for all MCP tools.

    Attributes:
        success: Whether the operation succeeded
        message: Human-readable result description
        data: Optional structured data (task details, lists, etc.)
    """
    success: bool
    message: str
    data: Optional[Any] = None
```

**Validation**:
- [ ] ToolResponse can be serialized to JSON

---

### T2.3: Create add_task Tool

**File**: `backend/app/mcp/tools/add_task.py`

**Action**: Create new file

**Code**:
```python
"""
Add Task Tool
Creates a new task for the user.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-002)
"""

from sqlmodel import Session
from datetime import datetime, UTC
from typing import Optional

from app.models.task import Task, TaskStatus
from app.mcp.tools.base import ToolResponse


def add_task(
    session: Session,
    user_id: int,
    title: str,
    description: Optional[str] = None,
    status: str = "pending"
) -> ToolResponse:
    """
    Create a new task for the user.

    Args:
        session: Database session
        user_id: Owner of the task
        title: Task title (required)
        description: Task description (optional)
        status: pending, in_progress, or completed (default: pending)

    Returns:
        ToolResponse with created task data
    """
    # Validate and convert status
    status_normalized = status.lower().replace(" ", "_").replace("-", "_")

    try:
        task_status = TaskStatus(status_normalized)
    except ValueError:
        return ToolResponse(
            success=False,
            message=f"Invalid status '{status}'. Valid options: pending, in_progress, completed"
        )

    # Validate title
    if not title or not title.strip():
        return ToolResponse(
            success=False,
            message="Task title cannot be empty"
        )

    title = title.strip()
    if len(title) > 200:
        return ToolResponse(
            success=False,
            message="Task title must be 200 characters or less"
        )

    # Create task
    task = Task(
        title=title,
        description=description.strip() if description else None,
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
        message=f"Created task '{title}' with status '{task_status.value}'",
        data={
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value if hasattr(task.status, 'value') else task.status
        }
    )
```

**Validation**:
- [ ] Creates task in database
- [ ] Handles invalid status gracefully
- [ ] Validates title length

---

### T2.4: Create list_tasks Tool

**File**: `backend/app/mcp/tools/list_tasks.py`

**Action**: Create new file

**Code**:
```python
"""
List Tasks Tool
Lists all tasks for the user with optional filtering.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-003)
"""

from sqlmodel import Session, select
from typing import Optional

from app.models.task import Task, TaskStatus
from app.mcp.tools.base import ToolResponse


def list_tasks(
    session: Session,
    user_id: int,
    status_filter: Optional[str] = None
) -> ToolResponse:
    """
    List all active tasks for the user.

    Args:
        session: Database session
        user_id: Owner of the tasks
        status_filter: Optional filter (all, pending, in_progress, completed)

    Returns:
        ToolResponse with list of tasks
    """
    # Build query - only active tasks (not deleted)
    query = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at == None
    ).order_by(Task.created_at.desc())

    # Apply status filter if provided
    if status_filter and status_filter.lower() != "all":
        status_normalized = status_filter.lower().replace(" ", "_").replace("-", "_")

        try:
            task_status = TaskStatus(status_normalized)
            query = query.where(Task.status == task_status)
        except ValueError:
            return ToolResponse(
                success=False,
                message=f"Invalid status filter '{status_filter}'. Valid options: all, pending, in_progress, completed"
            )

    tasks = session.exec(query).all()

    if not tasks:
        filter_msg = f" with status '{status_filter}'" if status_filter and status_filter.lower() != "all" else ""
        return ToolResponse(
            success=True,
            message=f"You have no active tasks{filter_msg}",
            data={"tasks": [], "count": 0}
        )

    task_list = []
    for t in tasks:
        task_list.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status.value if hasattr(t.status, 'value') else t.status
        })

    return ToolResponse(
        success=True,
        message=f"Found {len(tasks)} task(s)",
        data={"tasks": task_list, "count": len(tasks)}
    )
```

**Validation**:
- [ ] Returns only user's tasks
- [ ] Excludes deleted tasks
- [ ] Filter works correctly

---

### T2.5: Create complete_task Tool

**File**: `backend/app/mcp/tools/complete_task.py`

**Action**: Create new file

**Code**:
```python
"""
Complete Task Tool
Marks a task as completed.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-004)
"""

from sqlmodel import Session, select
from datetime import datetime, UTC

from app.models.task import Task, TaskStatus
from app.mcp.tools.base import ToolResponse


def complete_task(
    session: Session,
    user_id: int,
    task_identifier: str
) -> ToolResponse:
    """
    Mark a task as completed.

    Args:
        session: Database session
        user_id: Owner of the task
        task_identifier: Task title or ID

    Returns:
        ToolResponse with completion status
    """
    task = _find_task(session, user_id, task_identifier)

    if isinstance(task, ToolResponse):
        return task  # Error response

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
        message=f"Marked '{task.title}' as completed",
        data={
            "id": task.id,
            "title": task.title,
            "status": "completed"
        }
    )


def _find_task(session: Session, user_id: int, identifier: str) -> Task | ToolResponse:
    """
    Find a task by ID or title.
    Returns Task if found, ToolResponse if error.
    """
    # Try to find by ID first
    if identifier.isdigit():
        task = session.exec(
            select(Task).where(
                Task.id == int(identifier),
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).first()

        if task:
            return task

    # Search by title (case-insensitive partial match)
    all_tasks = session.exec(
        select(Task).where(
            Task.user_id == user_id,
            Task.deleted_at == None
        )
    ).all()

    identifier_lower = identifier.lower().strip()
    matching = [t for t in all_tasks if identifier_lower in t.title.lower()]

    if len(matching) == 1:
        return matching[0]
    elif len(matching) > 1:
        titles = [f"'{t.title}'" for t in matching]
        return ToolResponse(
            success=False,
            message=f"Multiple tasks match '{identifier}': {', '.join(titles)}. Please be more specific."
        )
    else:
        return ToolResponse(
            success=False,
            message=f"Task '{identifier}' not found"
        )
```

**Validation**:
- [ ] Finds task by ID
- [ ] Finds task by title (partial match)
- [ ] Handles multiple matches
- [ ] Handles already completed

---

### T2.6: Create update_task Tool

**File**: `backend/app/mcp/tools/update_task.py`

**Action**: Create new file

**Code**:
```python
"""
Update Task Tool
Updates an existing task's properties.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-005)
"""

from sqlmodel import Session, select
from datetime import datetime, UTC
from typing import Optional

from app.models.task import Task, TaskStatus
from app.mcp.tools.base import ToolResponse


def update_task(
    session: Session,
    user_id: int,
    task_identifier: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None
) -> ToolResponse:
    """
    Update an existing task.

    Args:
        session: Database session
        user_id: Owner of the task
        task_identifier: Task title or ID to update
        title: New title (optional)
        description: New description (optional)
        status: New status (optional)

    Returns:
        ToolResponse with update result
    """
    task = _find_task(session, user_id, task_identifier)

    if isinstance(task, ToolResponse):
        return task  # Error response

    updates = []

    # Update title
    if title is not None:
        title = title.strip()
        if not title:
            return ToolResponse(
                success=False,
                message="Title cannot be empty"
            )
        if len(title) > 200:
            return ToolResponse(
                success=False,
                message="Title must be 200 characters or less"
            )
        task.title = title
        updates.append(f"title to '{title}'")

    # Update description
    if description is not None:
        task.description = description.strip() if description else None
        updates.append("description")

    # Update status
    if status is not None:
        status_normalized = status.lower().replace(" ", "_").replace("-", "_")
        try:
            task.status = TaskStatus(status_normalized)
            updates.append(f"status to '{status_normalized}'")
        except ValueError:
            return ToolResponse(
                success=False,
                message=f"Invalid status '{status}'. Valid options: pending, in_progress, completed"
            )

    if not updates:
        return ToolResponse(
            success=False,
            message="No updates provided. Specify title, description, or status to update."
        )

    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()

    return ToolResponse(
        success=True,
        message=f"Updated task: {', '.join(updates)}",
        data={
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value if hasattr(task.status, 'value') else task.status
        }
    )


def _find_task(session: Session, user_id: int, identifier: str) -> Task | ToolResponse:
    """Find a task by ID or title."""
    if identifier.isdigit():
        task = session.exec(
            select(Task).where(
                Task.id == int(identifier),
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).first()
        if task:
            return task

    all_tasks = session.exec(
        select(Task).where(
            Task.user_id == user_id,
            Task.deleted_at == None
        )
    ).all()

    identifier_lower = identifier.lower().strip()
    matching = [t for t in all_tasks if identifier_lower in t.title.lower()]

    if len(matching) == 1:
        return matching[0]
    elif len(matching) > 1:
        titles = [f"'{t.title}'" for t in matching]
        return ToolResponse(
            success=False,
            message=f"Multiple tasks match '{identifier}': {', '.join(titles)}. Please be more specific."
        )
    else:
        return ToolResponse(
            success=False,
            message=f"Task '{identifier}' not found"
        )
```

**Validation**:
- [ ] Updates title correctly
- [ ] Updates description correctly
- [ ] Updates status correctly
- [ ] Validates all inputs

---

### T2.7: Create delete_task Tool

**File**: `backend/app/mcp/tools/delete_task.py`

**Action**: Create new file

**Code**:
```python
"""
Delete Task Tool
Soft deletes a task (moves to history).

Spec Reference: specs/phase-3-chatbot-spec.md (FR-006)
"""

from sqlmodel import Session, select
from datetime import datetime, UTC

from app.models.task import Task
from app.mcp.tools.base import ToolResponse


def delete_task(
    session: Session,
    user_id: int,
    task_identifier: str
) -> ToolResponse:
    """
    Soft delete a task (move to history).

    Args:
        session: Database session
        user_id: Owner of the task
        task_identifier: Task title or ID to delete

    Returns:
        ToolResponse with deletion result
    """
    task = _find_task(session, user_id, task_identifier)

    if isinstance(task, ToolResponse):
        return task  # Error response

    # Soft delete by setting deleted_at
    task.deleted_at = datetime.now(UTC)
    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()

    return ToolResponse(
        success=True,
        message=f"Deleted '{task.title}'. You can restore it from the History tab.",
        data={
            "id": task.id,
            "title": task.title
        }
    )


def _find_task(session: Session, user_id: int, identifier: str) -> Task | ToolResponse:
    """Find a task by ID or title."""
    if identifier.isdigit():
        task = session.exec(
            select(Task).where(
                Task.id == int(identifier),
                Task.user_id == user_id,
                Task.deleted_at == None
            )
        ).first()
        if task:
            return task

    all_tasks = session.exec(
        select(Task).where(
            Task.user_id == user_id,
            Task.deleted_at == None
        )
    ).all()

    identifier_lower = identifier.lower().strip()
    matching = [t for t in all_tasks if identifier_lower in t.title.lower()]

    if len(matching) == 1:
        return matching[0]
    elif len(matching) > 1:
        titles = [f"'{t.title}'" for t in matching]
        return ToolResponse(
            success=False,
            message=f"Multiple tasks match '{identifier}': {', '.join(titles)}. Please be more specific."
        )
    else:
        return ToolResponse(
            success=False,
            message=f"Task '{identifier}' not found"
        )
```

**Validation**:
- [ ] Soft deletes (sets deleted_at)
- [ ] Task appears in history after delete

---

## Step 3: AI Agent

### T3.1: Add OpenAI Dependency

**File**: `backend/requirements.txt`

**Action**: Modify existing file - add OpenAI package

**Code to Add**:
```
# AI Agent
openai>=1.0.0
```

**Validation**:
- [ ] pip install succeeds
- [ ] openai package importable

---

### T3.2: Create Agents Module

**File**: `backend/app/agents/__init__.py`

**Action**: Create directory and init file

**Code**:
```python
"""
AI Agents Module
OpenAI Agents SDK integration for natural language task management.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-011 to FR-018)
"""

from app.agents.task_agent import TaskAgent

__all__ = ["TaskAgent"]
```

**Validation**:
- [ ] Directory created
- [ ] Init file created

---

### T3.3: Create Task Agent

**File**: `backend/app/agents/task_agent.py`

**Action**: Create new file

**Code**:
```python
"""
Task Agent
OpenAI-powered agent for natural language task management.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-011 to FR-018)
"""

from openai import OpenAI
from sqlmodel import Session
from typing import Optional, List, Dict, Any
import json

from app.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task
from app.config import settings


# OpenAI Function Definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task. Use this when the user wants to add, create, or make a new task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title/name of the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Initial status. Default is 'pending'. Use 'in_progress' if user says 'in progress' or 'started'."
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
            "description": "List all tasks. Use when user asks to see, show, list, or view their tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["all", "pending", "in_progress", "completed"],
                        "description": "Filter by status. Use 'all' to show everything."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed. Use when user says they finished, completed, or done with a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "The task title or ID to mark as complete"
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
            "description": "Update a task's title, description, or status. Use when user wants to change, edit, modify, or update a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "The task title or ID to update"
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
            "description": "Delete a task (moves to history). Use when user wants to delete, remove, or trash a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "The task title or ID to delete"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    }
]


SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their todo tasks through natural language conversation.

Your capabilities:
- Add new tasks (with title, optional description, and status)
- List tasks (all or filtered by status: pending, in_progress, completed)
- Mark tasks as complete
- Update task details (title, description, status)
- Delete tasks (soft delete - they go to history and can be restored)

IMPORTANT: When parsing "add task" commands in this format:
"add task Title: X description: Y status: Z"
- Extract the title after "Title:"
- Extract the description after "description:"
- Extract the status after "status:" (convert "in progress" to "in_progress")

For example:
"add task Title: Read book description: Daily 10 pages status: in progress"
Should create: title="Read book", description="Daily 10 pages", status="in_progress"

Also handle natural formats like:
- "add a task to buy groceries" -> title="buy groceries"
- "create task: call mom" -> title="call mom"
- "remind me to exercise" -> title="exercise"

When referencing existing tasks, try to match by title. If multiple tasks match, ask for clarification.

Always confirm actions taken with a brief, friendly response.
Keep responses concise but helpful."""


class TaskAgent:
    """
    AI Agent for natural language task management.
    Uses OpenAI function calling to execute MCP tools.
    """

    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL or "gpt-4-turbo-preview"

    def _execute_tool(
        self,
        session: Session,
        user_id: int,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """
        Execute an MCP tool and return JSON result.

        Args:
            session: Database session
            user_id: User making the request
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            JSON string with tool result
        """
        tool_map = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "update_task": update_task,
            "delete_task": delete_task
        }

        tool_func = tool_map.get(tool_name)
        if not tool_func:
            return json.dumps({
                "success": False,
                "message": f"Unknown tool: {tool_name}"
            })

        try:
            result = tool_func(session, user_id, **arguments)
            return json.dumps(result.model_dump())
        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"Tool execution error: {str(e)}"
            })

    def chat(
        self,
        session: Session,
        user_id: int,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process a chat message and return the response.

        Args:
            session: Database session
            user_id: User making the request
            message: User's message
            conversation_history: Previous messages for context

        Returns:
            Assistant's response string
        """
        # Build messages array
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history (limited to last N messages)
        if conversation_history:
            context_limit = settings.CHAT_CONTEXT_MESSAGES or 20
            messages.extend(conversation_history[-context_limit:])

        # Add current message
        messages.append({"role": "user", "content": message})

        try:
            # Call OpenAI with tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=500,
                temperature=0.7
            )

            assistant_message = response.choices[0].message

            # Handle tool calls if present
            if assistant_message.tool_calls:
                # Add assistant's message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool and collect results
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    result = self._execute_tool(
                        session, user_id, tool_name, arguments
                    )

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

                # Get final response after tool execution
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )

                return final_response.choices[0].message.content or "Done!"

            # No tool calls, return direct response
            return assistant_message.content or "I'm not sure how to help with that. Try asking me to add, list, complete, update, or delete tasks."

        except Exception as e:
            return f"I encountered an error processing your request. Please try again. (Error: {str(e)})"
```

**Validation**:
- [ ] Agent initializes with OpenAI client
- [ ] Tools are called correctly
- [ ] Multi-turn context works
- [ ] Error handling is graceful

---

## Step 4: Chat API

### T4.1: Create Chat Router

**File**: `backend/app/api/v1/chat.py`

**Action**: Create new file

**Code**:
```python
"""
Chat API Router
Endpoints for AI chatbot interaction.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-019 to FR-026)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, UTC
from typing import Dict, List
import time

from app.db.session import get_session
from app.auth.dependencies import get_current_user_id
from app.models.conversation import Conversation
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    ConversationListResponse
)
from app.agents.task_agent import TaskAgent
from app.config import settings


router = APIRouter()

# Simple in-memory rate limiter
# For production, use Redis or similar
_rate_limit_cache: Dict[str, List[float]] = {}


def _check_rate_limit(user_id: int) -> bool:
    """
    Check if user has exceeded rate limit.

    Returns True if allowed, False if rate limited.
    """
    now = time.time()
    key = f"chat:{user_id}"
    rate_limit = settings.CHAT_RATE_LIMIT or 10

    if key not in _rate_limit_cache:
        _rate_limit_cache[key] = []

    # Remove entries older than 60 seconds
    _rate_limit_cache[key] = [
        t for t in _rate_limit_cache[key]
        if now - t < 60
    ]

    if len(_rate_limit_cache[key]) >= rate_limit:
        return False

    _rate_limit_cache[key].append(now)
    return True


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def send_chat_message(
    user_id: int,
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Process a chat message and return AI response.

    - Validates user authorization
    - Applies rate limiting
    - Manages conversation state
    - Calls AI agent for response
    """
    # Verify user owns the resource
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    # Check rate limit
    if not _check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 messages per minute."
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
        conversation = Conversation(
            user_id=user_id,
            messages=[]
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Build conversation history for context
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in (conversation.messages or [])
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

    new_messages = list(conversation.messages or [])
    new_messages.append({
        "role": "user",
        "content": request.message,
        "timestamp": now
    })
    new_messages.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": now
    })

    conversation.messages = new_messages
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
    """List all conversations for the user."""
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
        preview = "New conversation"
        if conv.messages:
            for msg in conv.messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "")
                    preview = content[:50] + "..." if len(content) > 50 else content
                    break

        summaries.append(ConversationSummary(
            id=conv.id,
            preview=preview,
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return {
        "id": conversation.id,
        "messages": conversation.messages,
        "created_at": conversation.created_at
    }


@router.delete("/{user_id}/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    user_id: int,
    conversation_id: str,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Delete a conversation."""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    session.delete(conversation)
    session.commit()

    return None
```

**Validation**:
- [ ] POST /api/{user_id}/chat works
- [ ] GET conversations list works
- [ ] GET single conversation works
- [ ] DELETE conversation works
- [ ] Rate limiting enforced
- [ ] User isolation enforced

---

### T4.2: Register Chat Router in Main

**File**: `backend/app/main.py`

**Action**: Modify existing file

**Changes**:
1. Add import: `from app.api.v1 import chat`
2. Add router: `app.include_router(chat.router, prefix="/api", tags=["Chat"])`

**Location**: After existing router registrations (around line 51)

**Code to Add**:
```python
# Add with other imports at top
from app.api.v1 import auth, tasks, profile, chat

# Add with other router registrations
app.include_router(chat.router, prefix="/api", tags=["Chat"])
```

**Validation**:
- [ ] Server starts without errors
- [ ] /docs shows new Chat endpoints

---

### T4.3: Update API v1 __init__.py

**File**: `backend/app/api/v1/__init__.py`

**Action**: Modify existing file - add chat import

**Code to Add**:
```python
from app.api.v1 import chat
```

**Validation**:
- [ ] Import works

---

### T4.4: Create Database Table

**Action**: The Conversation table will be auto-created by SQLModel on startup if `init_db()` is called. For production, create a migration.

**Optional Migration File**: `backend/app/migrations/002_add_conversations.py`

```python
"""
Migration: Add conversations table
"""

from sqlmodel import SQLModel
from app.db.session import engine
from app.models.conversation import Conversation

def upgrade():
    """Create conversations table."""
    SQLModel.metadata.create_all(engine, tables=[Conversation.__table__])

def downgrade():
    """Drop conversations table."""
    Conversation.__table__.drop(engine)

if __name__ == "__main__":
    upgrade()
    print("Migration complete: conversations table created")
```

**Validation**:
- [ ] Table exists in database
- [ ] Can insert/query conversations

---

## Step 5: Frontend Chat UI

### T5.1: Create Chat Types

**File**: `frontend/types/chat.ts`

**Action**: Create new file

**Code**:
```typescript
/**
 * Chat TypeScript Types
 * Type definitions for chat feature.
 *
 * Spec Reference: specs/phase-3-chatbot-spec.md
 */

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

export interface ConversationListResponse {
  conversations: ConversationSummary[];
}
```

**Validation**:
- [ ] Types are exported
- [ ] No TypeScript errors

---

### T5.2: Create Chat API Client

**File**: `frontend/lib/chat-api.ts`

**Action**: Create new file

**Code**:
```typescript
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
  const response = await apiPost(`/api/${userId}/chat`, request);

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
  const response = await apiGet(`/api/${userId}/conversations`);

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
    `/api/${userId}/conversations/${conversationId}`
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
    `/api/${userId}/conversations/${conversationId}`
  );

  if (!response.ok) {
    throw new Error("Failed to delete conversation");
  }
}
```

**Validation**:
- [ ] Functions work with backend
- [ ] Error handling works

---

### T5.3: Create ChatMessage Component

**File**: `frontend/components/chat/ChatMessage.tsx`

**Action**: Create directory and file

**Code**:
```typescript
/**
 * ChatMessage Component
 * Displays a single chat message bubble.
 */

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
        <p className="text-sm whitespace-pre-wrap break-words">
          {message.content}
        </p>
      </div>
    </div>
  );
}
```

**Validation**:
- [ ] User messages on right
- [ ] Assistant messages on left
- [ ] Styling matches theme

---

### T5.4: Create ChatInput Component

**File**: `frontend/components/chat/ChatInput.tsx`

**Action**: Create new file

**Code**:
```typescript
/**
 * ChatInput Component
 * Text input for sending chat messages.
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

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 120) + "px";
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
      className="p-3 border-t"
      style={{ borderColor: "var(--card-border)" }}
    >
      <div className="flex gap-2 items-end">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          disabled={disabled}
          rows={1}
          maxLength={2000}
          className="flex-1 px-4 py-2 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-[#6db9d4] transition-all min-h-[40px]"
          style={{
            background: "var(--input-bg)",
            color: "var(--input-text)",
          }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="p-2 rounded-xl text-white hover:opacity-90 transition-opacity disabled:opacity-50 flex-shrink-0"
          style={{ background: "#6db9d4" }}
          aria-label="Send message"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
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
    </div>
  );
}
```

**Validation**:
- [ ] Enter sends message
- [ ] Shift+Enter adds newline
- [ ] Button disabled when empty
- [ ] Max length enforced

---

### T5.5: Create ChatContainer Component

**File**: `frontend/components/chat/ChatContainer.tsx`

**Action**: Create new file

**Code**:
```typescript
/**
 * ChatContainer Component
 * Main chat interface with messages and input.
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
}

export function ChatContainer({ userId, isOpen, onClose }: ChatContainerProps) {
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

  if (!isOpen) return null;

  return (
    <div
      className="fixed bottom-20 right-4 w-[380px] h-[500px] rounded-2xl shadow-2xl flex flex-col overflow-hidden z-50 sm:w-96"
      style={{
        background: "var(--card-bg)",
        border: "1px solid var(--card-border)",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b flex-shrink-0"
        style={{
          borderColor: "var(--card-border)",
          background: "var(--accent-bg)",
        }}
      >
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span
            className="font-semibold text-sm"
            style={{ color: "var(--foreground)" }}
          >
            Task Assistant
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleNewChat}
            className="p-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
            title="New Chat"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style={{ color: "var(--foreground)" }}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
            title="Close"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style={{ color: "var(--foreground)" }}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div
            className="text-center py-8"
            style={{ color: "var(--foreground)", opacity: 0.6 }}
          >
            <div className="text-3xl mb-3">👋</div>
            <p className="text-sm font-medium">Hi! I'm your task assistant.</p>
            <p className="text-xs mt-2 opacity-80">
              Try: "Add a task to buy groceries"
            </p>
            <p className="text-xs mt-1 opacity-80">
              Or: "Show my tasks"
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div
              className="px-4 py-3 rounded-2xl rounded-bl-sm"
              style={{ background: "var(--accent-bg)" }}
            >
              <div className="flex space-x-1.5">
                <div
                  className="w-2 h-2 rounded-full animate-bounce"
                  style={{ background: "var(--foreground)", opacity: 0.4, animationDelay: "0ms" }}
                ></div>
                <div
                  className="w-2 h-2 rounded-full animate-bounce"
                  style={{ background: "var(--foreground)", opacity: 0.4, animationDelay: "150ms" }}
                ></div>
                <div
                  className="w-2 h-2 rounded-full animate-bounce"
                  style={{ background: "var(--foreground)", opacity: 0.4, animationDelay: "300ms" }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="text-center py-2">
            <p className="text-sm text-red-500">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-xs text-red-400 hover:text-red-300 mt-1"
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
```

**Validation**:
- [ ] Opens/closes correctly
- [ ] Messages display properly
- [ ] Loading state shows
- [ ] Error handling works
- [ ] New chat resets state

---

### T5.6: Create Chat Index Export

**File**: `frontend/components/chat/index.ts`

**Action**: Create new file

**Code**:
```typescript
export { ChatContainer } from "./ChatContainer";
export { ChatMessage } from "./ChatMessage";
export { ChatInput } from "./ChatInput";
```

**Validation**:
- [ ] Exports work

---

### T5.7: Integrate Chat into Dashboard

**File**: `frontend/app/dashboard/page.tsx`

**Action**: Modify existing file

**Changes**:

1. Add import at top:
```typescript
import { ChatContainer } from "@/components/chat";
```

2. Add state variables (inside component, with other useState):
```typescript
const [isChatOpen, setIsChatOpen] = useState(false);
const [userId, setUserId] = useState<number | null>(null);
```

3. Add useEffect to get user ID (after other useEffects):
```typescript
// Get user ID from JWT token
useEffect(() => {
  const token = localStorage.getItem("jwt_token");
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setUserId(parseInt(payload.sub));
    } catch (e) {
      console.error("Failed to parse token", e);
    }
  }
}, []);
```

4. Add chat button and container at end of JSX (before final closing `</div>`):
```typescript
{/* Chat Button and Container */}
{userId && (
  <>
    {/* Floating Chat Button */}
    <button
      onClick={() => setIsChatOpen(!isChatOpen)}
      className={`fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-lg flex items-center justify-center hover:scale-105 transition-transform z-40 ${
        isChatOpen ? "rotate-0" : ""
      }`}
      style={{ background: "#e08b3d" }}
      aria-label={isChatOpen ? "Close chat" : "Open chat"}
    >
      {isChatOpen ? (
        <svg
          className="w-6 h-6 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      ) : (
        <svg
          className="w-6 h-6 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      )}
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

**Validation**:
- [ ] Chat button visible on dashboard
- [ ] Click opens chat
- [ ] Click again closes chat
- [ ] Full chat flow works

---

## Execution Checklist

### Pre-Implementation
- [ ] Read Phase-2 code to understand patterns
- [ ] Ensure OPENAI_API_KEY is available
- [ ] Backend server running
- [ ] Frontend dev server running

### Step 1: Database & Models
- [ ] T1.1: Create Conversation model
- [ ] T1.2: Create Chat schemas
- [ ] T1.3: Update models __init__
- [ ] T1.4: Update config with chat settings
- [ ] **Verify**: Can create Conversation in DB

### Step 2: MCP Tools
- [ ] T2.1: Create MCP module structure
- [ ] T2.2: Create ToolResponse base
- [ ] T2.3: Create add_task tool
- [ ] T2.4: Create list_tasks tool
- [ ] T2.5: Create complete_task tool
- [ ] T2.6: Create update_task tool
- [ ] T2.7: Create delete_task tool
- [ ] **Verify**: All tools work independently

### Step 3: AI Agent
- [ ] T3.1: Add OpenAI dependency
- [ ] T3.2: Create agents module
- [ ] T3.3: Create TaskAgent
- [ ] **Verify**: Agent processes natural language

### Step 4: Chat API
- [ ] T4.1: Create chat router
- [ ] T4.2: Register router in main.py
- [ ] T4.3: Update API v1 __init__
- [ ] T4.4: Verify database table
- [ ] **Verify**: POST /api/{user_id}/chat works

### Step 5: Frontend Chat UI
- [ ] T5.1: Create chat types
- [ ] T5.2: Create chat API client
- [ ] T5.3: Create ChatMessage component
- [ ] T5.4: Create ChatInput component
- [ ] T5.5: Create ChatContainer component
- [ ] T5.6: Create chat index export
- [ ] T5.7: Integrate into dashboard
- [ ] **Verify**: Full E2E chat flow works

### Post-Implementation
- [ ] Test: Add task via chat
- [ ] Test: List tasks via chat
- [ ] Test: Complete task via chat
- [ ] Test: Update task via chat
- [ ] Test: Delete task via chat
- [ ] Test: Rate limiting works
- [ ] Test: Theme switching works
- [ ] Test: Mobile responsive

---

## Quick Reference

### New Backend Files (13)
```
backend/app/
├── models/conversation.py
├── schemas/chat.py
├── mcp/
│   ├── __init__.py
│   └── tools/
│       ├── __init__.py
│       ├── base.py
│       ├── add_task.py
│       ├── list_tasks.py
│       ├── complete_task.py
│       ├── update_task.py
│       └── delete_task.py
├── agents/
│   ├── __init__.py
│   └── task_agent.py
└── api/v1/chat.py
```

### New Frontend Files (6)
```
frontend/
├── types/chat.ts
├── lib/chat-api.ts
└── components/chat/
    ├── index.ts
    ├── ChatContainer.tsx
    ├── ChatMessage.tsx
    └── ChatInput.tsx
```

### Modified Files (4)
```
backend/app/main.py          # Add chat router
backend/app/config.py        # Add OpenAI settings
backend/app/models/__init__.py  # Add Conversation import
frontend/app/dashboard/page.tsx  # Add chat UI
```
