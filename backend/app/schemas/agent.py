from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime


class AgentBase(BaseModel):
    """Base agent schema"""
    name: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    external_id: Optional[str] = None


class AgentCreate(AgentBase):
    """Schema for creating agents"""
    organization_id: int
    billing_model_id: Optional[int] = None


class AgentUpdate(BaseModel):
    """Schema for updating agents"""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    billing_model_id: Optional[int] = None


class AgentInDBBase(AgentBase):
    """Base schema for agents in DB"""
    id: int
    organization_id: int
    billing_model_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class Agent(AgentInDBBase):
    """Schema for agent responses"""
    pass


class AgentWithStats(Agent):
    """Agent schema with usage statistics"""
    activity_count: int
    total_cost: float
    total_outcomes_value: float
    margin: float  # Calculated as (total_outcomes_value - total_cost) / total_outcomes_value


class AgentActivityBase(BaseModel):
    """Base agent activity schema"""
    activity_type: str
    activity_metadata: Optional[Dict[str, Any]] = None


class AgentActivityCreate(AgentActivityBase):
    """Schema for creating agent activities"""
    agent_id: int


class AgentActivityInDB(AgentActivityBase):
    """Schema for agent activities in DB"""
    id: int
    agent_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class AgentActivity(AgentActivityInDB):
    """Schema for agent activity responses"""
    pass


class AgentCostBase(BaseModel):
    """Base agent cost schema"""
    cost_type: str
    amount: float
    currency: str = "USD"
    details: Optional[Dict[str, Any]] = None


class AgentCostCreate(AgentCostBase):
    """Schema for creating agent costs"""
    agent_id: int


class AgentCostInDB(AgentCostBase):
    """Schema for agent costs in DB"""
    id: int
    agent_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class AgentCost(AgentCostInDB):
    """Schema for agent cost responses"""
    pass


class AgentOutcomeBase(BaseModel):
    """Base agent outcome schema"""
    outcome_type: str
    value: float
    currency: str = "USD"
    details: Optional[Dict[str, Any]] = None
    verified: bool = False


class AgentOutcomeCreate(AgentOutcomeBase):
    """Schema for creating agent outcomes"""
    agent_id: int


class AgentOutcomeInDB(AgentOutcomeBase):
    """Schema for agent outcomes in DB"""
    id: int
    agent_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class AgentOutcome(AgentOutcomeInDB):
    """Schema for agent outcome responses"""
    pass