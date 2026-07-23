from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str # JSON string

class Message(BaseModel):
    id: Optional[str] = None
    role: Role
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    citations: Optional[List[Dict[str, Any]]] = None

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    agent_type: str = "recruiter_copilot"
    message: str
    context_data: Optional[Dict[str, Any]] = None # Active page context (e.g. candidate_id)

class ChatResponse(BaseModel):
    conversation_id: str
    message: Message
    trace_id: Optional[str] = None

class ConversationSchema(BaseModel):
    id: str
    organization_id: str
    user_id: str
    title: Optional[str] = None
    agent_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    conversation_id: str
    message_id: str
    rating: float # 1.0 or -1.0
    comment: Optional[str] = None
    corrected_output: Optional[str] = None

class TraceResponse(BaseModel):
    id: str
    organization_id: str
    message_id: Optional[str] = None
    provider: str
    model: str
    latency_ms: float
    total_tokens: float
    cost_usd: float
    success: bool
    created_at: datetime
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

# Tool Schemas definition (OpenAI format)
class ToolSchemaProperty(BaseModel):
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None

class ToolSchemaParameters(BaseModel):
    type: str = "object"
    properties: Dict[str, ToolSchemaProperty]
    required: Optional[List[str]] = None

class ToolSchemaFunction(BaseModel):
    name: str
    description: str
    parameters: ToolSchemaParameters

class ToolSchema(BaseModel):
    type: str = "function"
    function: ToolSchemaFunction
