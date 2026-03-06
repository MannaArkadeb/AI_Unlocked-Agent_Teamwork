"""Feedback and learning module for adaptation."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import numpy as np

from src.models import FeedbackEvent, Plan, Task


class LearningEngine:
    """
    Online learning system that adapts based on user feedback.
    Updates user-specific weights and improves predictions over time.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # User-specific learned parameters
        self.user_params = {
            "scheduling_aggression": 0.5,  # 0=conservative, 1=aggressive
            "task_duration_multipliers": {},  # Task type -> multiplier
            "preferred_batch_size": 3,
            "risk_tolerance": 0.5,
            "learning_rate": 0.1
        }
        
        # Feedback history
        self.feedback_history: List[FeedbackEvent] = []
        
        # Statistics for monitoring
        self.stats = {
            "total_feedback_events": 0,
            "accept_rate": 0.0,
            "avg_task_completion_ratio": 1.0,
            "last_updated": datetime.now().isoformat()
        }
    
    def record_feedback(self, event: FeedbackEvent) -> None:
        """Record a feedback event."""
        self.feedback_history.append(event)
        self.stats["total_feedback_events"] += 1
        
        # Update statistics
        self._update_statistics()
        
        # Trigger incremental learning
        self._incremental_update(event)
    
    def record_plan_decision(
        self,
        plan: Plan,
        decision: str,
        modifications: Optional[Dict[str, Any]] = None
    ) -> FeedbackEvent:
        """
        Record user's decision on a plan (accept/reject/modify).
        
        Args:
            plan: The plan presented
            decision: "accept", "reject", or "modify"
            modifications: Details if modified
        
        Returns:
            Created FeedbackEvent
        """
        event = FeedbackEvent(
            event_type=decision,
            plan_id=plan.id,
            data={
                "confidence_score": plan.confidence_score,
                "num_tasks": len(plan.tasks),
                "modifications": modifications
            }
        )
        
        self.record_feedback(event)
        return event
    
    def record_task_completion(
        self,
        task: Task,
        actual_duration_hours: float,
        was_delayed: bool = False
    ) -> FeedbackEvent:
        """
        Record task completion metrics.
        
        Args:
            task: The completed task
            actual_duration_hours: Actual time taken
            was_delayed: Whether task was delayed beyond estimate
        
        Returns:
            Created FeedbackEvent
        """
        event = FeedbackEvent(
            event_type="complete",
            plan_id="",  # Would be linked to plan in full system
            task_id=task.id,
            data={
                "estimated_hours": task.effort_hours,
                "actual_hours": actual_duration_hours,
                "ratio": actual_duration_hours / task.effort_hours if task.effort_hours > 0 else 1.0,
                "delayed": was_delayed,
                "skills": task.skills_required
            }
        )
        
        self.record_feedback(event)
        return event
    
    def get_adjusted_estimate(
        self,
        base_estimate: float,
        task_type: str,
        skills: List[str]
    ) -> float:
        """
        Get adjusted effort estimate based on learned user patterns.
        
        Args:
            base_estimate: Base estimate in hours
            task_type: Type of task
            skills: Required skills
        
        Returns:
            Adjusted estimate
        """
        multiplier = self.user_params["task_duration_multipliers"].get(task_type, 1.0)
        
        # Adjust based on skill familiarity
        skill_adjustment = 1.0
        for skill in skills:
            if skill in self.user_params["task_duration_multipliers"]:
                skill_adjustment *= self.user_params["task_duration_multipliers"][skill]
        
        adjusted = base_estimate * multiplier * skill_adjustment
        
        # Apply scheduling aggression (more aggressive = tighter estimates)
        aggression = self.user_params["scheduling_aggression"]
        adjusted = adjusted * (1.0 - (aggression - 0.5) * 0.3)
        
        return max(0.5, adjusted)  # Minimum 0.5 hours
    
    def should_use_aggressive_scheduling(self) -> bool:
        """Determine if aggressive scheduling should be used."""
        return self.user_params["scheduling_aggression"] > 0.6
    
    def get_recommended_batch_size(self) -> int:
        """Get recommended number of concurrent tasks."""
        return self.user_params["preferred_batch_size"]
    
    def export_parameters(self) -> Dict[str, Any]:
        """Export learned parameters for persistence."""
        return {
            "user_id": self.user_id,
            "parameters": self.user_params,
            "statistics": self.stats,
            "num_feedback_events": len(self.feedback_history),
            "exported_at": datetime.now().isoformat()
        }
    
    def import_parameters(self, data: Dict[str, Any]) -> None:
        """Import previously learned parameters."""
        if data.get("user_id") != self.user_id:
            raise ValueError("User ID mismatch")
        
        self.user_params.update(data.get("parameters", {}))
        self.stats.update(data.get("statistics", {}))
    
    def _update_statistics(self) -> None:
        """Update aggregate statistics."""
        if not self.feedback_history:
            return
        
        # Compute accept rate
        decision_events = [
            e for e in self.feedback_history
            if e.event_type in ["accept", "reject", "modify"]
        ]
        if decision_events:
            accepts = sum(1 for e in decision_events if e.event_type == "accept")
            self.stats["accept_rate"] = accepts / len(decision_events)
        
        # Compute average task completion ratio
        completion_events = [
            e for e in self.feedback_history
            if e.event_type == "complete" and "ratio" in e.data
        ]
        if completion_events:
            ratios = [e.data["ratio"] for e in completion_events]
            self.stats["avg_task_completion_ratio"] = float(np.mean(ratios))
        
        self.stats["last_updated"] = datetime.now().isoformat()
    
    def _incremental_update(self, event: FeedbackEvent) -> None:
        """
        Perform incremental parameter update based on feedback.
        Implements online learning with exponential moving average.
        """
        lr = self.user_params["learning_rate"]
        
        if event.event_type == "reject":
            # User rejected plan - become more conservative
            current = self.user_params["scheduling_aggression"]
            self.user_params["scheduling_aggression"] = current * (1 - lr) + 0.3 * lr
        
        elif event.event_type == "accept":
            # User accepted - can be slightly more aggressive
            current = self.user_params["scheduling_aggression"]
            self.user_params["scheduling_aggression"] = current * (1 - lr) + 0.6 * lr
        
        elif event.event_type == "complete" and "ratio" in event.data:
            # Update task duration multipliers
            ratio = event.data["ratio"]
            skills = event.data.get("skills", [])
            
            for skill in skills:
                current = self.user_params["task_duration_multipliers"].get(skill, 1.0)
                # Update multiplier towards observed ratio
                updated = current * (1 - lr) + ratio * lr
                self.user_params["task_duration_multipliers"][skill] = updated
