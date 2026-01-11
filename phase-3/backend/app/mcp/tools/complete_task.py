"""
Complete Task Tool
Marks a task as completed.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-004)
"""

from sqlmodel import Session, select
from datetime import datetime, UTC
from typing import Union

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


def _find_task(session: Session, user_id: int, identifier: str) -> Union[Task, ToolResponse]:
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
