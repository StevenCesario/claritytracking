from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

# =============================================================================
# SECURITY & AUTH SCHEMAS
# =============================================================================

class TokenResponse(BaseModel):
    """The shape of the response when a user successfully logs in."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """The data we embed inside the JWT payload."""
    user_id: Optional[int] = None

# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    # The name is now optional. If the frontend doesn't send it,
    # our CRUD function will handle the default.
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    """Schema for returning user data (without the password)."""
    id: int
    name: str
    email: EmailStr
    registered_at: datetime

    class Config:
        from_attributes = True

# =============================================================================
# WEBSITE & CONNECTION SCHEMAS
# =============================================================================

class ConnectionBase(BaseModel):
    """Base schema for creating a platform connection."""
    platform: str # e.g., "meta", "shopify"
    platform_identifiers: Dict[str, Any] # e.g., {"pixel_id": "12345"}

class ConnectionCreate(ConnectionBase):
    pass

class ConnectionResponse(ConnectionBase):
    """Schema for returning connection details."""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class WebsiteBase(BaseModel):
    """Base schema for creating a website."""
    url: str
    name: str

class WebsiteCreate(WebsiteBase):
    pass

class WebsiteResponse(WebsiteBase):
    """Schema for returning website details, including its connections."""
    id: int
    user_id: int
    created_at: datetime
    connections: list[ConnectionResponse] = []

    class Config:
        from_attributes = True

# =============================================================================
# DASHBOARD & EVENT SCHEMAS
# =============================================================================

class EventHealth(BaseModel):
    """Represents the health status of a specific event type."""
    event_name: str
    emq_score: float
    last_received: datetime
    status: str # e.g., "healthy", "warning", "error"

# NEW: Schema for the Health Monitor alerts
class EventAlert(BaseModel):
    """Represents a specific health alert for the dashboard."""
    id: str
    severity: str # "error" or "warning"
    title: str
    message: str
    timestamp: datetime

class DashboardResponse(BaseModel):
    """The single source of truth for the frontend dashboard."""
    total_conversions_recovered: int
    overall_roas: float
    campaign_performance: list[Dict[str, Any]] # A list of campaign objects
    event_health_monitor: list[EventHealth]

# =============================================================================
# WAITLIST SCHEMAS
# =============================================================================

class WaitlistCreate(BaseModel):
    """Schema for adding a new email to the Beta waitlist."""
    # Use Field alias to accept "Email" from Framer's webhook
    email: EmailStr = Field(..., alias='Email')
    source: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    referer: Optional[str] = None

class WaitlistResponse(BaseModel):
    """The shape of the response after a successful waitlist signup."""
    id: int
    email: EmailStr # Keep this as 'email' for the response
    created_at: datetime

    class Config:
        from_attributes = True
