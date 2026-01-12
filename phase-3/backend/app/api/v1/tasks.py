# """
# Task CRUD API Endpoints
# FastAPI router for task create, read, update, delete operations.

# Spec Reference: specs/features/task-crud.md (FR1-FR6)
# Plan Reference: specs/features/plans/task-crud-plan.md
# """

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlmodel import Session, select
# from datetime import datetime, UTC
# from app.db.session import get_session
# from app.auth.dependencies import get_current_user_id
# from app.models.task import Task, TaskStatus
# from app.schemas.task import (
#     TaskCreateRequest,
#     TaskUpdateRequest,
#     TaskResponse,
#     TaskListResponse
# )

# router = APIRouter()


# @router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
# async def create_task(
#     request: TaskCreateRequest,
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> TaskResponse:
#     """
#     Create a new task for the authenticated user.

#     Spec: specs/features/task-crud.md (FR1: Create Task)
#     Contract: specs/features/plans/contracts/task-create.json

#     Args:
#         request: Task creation data (title, description, status)
#         user_id: Authenticated user ID (auto-extracted from JWT)
#         session: Database session

#     Returns:
#         TaskResponse: Created task with auto-generated ID and timestamps

#     Raises:
#         HTTPException 401: Missing or invalid JWT token
#         HTTPException 422: Validation error (title too long, invalid status, etc.)

#     User Isolation: user_id is auto-assigned from JWT (never from request body)
#     """
#     # Create task with user_id from JWT
#     task = Task(
#         title=request.title,
#         description=request.description,
#         status=request.status,
#         user_id=user_id,  # Auto-assign from JWT (Constitution III)
#         created_at=datetime.now(UTC),
#         updated_at=datetime.now(UTC)
#     )

#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     return TaskResponse.model_validate(task)


# @router.get("", response_model=TaskListResponse, status_code=status.HTTP_200_OK)
# async def list_tasks(
#     status_filter: str | None = None,
#     sort_order: str = "asc",
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> TaskListResponse:
#     """
#     List all active (non-deleted) tasks for the authenticated user.

#     Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-009 to FR-015)

#     Args:
#         status_filter: Filter by status (pending, in_progress, completed) - optional
#         sort_order: Sort order (asc=ascending/oldest first, desc=descending/newest first) - default asc
#         user_id: Authenticated user ID (auto-extracted from JWT)
#         session: Database session

#     Returns:
#         TaskListResponse: Array of active tasks owned by user

#     Raises:
#         HTTPException 401: Missing or invalid JWT token
#         HTTPException 400: Invalid status_filter or sort_order

#     User Isolation: Returns ONLY tasks where user_id matches authenticated user
#     """
#     # Validate sort order
#     if sort_order not in ["asc", "desc"]:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="sort_order must be 'asc' or 'desc'"
#         )

#     # Validate status filter if provided
#     if status_filter and status_filter not in ["pending", "in_progress", "completed"]:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="status_filter must be 'pending', 'in_progress', or 'completed'"
#         )

#     # Query tasks with user isolation and exclude soft-deleted tasks
#     statement = (
#         select(Task)
#         .where(Task.user_id == user_id)
#         .where(Task.deleted_at.is_(None))  # Only active tasks
#     )

#     # Apply status filter if provided
#     if status_filter:
#         statement = statement.where(Task.status == status_filter)

#     # Apply sorting
#     if sort_order == "asc":
#         statement = statement.order_by(Task.created_at.asc())
#     else:
#         statement = statement.order_by(Task.created_at.desc())

#     tasks = session.exec(statement).all()

#     # Convert to response models
#     task_responses = [TaskResponse.model_validate(task) for task in tasks]

#     return TaskListResponse(tasks=task_responses)


# @router.get("/history", response_model=TaskListResponse, status_code=status.HTTP_200_OK)
# async def get_task_history(
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> TaskListResponse:
#     """
#     Get all deleted tasks (history) for the authenticated user.

#     Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-019, FR-022)

#     Args:
#         user_id: Authenticated user ID (auto-extracted from JWT)
#         session: Database session

