"""Negotiation module for human-in-the-loop approval."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from src.models import Action, ActionType, NegotiationDigest, Plan


class ApprovalStatus(str, Enum):
    """Status of approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class Negotiator:
    """
    Handles human-in-the-loop negotiation for plan approval.
    Presents compact digests and manages approval workflow.
    """
    
    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approval_history: List[Dict[str, Any]] = []
    
    def prepare_digest(
        self,
        plan: Plan,
        actions: List[Action]
    ) -> NegotiationDigest:
        """
        Prepare a compact negotiation digest for user review.
        
        Args:
            plan: The plan to present
            actions: Actions that would be executed
        
        Returns:
            NegotiationDigest for user review
        """
        # Identify hard actions requiring explicit approval
        hard_actions = [a for a in actions if a.type == ActionType.HARD]
        
        # Prepare suggested changes summary
        suggested_changes = []
        for action in hard_actions:
            suggested_changes.append({
                "action": action.description,
                "params": action.parameters,
                "impact": self._assess_impact(action)
            })
        
        # Generate alternatives
        alternatives = self._generate_alternatives(plan, hard_actions)
        
        # Assess risks
        risks = self._assess_risks(plan, actions)
        
        # Create digest
        digest = NegotiationDigest(
            plan_id=plan.id,
            suggested_changes=suggested_changes,
            alternatives=alternatives,
            expected_risks=risks,
            requires_approval=len(hard_actions) > 0
        )
        
        # Store as pending
        self.pending_approvals[plan.id] = {
            "digest": digest,
            "plan": plan,
            "actions": actions,
            "status": ApprovalStatus.PENDING,
            "created_at": datetime.now().isoformat()
        }
        
        return digest
    
    def request_approval(
        self,
        digest: NegotiationDigest,
        prompt_user: bool = True
    ) -> ApprovalStatus:
        """
        Request approval from user.
        
        Args:
            digest: The negotiation digest
            prompt_user: If True, would prompt user (simulated in prototype)
        
        Returns:
            Approval status
        """
        if not digest.requires_approval:
            return ApprovalStatus.APPROVED
        
        # In production: prompt user through UI/CLI
        # For prototype: auto-approve with logging
        
        if prompt_user:
            print(f"\n{'='*60}")
            print("APPROVAL REQUIRED")
            print(f"{'='*60}")
            print(f"Plan ID: {digest.plan_id}")
            print(f"\nSuggested Changes ({len(digest.suggested_changes)}):")
            for i, change in enumerate(digest.suggested_changes, 1):
                print(f"  {i}. {change['action']}")
                print(f"     Impact: {change['impact']}")
            
            if digest.alternatives:
                print(f"\nAlternatives ({len(digest.alternatives)}):")
                for i, alt in enumerate(digest.alternatives, 1):
                    print(f"  {i}. {alt['description']}")
            
            if digest.expected_risks:
                print(f"\nExpected Risks ({len(digest.expected_risks)}):")
                for i, risk in enumerate(digest.expected_risks, 1):
                    print(f"  {i}. {risk}")
            
            print(f"\n{'='*60}\n")
        
        # Simulated approval for prototype
        return ApprovalStatus.APPROVED
    
    def handle_approval(
        self,
        plan_id: str,
        status: ApprovalStatus,
        modifications: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle user's approval decision.
        
        Args:
            plan_id: ID of the plan
            status: Approval status
            modifications: Optional modifications if status is MODIFIED
        
        Returns:
            Result of approval handling
        """
        if plan_id not in self.pending_approvals:
            return {
                "success": False,
                "error": "Plan not found in pending approvals"
            }
        
        approval_record = self.pending_approvals[plan_id]
        approval_record["status"] = status
        approval_record["resolved_at"] = datetime.now().isoformat()
        
        if status == ApprovalStatus.MODIFIED and modifications:
            approval_record["modifications"] = modifications
        
        # Move to history
        self.approval_history.append(approval_record)
        del self.pending_approvals[plan_id]
        
        result = {
            "success": True,
            "plan_id": plan_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        # If modified, trigger re-planning
        if status == ApprovalStatus.MODIFIED:
            result["requires_replan"] = True
            result["modifications"] = modifications
        
        return result
    
    def _assess_impact(self, action: Action) -> str:
        """Assess the impact of an action."""
        if action.type == ActionType.HARD:
            return "High - Creates external commitment"
        else:
            return "Low - Internal planning only"
    
    def _generate_alternatives(
        self,
        plan: Plan,
        hard_actions: List[Action]
    ) -> List[Dict[str, Any]]:
        """Generate alternative approaches."""
        alternatives = []
        
        # Alternative: More conservative timeline
        if plan.expected_completion:
            alternatives.append({
                "description": "Extended timeline with 20% buffer",
                "impact": "Lower risk, later completion",
                "confidence_delta": "+0.15"
            })
        
        # Alternative: Reduced scope
        if len(plan.tasks) > 3:
            alternatives.append({
                "description": f"Focus on top {len(plan.tasks)//2} priority tasks",
                "impact": "Reduced scope, higher success rate",
                "confidence_delta": "+0.10"
            })
        
        # Alternative: Different scheduling
        alternatives.append({
            "description": "Batch similar tasks together",
            "impact": "Better focus, potential efficiency gains",
            "confidence_delta": "+0.05"
        })
        
        return alternatives
    
    def _assess_risks(
        self,
        plan: Plan,
        actions: List[Action]
    ) -> List[str]:
        """Assess potential risks in the plan."""
        risks = []
        
        # Low confidence risk
        if plan.confidence_score < 0.7:
            risks.append(
                f"Low confidence score ({plan.confidence_score:.2f}) - "
                "Plan may require adjustments"
            )
        
        # Tight timeline risk
        if plan.contingency_branches:
            risks.append(
                f"{len(plan.contingency_branches)} contingency scenarios identified - "
                "Timeline may slip"
            )
        
        # Hard action risks
        hard_actions = [a for a in actions if a.type == ActionType.HARD]
        if hard_actions:
            risks.append(
                f"{len(hard_actions)} hard actions will create external commitments - "
                "Changes may be difficult after execution"
            )
        
        return risks
