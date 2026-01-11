from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from typing import List
from uuid import uuid4


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    __table_args__ = {"schema": "public"}

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="UUID for conversation"
    )
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of this conversation"
    )
    messages: List[dict] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, default=list),
        description="Array of {role, content, timestamp} objects"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When conversation started"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last message timestamp"
    )
