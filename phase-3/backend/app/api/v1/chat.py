"""
Chat API Router
Endpoints for AI chatbot interaction.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-019 to FR-026)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone
from typing import Dict, List
import time
import traceback

from app.db.session import get_session
from app.auth.dependencies import get_current_user_id
from app.models.conversation import Conversation
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    ConversationListResponse
)
from app.agents.task_agent import TaskAgent
from app.config import settings

router = APIRouter()

# -----------------------------
# Simple in-memory rate limiter
# -----------------------------
_rate_limit_cache: Dict[int, List[float]] = {}

def _check_rate_limit(user_id: int) -> bool:
    """
    Check if user has exceeded rate limit.
    Returns True if allowed, False if rate limited.
    """
    now = time.time()
    rate_limit = settings.CHAT_RATE_LIMIT or 10

    if user_id not in _rate_limit_cache:
        _rate_limit_cache[user_id] = []

    # Remove timestamps older than 60 seconds
    _rate_limit_cache[user_id] = [
        t for t in _rate_limit_cache[user_id] if now - t < 60
    ]

    if len(_rate_limit_cache[user_id]) >= rate_limit:
        return False

    _rate_limit_cache[user_id].append(now)
    return True


# -----------------------------
# Chat Endpoint
# -----------------------------
@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Process a chat message and return AI response.
    """
    user_id = current_user_id

    # Rate limit
    if not _check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {settings.CHAT_RATE_LIMIT or 10} messages per minute."
        )

    # Get or create conversation
    conversation = None
    if request.conversation_id:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

    if not conversation:
        conversation = Conversation(
            user_id=user_id,
            messages=[]
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Build conversation history
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in (conversation.messages or [])
    ]

    # Call AI agent
    agent = TaskAgent()
    try:
        response_text = agent.chat(
            session=session,
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_history
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

    # Append new messages
    now = datetime.now(timezone.utc).isoformat()
    conversation.messages = list(conversation.messages or []) + [
        {"role": "user", "content": request.message, "timestamp": now},
        {"role": "assistant", "content": response_text, "timestamp": now}
    ]
    conversation.updated_at = datetime.now(timezone.utc)

    session.add(conversation)
    session.commit()

    return ChatResponse(
        response=response_text,
        conversation_id=str(conversation.id)
    )


# -----------------------------
# List Conversations
# -----------------------------
@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    List all conversations for the authenticated user.
    """
    user_id = current_user_id

    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    summaries = []
    for conv in conversations:
        preview = "New conversation"
        if conv.messages:
            for msg in conv.messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "")
                    preview = content[:50] + "..." if len(content) > 50 else content
                    break

        summaries.append(ConversationSummary(
            id=str(conv.id),
            preview=preview,
            created_at=conv.created_at
        ))

    return ConversationListResponse(conversations=summaries)


# -----------------------------
# Get Single Conversation
# -----------------------------
@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific conversation.
    """
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user_id
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return {
        "id": str(conversation.id),
        "messages": conversation.messages,
        "created_at": conversation.created_at
    }


# -----------------------------
# Delete Conversation
# -----------------------------
@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete a conversation for the authenticated user.
    """
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user_id
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    session.delete(conversation)
    session.commit()
    return None
"""
Chat API Router
Endpoints for AI chatbot interaction.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-019 to FR-026)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, UTC
from typing import Dict, List
import time
import traceback

from app.db.session import get_session
from app.auth.dependencies import get_current_user_id
from app.models.conversation import Conversation
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    ConversationListResponse
)
from app.agents.task_agent import TaskAgent
from app.config import settings


router = APIRouter()

# Simple in-memory rate limiter
# For production, use Redis or similar
_rate_limit_cache: Dict[str, List[float]] = {}


def _check_rate_limit(user_id: int) -> bool:
    """
    Check if user has exceeded rate limit.

    Returns True if allowed, False if rate limited.
    """
    now = time.time()
    key = f"chat:{user_id}"
    rate_limit = settings.CHAT_RATE_LIMIT or 10

    if key not in _rate_limit_cache:
        _rate_limit_cache[key] = []

    # Remove entries older than 60 seconds
    _rate_limit_cache[key] = [
        t for t in _rate_limit_cache[key]
        if now - t < 60
    ]

    if len(_rate_limit_cache[key]) >= rate_limit:
        return False

    _rate_limit_cache[key].append(now)
    return True


