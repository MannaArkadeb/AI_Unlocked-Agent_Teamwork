"""Main system orchestrator integrating all components."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models import Action, ActionType, Constraint, Plan
from src.input_capture import InputCapture
from src.knowledge_graph import KnowledgeGraph
from src.planner import Planner
from src.retriever import Retriever
from src.executor import ActionExecutor
from src.negotiation import Negotiator, ApprovalStatus
from src.learning import LearningEngine
from src.audit import AuditLogger


class PlanningSystem:
    """
    Main orchestrator for the intelligent planning and execution system.
    Coordinates all components to provide end-to-end functionality.
    """
    
    def __init__(self, user_id: str, log_dir: Optional[str] = None):
        self.user_id = user_id
        
        # Initialize all components
        self.input_capture = InputCapture()
        self.knowledge_graph = KnowledgeGraph(user_id)
        self.planner = Planner(self.knowledge_graph)
        self.retriever = Retriever(self.knowledge_graph)
        self.executor = ActionExecutor()
        self.negotiator = Negotiator()
        self.learning_engine = LearningEngine(user_id)
        self.audit_logger = AuditLogger(user_id, log_dir)
        
        # Active plans
        self.active_plans: Dict[str, Plan] = {}
        
        # Execution results
        self.execution_results: Dict[str, List[Dict[str, Any]]] = {}
        
        # Log system initialization
        self.audit_logger.log_event(
            event_type="system",
            entity_id=user_id,
            action="initialized",
            details={"components": [
                "input_capture", "knowledge_graph", "planner",
                "retriever", "executor", "negotiator", "learning", "audit"
            ]}
        )
    
    def process_goal(
        self,
        goal: str,
        hard_constraints: Optional[Dict[str, Any]] = None,
        soft_constraints: Optional[Dict[str, Any]] = None,
        external_tokens: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: process a user goal end-to-end.
        
        Args:
            goal: User's goal statement
            hard_constraints: Must-satisfy constraints
            soft_constraints: Optimization targets
            external_tokens: External documents/data
        
        Returns:
            Processing result with plan and next steps
        """
        # Stage 1: Input Capture
        captured_input = self.input_capture.parse_input(
            goal=goal,
            hard_constraints=hard_constraints,
            soft_constraints=soft_constraints,
            external_tokens=external_tokens
        )
        
        # Log input
        self.audit_logger.log_event(
            event_type="input",
            entity_id="goal_input",
            action="captured",
            details={
                "goal": captured_input["goal"],
                "num_constraints": len(captured_input["constraints"])
            }
        )
        
        # Update knowledge graph with new information
        self._update_kg_with_input(captured_input)
        
        # Stage 2: Planning
        plan = self.planner.create_plan(
            goal=captured_input["goal"],
            constraints=captured_input["constraints"]
        )
        
        # Log plan creation
        self.audit_logger.log_event(
            event_type="plan",
            entity_id=plan.id,
            action="created",
            details={
                "goal": plan.goal,
                "num_milestones": len(plan.milestones),
                "num_tasks": len(plan.tasks),
                "confidence": plan.confidence_score
            }
        )
        
        # Stage 3: Retrieval - gather resources for tasks
        task_resources = self.retriever.retrieve_for_tasks(plan.tasks, top_k=3)
        
        # Log retrieval
        self.audit_logger.log_event(
            event_type="retrieval",
            entity_id=plan.id,
            action="resources_retrieved",
            details={
                "num_tasks": len(plan.tasks),
                "total_resources": sum(len(resources) for resources in task_resources.values())
            }
        )
        
        # Stage 4: Create executable actions
        actions = self._create_actions_from_plan(plan)
        
        # Stage 5: Negotiation - prepare digest for approval
        digest = self.negotiator.prepare_digest(plan, actions)
        
        # Log negotiation initiation
        self.audit_logger.log_event(
            event_type="negotiation",
            entity_id=plan.id,
            action="digest_prepared",
            details={
                "num_changes": len(digest.suggested_changes),
                "num_alternatives": len(digest.alternatives),
                "num_risks": len(digest.expected_risks),
                "requires_approval": digest.requires_approval
            }
        )
        
        # Store active plan
        self.active_plans[plan.id] = plan
        
        return {
            "status": "awaiting_approval",
            "plan_id": plan.id,
            "plan": plan,
            "digest": digest,
            "task_resources": task_resources,
            "actions": actions
        }
    
    def approve_plan(
        self,
        plan_id: str,
        modifications: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Approve and execute a plan.
        
        Args:
            plan_id: ID of the plan to approve
            modifications: Optional modifications to apply
        
        Returns:
            Execution result
        """
        if plan_id not in self.active_plans:
            return {
                "status": "error",
                "error": "Plan not found"
            }
        
        plan = self.active_plans[plan_id]
        
        # Request approval through negotiator
        if plan_id in self.negotiator.pending_approvals:
            digest = self.negotiator.pending_approvals[plan_id]["digest"]
            approval_status = self.negotiator.request_approval(digest, prompt_user=True)
        else:
            approval_status = ApprovalStatus.APPROVED
        
        # Handle approval
        status = ApprovalStatus.MODIFIED if modifications else approval_status
        approval_result = self.negotiator.handle_approval(
            plan_id,
            status,
            modifications
        )
        
        # Record feedback
        decision = "modify" if modifications else "accept"
        self.learning_engine.record_plan_decision(plan, decision, modifications)
        
        # Log approval
        self.audit_logger.log_event(
            event_type="approval",
            entity_id=plan_id,
            action=decision,
            details={
                "status": status.value,
                "has_modifications": modifications is not None
            }
        )
        
        if approval_result.get("requires_replan"):
            # Re-plan with modifications
            return {
                "status": "requires_replan",
                "plan_id": plan_id,
                "modifications": modifications
            }
        
        # Execute plan
        execution_result = self._execute_plan(plan)
        
        return {
            "status": "approved_and_executed",
            "plan_id": plan_id,
            "execution_result": execution_result
        }
    
    def reject_plan(self, plan_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Reject a plan."""
        if plan_id not in self.active_plans:
            return {"status": "error", "error": "Plan not found"}
        
        plan = self.active_plans[plan_id]
        
        # Record feedback
        self.learning_engine.record_plan_decision(plan, "reject")
        
        # Log rejection
        self.audit_logger.log_event(
            event_type="approval",
            entity_id=plan_id,
            action="reject",
            details={"reason": reason}
        )
        
        # Handle through negotiator
        self.negotiator.handle_approval(plan_id, ApprovalStatus.REJECTED)
        
        # Remove from active plans
        del self.active_plans[plan_id]
        
        return {
            "status": "rejected",
            "plan_id": plan_id
        }
    
    def record_task_completion(
        self,
        task_id: str,
        actual_duration_hours: float
    ) -> Dict[str, Any]:
        """Record completion of a task for learning."""
        # Find task in active plans
        task = None
        for plan in self.active_plans.values():
            for t in plan.tasks:
                if t.id == task_id:
                    task = t
                    break
        
        if not task:
            return {"status": "error", "error": "Task not found"}
        
        # Record feedback
        was_delayed = actual_duration_hours > task.effort_hours * 1.2
        self.learning_engine.record_task_completion(
            task,
            actual_duration_hours,
            was_delayed
        )
        
        # Log completion
        self.audit_logger.log_event(
            event_type="task",
            entity_id=task_id,
            action="completed",
            details={
                "estimated_hours": task.effort_hours,
                "actual_hours": actual_duration_hours,
                "delayed": was_delayed
            }
        )
        
        return {
            "status": "recorded",
            "task_id": task_id,
            "learned_ratio": actual_duration_hours / task.effort_hours
        }
    
    def get_audit_trail(
        self,
        plan_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get audit trail for a plan or entire system."""
        return self.audit_logger.export_audit_trail(
            entity_id=plan_id,
            include_private=True
        )
    
    def verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify integrity of audit chain."""
        return self.audit_logger.verify_chain_integrity()
    
    def _update_kg_with_input(self, captured_input: Dict[str, Any]) -> None:
        """Update knowledge graph with captured input."""
        # Add constraints to KG
        for constraint in captured_input["constraints"]:
            self.knowledge_graph.add_entity(
                entity_id=f"constraint_{constraint.key}",
                entity_type="constraint",
                properties={
                    "type": constraint.type.value,
                    "key": constraint.key,
                    "value": constraint.value,
                    "priority": constraint.priority
                }
            )
        
        # Add external tokens to KG
        for token in captured_input.get("external_tokens", []):
            self.knowledge_graph.add_entity(
                entity_id=f"token_{token.get('type', 'unknown')}",
                entity_type="resource",
                properties=token
            )
    
    def _create_actions_from_plan(self, plan: Plan) -> List[Action]:
        """Create executable actions from plan tasks."""
        actions = []
        
        for task in plan.tasks:
            # Determine if this is a soft or hard action
            # Hard actions: create calendar events, send notifications, etc.
            # Soft actions: generate study materials, create templates, etc.
            
            if any(keyword in task.name.lower() for keyword in ["exam", "deadline", "meeting"]):
                action_type = ActionType.HARD
                preconditions = ["calendar_slot_available", "no_conflicts"]
                postconditions = ["event_created", "confirmation_received"]
            else:
                action_type = ActionType.SOFT
                preconditions = []
                postconditions = []
            
            action = Action(
                type=action_type,
                task_id=task.id,
                description=f"execute_{task.name.lower().replace(' ', '_')}",
                preconditions=preconditions,
                postconditions=postconditions,
                parameters={
                    "task_name": task.name,
                    "effort_hours": task.effort_hours,
                    "earliest_start": task.earliest_start.isoformat() if task.earliest_start else None,
                    "latest_deadline": task.latest_deadline.isoformat() if task.latest_deadline else None
                }
            )
            
            actions.append(action)
        
        return actions
    
    def _execute_plan(self, plan: Plan) -> Dict[str, Any]:
        """Execute all actions in a plan."""
        results = []
        
        actions = self._create_actions_from_plan(plan)
        
        for action in actions:
            # Soft actions: execute immediately
            # Hard actions: execute with full verification
            dry_run = action.type == ActionType.HARD
            
            result = self.executor.execute_action(action, dry_run=dry_run)
            results.append(result)
            
            # Log execution
            self.audit_logger.log_event(
                event_type="execution",
                entity_id=action.id,
                action="executed",
                details={
                    "task_id": action.task_id,
                    "action_type": action.type.value,
                    "status": result["status"],
                    "dry_run": dry_run
                }
            )
            
            # If dry run succeeded, execute for real
            if dry_run and result["status"] == "success":
                real_result = self.executor.execute_action(action, dry_run=False)
                results.append(real_result)
                
                # Log real execution
                self.audit_logger.log_event(
                    event_type="execution",
                    entity_id=action.id,
                    action="executed_real",
                    details={
                        "task_id": action.task_id,
                        "status": real_result["status"]
                    }
                )
        
        # Store execution results
        self.execution_results[plan.id] = results
        
        return {
            "plan_id": plan.id,
            "total_actions": len(actions),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results
        }
