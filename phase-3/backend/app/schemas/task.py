# """
# Task Request/Response Schemas
# Pydantic models for task CRUD API validation.

# Spec Reference: specs/features/task-crud.md (FR1-FR5)
# Plan Reference: specs/features/plans/data-model.md (Pydantic Schemas)
# """










# from pydantic import BaseModel, Field
# from typing import Optional
# from datetime import datetime
# from app.models.task import TaskStatus


# class TaskCreateRequest(BaseModel):
#     """
#     Request schema for creating a new task.

#     Spec: specs/features/task-crud.md (FR1: Create Task)
#     Contract: specs/features/plans/contracts/task-create.json
#     """
#     title: str = Field(..., min_length=1, max_length=200, description="Task title")
#     description: Optional[str] = Field(None, max_length=2000, description="Task description (optional)")
#     status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "title": "Buy groceries",
#                 "description": "Milk, eggs, bread",
#                 "status": "pending"
#             }
#         }


# class TaskUpdateRequest(BaseModel):
#     """
#     Request schema for updating an existing task (partial updates).

#     All fields are optional - only provided fields will be updated.

#     Spec: specs/features/task-crud.md (FR4: Update Task)
#     Contract: specs/features/plans/contracts/task-update.json
#     """
#     title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
#     description: Optional[str] = Field(None, max_length=2000, description="Task description")
#     status: Optional[TaskStatus] = Field(None, description="Task status")

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "title": "Buy groceries and cook dinner",
#                 "status": "in_progress"
#             }
#         }


# class TaskResponse(BaseModel):
#     """
#     Response schema for a single task.

#     Returned by all task endpoints (create, get, update, list).

#     Spec: specs/features/task-crud.md (FR1-FR5 responses)
#     """
#     id: int
#     title: str
#     description: Optional[str]
#     status: TaskStatus
#     user_id: int
#     deleted_at: Optional[datetime] = None
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True  # ORM mode for SQLModel conversion
#         json_schema_extra = {
#             "example": {
#                 "id": 123,
#                 "title": "Buy groceries",
#                 "description": "Milk, eggs, bread",
#                 "status": "pending",
#                 "user_id": 456,
#                 "deleted_at": None,
#                 "created_at": "2025-12-30T10:00:00Z",
#                 "updated_at": "2025-12-30T10:00:00Z"
#             }
#         }


# class TaskListResponse(BaseModel):
#     """
#     Response schema for task list endpoint.

#     Returns array of tasks owned by authenticated user.

#     Spec: specs/features/task-crud.md (FR2: List All Tasks)
#     Contract: specs/features/plans/contracts/task-list.json
#     """
#     tasks: list[TaskResponse]

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "tasks": [
#                     {
#                         "id": 123,
#                         "title": "Buy groceries",
#                         "description": "Milk, eggs, bread",
#                         "status": "pending",
#                         "user_id": 456,
#                         "created_at": "2025-12-30T10:00:00Z",
#                         "updated_at": "2025-12-30T10:00:00Z"
#                     },
#                     {
#                         "id": 124,
#                         "title": "Write report",
#                         "description": None,
#                         "status": "in_progress",
#                         "user_id": 456,
#                         "created_at": "2025-12-30T11:00:00Z",
#                         "updated_at": "2025-12-30T11:30:00Z"
#                     }
#                 ]
#             }
#         }


















"""
Task Request/Response Schemas
Pydantic models for task CRUD API validation.

Spec Reference: specs/features/task-crud.md (FR1-FR5)
Plan Reference: specs/features/plans/data-model.md (Pydantic Schemas)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskStatus


class TaskCreateRequest(BaseModel):
    """
    Request schema for creating a new task.

    Spec: FR1: Create Task
    """
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description (optional)")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete Hackathon",
                "description": "Participate and finish the hackathon project",
                "status": "pending"
            }
        }


class TaskUpdateRequest(BaseModel):
    """
    Request schema for updating an existing task (partial updates).

    All fields are optional.
    Spec: FR4: Update Task
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    status: Optional[TaskStatus] = Field(None, description="Task status")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete Hackathon and submit report",
                "status": "in_progress"
            }
        }


class TaskResponse(BaseModel):
    """
    Response schema for a single task.
    Spec: FR1-FR5 responses
    """
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    user_id: int
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ORM mode for SQLModel conversion
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Complete Hackathon",
                "description": "Participate and finish the hackathon project",
                "status": "pending",
                "user_id": 123,
                "deleted_at": None,
                "created_at": "2026-01-12T10:00:00Z",
                "updated_at": "2026-01-12T10:30:00Z"
            }
        }


class TaskListResponse(BaseModel):
    """
    Response schema for task list endpoint.
    Returns array of tasks owned by authenticated user.
    Spec: FR2: List All Tasks
    """
    tasks: List[TaskResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Complete Hackathon",
                        "description": "Participate and finish the hackathon project",
                        "status": "pending",
                        "user_id": 123,
                        "created_at": "2026-01-12T10:00:00Z",
                        "updated_at": "2026-01-12T10:30:00Z"
                    },
                    {
                        "id": 2,
                        "title": "Write report",
                        "description": None,
                        "status": "in_progress",
                        "user_id": 123,
                        "created_at": "2026-01-12T11:00:00Z",
                        "updated_at": "2026-01-12T11:30:00Z"
                    }
                ]
            }
        }
