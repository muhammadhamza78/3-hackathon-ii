"""
Task CRUD API Endpoints
FastAPI router for task create, read, update, delete operations.

Spec Reference: specs/features/task-crud.md (FR1-FR6)
Plan Reference: specs/features/plans/task-crud-plan.md
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, UTC
from app.db.session import get_session
from app.auth.dependencies import get_current_user_id
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskListResponse



router = APIRouter()


# ---------------------------
# Create Task
# ---------------------------
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreateRequest,
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    task = Task(
        title=request.title,
        description=request.description,
        status=request.status,
        user_id=user_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskResponse.model_validate(task)


# ---------------------------
# Clear Completed Tasks (Soft Delete)
# ---------------------------
@router.post("/clear-completed", status_code=status.HTTP_204_NO_CONTENT)
async def clear_completed_tasks(
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id, Task.status == TaskStatus.COMPLETED, Task.deleted_at.is_(None))
    ).all()

    for task in tasks:
        task.deleted_at = datetime.now(UTC)
        task.updated_at = datetime.now(UTC)
        session.add(task)
    session.commit()


# ---------------------------
# Task History (Deleted Tasks) - MOVED UP!
# ---------------------------
@router.get("/history", response_model=TaskListResponse)
async def get_task_history(
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskListResponse:
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id, Task.deleted_at.isnot(None))
        .order_by(Task.deleted_at.desc())
    ).all()
    return TaskListResponse(tasks=[TaskResponse.model_validate(task) for task in tasks])


# ---------------------------
# Clear Task History (Hard Delete) - MOVED UP!
# ---------------------------
@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_task_history(
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id, Task.deleted_at.isnot(None))
    ).all()
    for task in tasks:
        session.delete(task)
    session.commit()


# ---------------------------
# List Tasks
# ---------------------------
@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status_filter: str | None = None,
    sort_order: str = "asc",
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskListResponse:
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="sort_order must be 'asc' or 'desc'")
    if status_filter and status_filter not in ["pending", "in_progress", "completed"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="status_filter must be 'pending', 'in_progress', or 'completed'")

    statement = select(Task).where(Task.user_id == user_id, Task.deleted_at.is_(None))
    if status_filter:
        statement = statement.where(Task.status == status_filter)

    statement = statement.order_by(Task.created_at.asc() if sort_order == "asc" else Task.created_at.desc())
    tasks = session.exec(statement).all()
    return TaskListResponse(tasks=[TaskResponse.model_validate(task) for task in tasks])


# ---------------------------
# Get Task by ID
# ---------------------------
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse.model_validate(task)


# ---------------------------
# Update Task
# ---------------------------
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: TaskUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    if request.status is not None:
        task.status = request.status

    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskResponse.model_validate(task)


# ---------------------------
# Soft Delete Task
# ---------------------------
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id, Task.deleted_at.is_(None))
    ).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.deleted_at = datetime.now(UTC)
    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()


# ---------------------------
# Restore Deleted Task
# ---------------------------
@router.post("/{task_id}/restore", response_model=TaskResponse)
async def restore_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id, Task.deleted_at.isnot(None))
    ).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found in history")

    task.deleted_at = None
    task.updated_at = datetime.now(UTC)
    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskResponse.model_validate(task)
