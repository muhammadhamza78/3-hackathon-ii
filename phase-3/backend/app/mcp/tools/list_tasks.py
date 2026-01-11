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
