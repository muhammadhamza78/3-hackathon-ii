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
