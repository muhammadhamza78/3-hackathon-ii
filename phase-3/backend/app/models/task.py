"""
Task Model
Defines the Task entity for the task CRUD feature.

Spec Reference: specs/features/task-crud.md (Task Data Model)
Plan Reference: specs/features/plans/data-model.md
"""

from sqlmodel import SQLModel, Field
from datetime import datetime, UTC
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    """
    Task status enum with string values.

    Values:
    - PENDING: Task not yet started (default)
    - IN_PROGRESS: Task currently being worked on
    - COMPLETED: Task finished

    Spec: specs/features/task-crud.md (Task Status Values)
    Research: specs/features/plans/research.md (R1: Enum Implementation)
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    User Isolation: All queries MUST filter by user_id.
    Constitution: Principle III (NON-NEGOTIABLE)

    Spec: specs/features/task-crud.md (FR1-FR6)
    Plan: specs/features/plans/data-model.md (Task Entity)
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    user_id: int = Field(foreign_key="users.id", index=True)
    deleted_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        use_enum_values = True  # Store enum as string in database
