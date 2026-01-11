# """
# Chat Schemas
# Pydantic models for chat API request/response validation.

# Spec Reference: specs/phase-3-chatbot-spec.md (FR-019 to FR-026)
# """

# from pydantic import BaseModel, Field
# from typing import Optional, List
# from datetime import datetime


# class ChatMessage(BaseModel):
#     """Individual message in a conversation."""
#     role: str = Field(..., description="'user' or 'assistant'")
#     content: str = Field(..., description="Message content")
#     timestamp: datetime = Field(..., description="When message was sent")


# class ChatRequest(BaseModel):
#     """Request body for POST /api/{user_id}/chat"""
#     message: str = Field(
#         ...,
#         min_length=1,
#         max_length=2000,
#         description="User's message"
#     )
#     conversation_id: Optional[str] = Field(
#         None,
#         description="Continue existing conversation, or None for new"
#     )


# class ChatResponse(BaseModel):
#     """Response from POST /api/{user_id}/chat"""
#     response: str = Field(..., description="Assistant's response")
#     conversation_id: str = Field(..., description="Conversation ID for continuity")


# class ConversationSummary(BaseModel):
#     """Summary of a conversation for listing."""
#     id: str
#     preview: str = Field(..., description="First 50 chars of first user message")
#     created_at: datetime


# class ConversationListResponse(BaseModel):
#     """Response from GET /api/{user_id}/conversations"""
#     conversations: List[ConversationSummary]


# class ConversationDetail(BaseModel):
#     """Full conversation with all messages."""
#     id: str
#     messages: List[ChatMessage]
#     created_at: datetime


"""
Chat Schemas
Pydantic models for chat API request/response validation.
Spec Reference: specs/phase-3-chatbot-spec.md (FR-019 to FR-026)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ChatMessage(BaseModel):
    """Individual message in a conversation."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When message was sent")


class ChatRequest(BaseModel):
    """Request body for POST /api/{user_id}/chat"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Continue existing conversation, or None for new"
    )


class ChatResponse(BaseModel):
    """Response from POST /api/{user_id}/chat"""
    response: str = Field(..., description="Assistant's response")
    conversation_id: str = Field(..., description="Conversation ID for continuity")
    
    @field_validator('conversation_id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings automatically."""
        if isinstance(v, UUID):
            return str(v)
        return v


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing."""
    id: str
    preview: str = Field(..., description="First 50 chars of first user message")
    created_at: datetime
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings automatically."""
        if isinstance(v, UUID):
            return str(v)
        return v


class ConversationListResponse(BaseModel):
    """Response from GET /api/{user_id}/conversations"""
    conversations: List[ConversationSummary]


class ConversationDetail(BaseModel):
    """Full conversation with all messages."""
    id: str
    messages: List[ChatMessage]
    created_at: datetime
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings automatically."""
        if isinstance(v, UUID):
            return str(v)
        return v