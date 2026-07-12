from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── HCP Schemas ──────────────────────────────────────────────────────────────

class HCPBase(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    institution: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    npi_number: Optional[str] = None
    territory: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    tier: Optional[str] = "B"


class HCPCreate(HCPBase):
    pass


class HCPUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialty: Optional[str] = None
    institution: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    territory: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    tier: Optional[str] = None


class HCPResponse(HCPBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    interaction_count: Optional[int] = 0

    class Config:
        from_attributes = True


# ── Product Schemas ──────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    key_messages: Optional[str] = None
    therapeutic_area: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Interaction Schemas ──────────────────────────────────────────────────────

class InteractionBase(BaseModel):
    hcp_id: int
    rep_name: Optional[str] = "Field Rep"
    interaction_type: str
    channel: Optional[str] = None
    interaction_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    raw_notes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    status: Optional[str] = "completed"
    product_ids: Optional[List[int]] = []


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    hcp_id: Optional[int] = None
    rep_name: Optional[str] = None
    interaction_type: Optional[str] = None
    channel: Optional[str] = None
    interaction_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    raw_notes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    status: Optional[str] = None
    product_ids: Optional[List[int]] = None


class InteractionResponse(BaseModel):
    id: int
    hcp_id: int
    rep_name: Optional[str] = None
    interaction_type: str
    channel: Optional[str] = None
    interaction_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    raw_notes: Optional[str] = None
    ai_summary: Optional[str] = None
    sentiment: Optional[str] = None
    key_topics: Optional[str] = None
    follow_up_actions: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    hcp_name: Optional[str] = None
    products: Optional[List[ProductResponse]] = []

    class Config:
        from_attributes = True


# ── Chat / Agent Schemas ─────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class WorkflowStep(BaseModel):
    """Represents a step in the LangGraph agent workflow pipeline."""
    step_name: str
    status: str = "completed"  # completed, in_progress, pending
    description: Optional[str] = None
    tool_name: Optional[str] = None


class ToolExecution(BaseModel):
    tool_name: str
    tool_input: Optional[dict] = None
    tool_output: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    tool_executions: Optional[List[ToolExecution]] = []
    workflow_steps: Optional[List[WorkflowStep]] = []
    extracted_data: Optional[dict] = None


# ── Dashboard Stats Schema ───────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_hcps: int = 0
    total_interactions: int = 0
    positive_sentiment_rate: int = 0
    pending_followups: int = 0
    most_discussed_product: Optional[str] = None
    highest_priority_hcp: Optional[str] = None
    negative_sentiment_hcp: Optional[str] = None
    doctors_needing_followup: int = 0
    most_successful_product: Optional[str] = None
    recent_ai_activity: Optional[List[dict]] = []
    interactions_this_week: int = 0
    sentiment_trend: Optional[str] = None  # "up", "down", "stable"


# ── HCP Insights Schema ─────────────────────────────────────────────────────

class HCPInsights(BaseModel):
    hcp_id: int
    hcp_name: str
    interested_products: Optional[List[str]] = []
    communication_style: Optional[str] = None
    last_meeting_summary: Optional[str] = None
    preferred_meeting_type: Optional[str] = None
    conversion_probability: Optional[int] = 0  # 0-100
    recommended_product: Optional[str] = None
    recommended_product_reason: Optional[str] = None
    pending_actions: Optional[List[str]] = []
    total_interactions: int = 0
    avg_sentiment: Optional[str] = None