@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Process a chat message and return AI response.

    - User ID comes from JWT authentication
    - Applies rate limiting
    - Manages conversation state
    - Calls AI agent for response
    """
    print("\n" + "="*50)
    print(f"🔵 CHAT ENDPOINT HIT")
    print(f"🔵 User ID: {current_user_id}")
    print(f"🔵 Message: {request.message[:50]}...")
    print(f"🔵 Conversation ID: {request.conversation_id}")
    print("="*50 + "\n")
    
    user_id = current_user_id

    # Check rate limit
    print("🔵 Checking rate limit...")
    if not _check_rate_limit(user_id):
        print("❌ Rate limit exceeded")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 messages per minute."
        )
    print("✅ Rate limit OK")

    # Get or create conversation
    print("🔵 Getting/creating conversation...")
    conversation = None
    if request.conversation_id:
        print(f"🔵 Looking for existing conversation: {request.conversation_id}")
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

    if not conversation:
        print("🔵 Creating new conversation...")
        try:
            conversation = Conversation(
                user_id=user_id,
                messages=[]
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            print(f"✅ Conversation created: {conversation.id}")
        except Exception as e:
            print(f"❌ Failed to create conversation: {e}")
            traceback.print_exc()
            raise
    else:
        print(f"✅ Using existing conversation: {conversation.id}")

    # Build conversation history for context
    print("🔵 Building conversation history...")
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in (conversation.messages or [])
    ]
    print(f"✅ History has {len(conversation_history)} messages")

    # Process message with AI agent
    print("🔵 Calling AI agent...")
    print(f"🔵 Creating TaskAgent instance...")
    agent = TaskAgent()
    print("✅ TaskAgent created")
    
    try:
        print("🔵 Calling agent.chat()...")
        response_text = agent.chat(
            session=session,
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_history
        )
        print(f"✅ AI Response received: {response_text[:100]}...")
    except Exception as e:
        print(f"❌ AI agent error: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

    # Update conversation with new messages
    print("🔵 Updating conversation with new messages...")
    now = datetime.now(UTC).isoformat()

    new_messages = list(conversation.messages or [])
    new_messages.append({
        "role": "user",
        "content": request.message,
        "timestamp": now
    })
    new_messages.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": now
    })

    conversation.messages = new_messages
    conversation.updated_at = datetime.now(UTC)

    try:
        session.add(conversation)
        session.commit()
        print("✅ Conversation updated in database")
    except Exception as e:
        print(f"❌ Failed to update conversation: {e}")
        traceback.print_exc()
        raise

    print(f"✅ Returning response")
    print("="*50 + "\n")
    
    # ✅ FIX: Convert UUID to string
    return ChatResponse(
        response=response_text,
        conversation_id=str(conversation.id)  # Convert UUID to string
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """List all conversations for the authenticated user."""
    print(f"\n🔵 LIST CONVERSATIONS - User ID: {current_user_id}")
    user_id = current_user_id

    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    print(f"✅ Found {len(conversations)} conversations")

    summaries = []
    for conv in conversations:
        preview = "New conversation"
        if conv.messages:
            for msg in conv.messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "")
                    preview = content[:50] + "..." if len(content) > 50 else content
                    break

        summaries.append(ConversationSummary(
            id=str(conv.id),  # ✅ FIX: Convert UUID to string
            preview=preview,
            created_at=conv.created_at
        ))

    return ConversationListResponse(conversations=summaries)


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Get a specific conversation with all messages for the authenticated user."""
    print(f"\n🔵 GET CONVERSATION - ID: {conversation_id}, User: {current_user_id}")
    user_id = current_user_id

    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conversation:
        print(f"❌ Conversation not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    print(f"✅ Conversation found with {len(conversation.messages or [])} messages")
    return {
        "id": str(conversation.id),  # ✅ FIX: Convert UUID to string
        "messages": conversation.messages,
        "created_at": conversation.created_at
    }


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Delete a conversation for the authenticated user."""
    print(f"\n🔵 DELETE CONVERSATION - ID: {conversation_id}, User: {current_user_id}")
    user_id = current_user_id

    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conversation:
        print(f"❌ Conversation not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    session.delete(conversation)
    session.commit()
    print(f"✅ Conversation deleted")

    return None
