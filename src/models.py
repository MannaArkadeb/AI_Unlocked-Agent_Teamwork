"""Core data models for the planning system."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field
from uuid import uuid4


class ConstraintType(str, Enum):
    """Types of constraints."""
    HARD = "hard"  # Must be satisfied
    SOFT = "soft"  # Optimization targets


class TaskStatus(str, Enum):
    """Task execution states."""
    PLANNED = "planned"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class ActionType(str, Enum):
    """Types of executable actions."""
    SOFT = "soft"  # No external effects (generate content, analyze)
    HARD = "hard"  # External effects (create calendar event, send email)


class Constraint(BaseModel):
    """Represents a planning constraint."""
    type: ConstraintType
    key: str
    value: Any
    priority: float = 1.0


class Task(BaseModel):
    """Represents a task in the HTN."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    effort_hours: float
    skills_required: List[str] = []
    earliest_start: Optional[datetime] = None
    latest_deadline: Optional[datetime] = None
    dependencies: List[str] = []  # Task IDs
    status: TaskStatus = TaskStatus.PLANNED
    metadata: Dict[str, Any] = {}


class Milestone(BaseModel):
    """Represents a milestone (collection of tasks)."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    tasks: List[str] = []  # Task IDs
    target_date: Optional[datetime] = None


class Plan(BaseModel):
    """Represents a complete plan."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    goal: str
    milestones: List[Milestone] = []
    tasks: List[Task] = []
    constraints: List[Constraint] = []
    critical_path: List[str] = []  # Task IDs
    confidence_score: float = 0.0
    expected_completion: Optional[datetime] = None
    contingency_branches: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.now)


class Evidence(BaseModel):
    """Evidence supporting a retrieval result."""
    source: str
    content: str
    relevance_score: float
    trust_score: float
    recency_score: float
    
    @property
    def evidence_score(self) -> float:
        """Compute combined evidence score."""
        return self.relevance_score * self.trust_score * self.recency_score


class Action(BaseModel):
    """Represents an executable action."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: ActionType
    task_id: str
    description: str
    preconditions: List[str] = []
    postconditions: List[str] = []
    parameters: Dict[str, Any] = {}
    dry_run_result: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None


class NegotiationDigest(BaseModel):
    """Summary for human-in-the-loop approval."""
    plan_id: str
    suggested_changes: List[Dict[str, Any]]
    alternatives: List[Dict[str, Any]]
    expected_risks: List[str]
    requires_approval: bool = True


class FeedbackEvent(BaseModel):
    """User feedback event for learning."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str  # accept, reject, edit, complete, delay
    plan_id: str
    task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = {}


class AuditEvent(BaseModel):
    """Immutable audit log entry."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str
    event_type: str
    entity_id: str  # Plan, task, or action ID
    action: str
    details: Dict[str, Any] = {}
    privacy_level: str = "private"  # private, shared, public
