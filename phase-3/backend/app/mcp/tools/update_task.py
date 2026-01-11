"""
Update Task Tool
Updates an existing task's properties.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-005)
"""

from sqlmodel import Session, select
from datetime import datetime, UTC
from typing import Optional, Union

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
