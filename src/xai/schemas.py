"""
Explainable AI (XAI) Structure Schemas
Defines structured telemetry feedback models for system safety and web UI consumption.
"""

from pydantic import BaseModel, Field
from typing import Optional

class XAIRiskReport(BaseModel):
    """Structured telemetry data outlining the safety audit details of a tool call."""
    confidence_score: float = Field(
        ..., 
        description="Confidence alignment indicator metrics (0.0 to 1.0) mapping user intent to arguments."
    )
    risk_level: str = Field(
        ..., 
        description="The calculated risk classification weight. MUST be exactly one of: 'LOW', 'MEDIUM', or 'HIGH'."
    )
    action_classification: str = Field(
        ..., 
        description="The category of action. MUST be: 'ACCESS' (Read-only data pull) or 'MUTATION' (Destructive write/delete/send)."
    )
    reasoning: str = Field(
        ..., 
        description="Detailed plain-language explanation breaking down why the agent configured this tool execution sequence."
    )
    potential_impact: str = Field(
        ..., 
        description="Explicit system warning outlining what will happen if this operation runs (e.g., 'Will append an entry on your live calendar timeline')."
    )
    alternative_suggestions: Optional[str] = Field(
        None, 
        description="Proactive adjustments or parameter corrections if an anomaly or divergence is caught by the guard."
    )