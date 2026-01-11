"""
Base Tool Response
Consistent response format for all MCP tools.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-010)
"""

from pydantic import BaseModel
from typing import Optional, Any


class ToolResponse(BaseModel):
    """
    Standard response format for all MCP tools.

    Attributes:
        success: Whether the operation succeeded
        message: Human-readable result description
        data: Optional structured data (task details, lists, etc.)
    """
    success: bool
    message: str
    data: Optional[Any] = None