#     Returns:
#         TaskListResponse: Array of deleted tasks, ordered by deleted_at DESC

#     Raises:
#         HTTPException 401: Missing or invalid JWT token

#     User Isolation: Returns ONLY deleted tasks where user_id matches authenticated user
#     """
#     # Query deleted tasks with user isolation
#     statement = (
#         select(Task)
#         .where(Task.user_id == user_id)
#         .where(Task.deleted_at.isnot(None))  # Only deleted tasks
#         .order_by(Task.deleted_at.desc())
#     )

#     tasks = session.exec(statement).all()

#     # Convert to response models
#     task_responses = [TaskResponse.model_validate(task) for task in tasks]

#     return TaskListResponse(tasks=task_responses)


# @router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
# async def clear_task_history(
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> None:
#     """
#     Permanently delete all tasks in history (hard delete).

#     Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-024, FR-025)

#     Args:
#         user_id: Authenticated user ID (auto-extracted from JWT)
#         session: Database session

#     Returns:
#         None: 204 No Content on successful permanent deletion

#     Raises:
#         HTTPException 401: Missing or invalid JWT token

#     User Isolation: Only deletes tasks where user_id matches authenticated user
#     Warning: This is a PERMANENT deletion and cannot be undone
#     """
#     # Query all deleted tasks with user isolation
#     statement = select(Task).where(
#         Task.user_id == user_id,
#         Task.deleted_at.isnot(None)  # Only deleted tasks
#     )
#     tasks = session.exec(statement).all()

#     # Hard delete all history tasks
#     for task in tasks:
#         session.delete(task)

#     session.commit()

#     # Return 204 No Content (no response body)


# @router.post("/clear-completed", status_code=status.HTTP_204_NO_CONTENT)
# async def clear_completed_tasks(
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> None:
#     """
#     Soft delete all completed tasks (move to history).

#     Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-020)

#     Args:
#         user_id: Authenticated user ID (auto-extracted from JWT)
#         session: Database session

#     Returns:
#         None: 204 No Content on successful soft deletion

#     Raises:
#         HTTPException 401: Missing or invalid JWT token

#     User Isolation: Only affects tasks where user_id matches authenticated user
#     """
#     # Query all completed active tasks with user isolation
#     statement = select(Task).where(
#         Task.user_id == user_id,
#         Task.status == TaskStatus.COMPLETED,
#         Task.deleted_at.is_(None)  # Only active tasks
#     )
#     tasks = session.exec(statement).all()

#     # Soft delete all completed tasks
#     for task in tasks:
#         task.deleted_at = datetime.now(UTC)
#         task.updated_at = datetime.now(UTC)
#         session.add(task)

#     session.commit()

#     # Return 204 No Content (no response body)


# @router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
# async def get_task(
#     task_id: int,
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> TaskResponse:
#     """
#     Get a single task by ID (only if owned by authenticated user).

#     Spec: specs/features/task-crud.md (FR3: Get Single Task)
#     Contract: specs/features/plans/contracts/task-get.json

#     Args:
#         task_id: Task ID from path parameter
#         user_id: Authenticated user ID (auto-extracted from JWT)
#         session: Database session

#     Returns:
#         TaskResponse: Task details if found and owned by user

#     Raises:
#         HTTPException 401: Missing or invalid JWT token
#         HTTPException 404: Task not found OR belongs to different user

#     User Isolation: Returns 404 if task exists but belongs to different user
#     Research: specs/features/plans/research.md (R3: 404 for Cross-User Access)
#     """
#     # Query with user isolation (Constitution III - NON-NEGOTIABLE)
#     # Returns None if task doesn't exist OR belongs to different user
#     statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
#     task = session.exec(statement).first()

#     if not task:
#         # Return 404 (not 403) to prevent user enumeration
#         # Same response whether task doesn't exist or belongs to other user
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found"
#         )

#     return TaskResponse.model_validate(task)


# @router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
# async def update_task(
#     task_id: int,
#     request: TaskUpdateRequest,
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> TaskResponse:
#     """
#     Update an existing task (only if owned by authenticated user).

