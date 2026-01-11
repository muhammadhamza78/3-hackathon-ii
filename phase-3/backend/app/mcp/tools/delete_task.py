"""
Delete Task Tool
Soft deletes a task (moves to history).

Spec Reference: specs/phase-3-chatbot-spec.md (FR-006)
"""

from sqlmodel import Session, select
from datetime import datetime, UTC
from typing import Union

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


def _find_task(session: Session, user_id: int, identifier: str) -> Union[Task, ToolResponse]:
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
