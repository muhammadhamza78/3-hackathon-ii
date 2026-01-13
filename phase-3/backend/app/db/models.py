from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from typing import Optional
import sqlalchemy as sa


class User(SQLModel, table=True):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    profile_picture: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
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