#     Partial updates supported - only provided fields will be updated.

#     Spec: specs/features/task-crud.md (FR4: Update Task)
#     Contract: specs/features/plans/contracts/task-update.json

#     Args:
#         task_id: Task ID from path parameter
#         request: Task update data (all fields optional)
#         user_id: Authenticated user ID (auto-extracted from JWT)
#         session: Database session

#     Returns:
#         TaskResponse: Updated task with auto-updated updated_at

#     Raises:
#         HTTPException 401: Missing or invalid JWT token
#         HTTPException 404: Task not found OR belongs to different user
#         HTTPException 422: Validation error (title too long, invalid status, etc.)

#     User Isolation: Returns 404 if task exists but belongs to different user
#     Immutability: created_at and user_id cannot be changed
#     """
#     # Query with user isolation (Constitution III - NON-NEGOTIABLE)
#     statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
#     task = session.exec(statement).first()

#     if not task:
#         # Return 404 (not 403) to prevent user enumeration
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found"
#         )

#     # Update only provided fields (partial update)
#     if request.title is not None:
#         task.title = request.title
#     if request.description is not None:
#         task.description = request.description
#     if request.status is not None:
#         task.status = request.status

#     # Auto-update updated_at timestamp
#     task.updated_at = datetime.now(UTC)

#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     return TaskResponse.model_validate(task)


# @router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_task(
#     task_id: int,
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> None:
#     """
#     Soft delete a task (move to history).

#     Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-021)

#     Args:
#         task_id: Task ID from path parameter
#         user_id: Authenticated user ID (auto-extracted from JWT)
#         session: Database session

#     Returns:
#         None: 204 No Content on successful soft deletion

#     Raises:
#         HTTPException 401: Missing or invalid JWT token
#         HTTPException 404: Task not found OR belongs to different user OR already deleted

#     User Isolation: Returns 404 if task exists but belongs to different user
#     """
#     # Query with user isolation - only get active tasks
#     statement = select(Task).where(
#         Task.id == task_id,
#         Task.user_id == user_id,
#         Task.deleted_at.is_(None)  # Only active tasks can be deleted
#     )
#     task = session.exec(statement).first()

#     if not task:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found"
#         )

#     # Soft delete: set deleted_at timestamp
#     task.deleted_at = datetime.now(UTC)
#     task.updated_at = datetime.now(UTC)

#     session.add(task)
#     session.commit()

#     # Return 204 No Content (no response body)


# @router.post("/{task_id}/restore", response_model=TaskResponse, status_code=status.HTTP_200_OK)
# async def restore_task(
#     task_id: int,
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> TaskResponse:
#     """
#     Restore a deleted task from history back to active tasks.

#     Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-027, FR-028)

#     Args:
#         task_id: Task ID from path parameter
#         user_id: Authenticated user ID (auto-extracted from JWT)
#         session: Database session

#     Returns:
#         TaskResponse: Restored task with deleted_at cleared

#     Raises:
#         HTTPException 401: Missing or invalid JWT token
#         HTTPException 404: Task not found OR belongs to different user OR not deleted

#     User Isolation: Returns 404 if task exists but belongs to different user
#     """
#     # Query with user isolation - only get deleted tasks
#     statement = select(Task).where(
#         Task.id == task_id,
#         Task.user_id == user_id,
#         Task.deleted_at.isnot(None)  # Only deleted tasks can be restored
#     )
#     task = session.exec(statement).first()

#     if not task:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found in history"
#         )

#     # Restore: clear deleted_at timestamp
#     task.deleted_at = None
#     task.updated_at = datetime.now(UTC)

#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     return TaskResponse.model_validate(task)













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
# Task History (Deleted Tasks)
# ---------------------------
@router.get("/history", response_model=TaskListResponse)
async def get_task_history(
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskListResponse:
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id, Task.deleted_at.isnot(None)).order_by(Task.deleted_at.desc())
    ).all()
    return TaskListResponse(tasks=[TaskResponse.model_validate(task) for task in tasks])


# ---------------------------
# Clear Task History (Hard Delete)
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
