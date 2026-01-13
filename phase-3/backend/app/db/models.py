from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from typing import Optional
import sqlalchemy as sa


class Task(SQLModel, table=True):
    """Task model for todo items"""
    
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default="", max_length=2000)
    status: str = Field(default="pending", max_length=50)  # pending, in_progress, completed
    priority: str = Field(default="medium", max_length=50)  # low, medium, high
    is_deleted: bool = Field(default=False)  # ✅ Soft delete flag
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            sa.DateTime(timezone=True),
            nullable=False,
            onupdate=datetime.utcnow
        )
    )
