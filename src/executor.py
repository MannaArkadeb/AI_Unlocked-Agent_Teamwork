"""Verifiable action executor with pre/postcondition checking."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import json

from src.models import Action, ActionType, Task


class VerificationStatus(str, Enum):
    """Status of verification checks."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class VerificationResult(Enum):
    """Result of a verification check."""
    def __init__(self, status: VerificationStatus, message: str, details: Optional[Dict] = None):
        self.status = status
        self.message = message
        self.details = details or {}


class ActionExecutor:
    """
    Verifiable action engine that distinguishes soft/hard actions.
    Enforces preconditions and postconditions with formal checks.
    """
    
    def __init__(self):
        # Registry of action handlers
        self.handlers: Dict[str, Callable] = {}
        
        # Registry of verification functions
        self.precondition_checks: Dict[str, List[Callable]] = {}
        self.postcondition_checks: Dict[str, List[Callable]] = {}
        
        # Transaction log for rollback
        self.transaction_log: List[Dict[str, Any]] = []
        
        # Register default handlers
        self._register_default_handlers()
    
    def register_action_handler(
        self,
        action_name: str,
        handler: Callable,
        preconditions: Optional[List[Callable]] = None,
        postconditions: Optional[List[Callable]] = None
    ) -> None:
        """Register a handler for a specific action type."""
        self.handlers[action_name] = handler
        
        if preconditions:
            self.precondition_checks[action_name] = preconditions
        
        if postconditions:
            self.postcondition_checks[action_name] = postconditions
    
    def execute_action(
        self,
        action: Action,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute an action with full verification.
        
        Args:
            action: The action to execute
            dry_run: If True, only simulate execution
        
        Returns:
            Execution result with status and details
        """
        result = {
            "action_id": action.id,
            "status": "pending",
            "dry_run": dry_run,
            "timestamp": datetime.now().isoformat(),
            "verifications": {}
        }
        
        try:
            # For hard actions, always perform dry run first
            if action.type == ActionType.HARD and not dry_run:
                # First do a dry run
                dry_result = self.execute_action(action, dry_run=True)
                if dry_result["status"] != "success":
                    result["status"] = "failed"
                    result["error"] = "Dry run failed"
                    result["dry_run_result"] = dry_result
                    return result
                
                action.dry_run_result = dry_result
            
            # Step 1: Verify preconditions
            precond_result = self._verify_preconditions(action)
            result["verifications"]["preconditions"] = precond_result
            
            if precond_result["status"] != VerificationStatus.PASSED:
                result["status"] = "failed"
                result["error"] = "Preconditions not satisfied"
                return result
            
            # Step 2: Execute action
            if not dry_run:
                exec_result = self._execute(action)
                result["execution"] = exec_result
                action.execution_result = exec_result
                
                # Log transaction for potential rollback
                self._log_transaction(action, exec_result)
            else:
                # Dry run: simulate execution
                exec_result = self._simulate_execution(action)
                result["execution"] = exec_result
            
            # Step 3: Verify postconditions
            if not dry_run:
                postcond_result = self._verify_postconditions(action)
                result["verifications"]["postconditions"] = postcond_result
                
                if postcond_result["status"] != VerificationStatus.PASSED:
                    result["status"] = "failed"
                    result["error"] = "Postconditions not satisfied"
                    
                    # Trigger remediation
                    remediation = self._remediate(action, postcond_result)
                    result["remediation"] = remediation
                    return result
            
            result["status"] = "success"
            return result
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            return result
    
    def _verify_preconditions(self, action: Action) -> Dict[str, Any]:
        """Verify all preconditions for an action."""
        result = {
            "status": VerificationStatus.PASSED,
            "checks": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Get registered precondition checks
        checks = self.precondition_checks.get(action.description, [])
        
        # Also check action-specific preconditions
        for precondition in action.preconditions:
            check_result = self._evaluate_condition(precondition, action)
            result["checks"].append(check_result)
            
            if not check_result["passed"]:
                result["status"] = VerificationStatus.FAILED
        
        # Run registered checks
        for check_fn in checks:
            try:
                passed = check_fn(action)
                result["checks"].append({
                    "name": check_fn.__name__,
                    "passed": passed
                })
                if not passed:
                    result["status"] = VerificationStatus.FAILED
            except Exception as e:
                result["checks"].append({
                    "name": check_fn.__name__,
                    "passed": False,
                    "error": str(e)
                })
                result["status"] = VerificationStatus.FAILED
        
        return result
    
    def _verify_postconditions(self, action: Action) -> Dict[str, Any]:
        """Verify all postconditions after action execution."""
        result = {
            "status": VerificationStatus.PASSED,
            "checks": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Get registered postcondition checks
        checks = self.postcondition_checks.get(action.description, [])
        
        # Check action-specific postconditions
        for postcondition in action.postconditions:
            check_result = self._evaluate_condition(postcondition, action)
            result["checks"].append(check_result)
            
            if not check_result["passed"]:
                result["status"] = VerificationStatus.FAILED
        
        # Run registered checks
        for check_fn in checks:
            try:
                passed = check_fn(action)
                result["checks"].append({
                    "name": check_fn.__name__,
                    "passed": passed
                })
                if not passed:
                    result["status"] = VerificationStatus.FAILED
            except Exception as e:
                result["checks"].append({
                    "name": check_fn.__name__,
                    "passed": False,
                    "error": str(e)
                })
                result["status"] = VerificationStatus.FAILED
        
        return result
    
    def _evaluate_condition(
        self,
        condition: str,
        action: Action
    ) -> Dict[str, Any]:
        """Evaluate a condition string against action state."""
        # Simplified condition evaluation for prototype
        # In production: use proper expression evaluator
        
        result = {
            "condition": condition,
            "passed": True,
            "details": {}
        }
        
        # Example condition: "calendar_slot_available"
        if "available" in condition:
            # Simulate check
            result["passed"] = True
        elif "exists" in condition:
            result["passed"] = action.execution_result is not None
        else:
            result["passed"] = True  # Default pass for prototype
        
        return result
    
    def _execute(self, action: Action) -> Dict[str, Any]:
        """Execute the actual action."""
        # Look up handler
        handler = self.handlers.get(action.description)
        
        if handler:
            return handler(action)
        else:
            # Default execution
            return self._default_execute(action)
    
    def _simulate_execution(self, action: Action) -> Dict[str, Any]:
        """Simulate action execution for dry run."""
        return {
            "simulated": True,
            "action": action.description,
            "parameters": action.parameters,
            "expected_result": "success",
            "timestamp": datetime.now().isoformat()
        }
    
    def _default_execute(self, action: Action) -> Dict[str, Any]:
        """Default execution for unknown action types."""
        return {
            "action": action.description,
            "task_id": action.task_id,
            "parameters": action.parameters,
            "result": "completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def _log_transaction(self, action: Action, result: Dict[str, Any]) -> None:
        """Log transaction for potential rollback."""
        self.transaction_log.append({
            "action_id": action.id,
            "action_type": action.type,
            "description": action.description,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def _remediate(
        self,
        action: Action,
        verification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt automatic remediation for failed postconditions."""
        remediation = {
            "attempted": True,
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        
        # Attempt rollback
        rollback_result = self.rollback_action(action.id)
        remediation["actions"].append({
            "type": "rollback",
            "result": rollback_result
        })
        
        # Notify user
        remediation["actions"].append({
            "type": "notify_user",
            "message": f"Action {action.id} failed verification and was rolled back"
        })
        
        return remediation
    
    def rollback_action(self, action_id: str) -> Dict[str, Any]:
        """Rollback a previously executed action."""
        # Find transaction in log
        transaction = None
        for t in reversed(self.transaction_log):
            if t["action_id"] == action_id:
                transaction = t
                break
        
        if not transaction:
            return {
                "status": "failed",
                "error": "Transaction not found"
            }
        
        # Perform rollback (simplified for prototype)
        return {
            "status": "success",
            "action_id": action_id,
            "rolled_back": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _register_default_handlers(self) -> None:
        """Register default action handlers."""
        
        def handle_create_calendar_event(action: Action) -> Dict[str, Any]:
            """Handler for creating calendar events."""
            params = action.parameters
            return {
                "event_id": f"evt_{action.id}",
                "title": params.get("title", "Untitled"),
                "start": params.get("start"),
                "end": params.get("end"),
                "created": True,
                "timestamp": datetime.now().isoformat()
            }
        
        def handle_generate_content(action: Action) -> Dict[str, Any]:
            """Handler for generating content (soft action)."""
            params = action.parameters
            return {
                "content_type": params.get("type", "generic"),
                "content": f"Generated content for {action.task_id}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Register handlers
        self.register_action_handler(
            "create_calendar_event",
            handle_create_calendar_event,
            preconditions=[lambda a: "start" in a.parameters and "end" in a.parameters],
            postconditions=[lambda a: a.execution_result.get("created") is True]
        )
        
        self.register_action_handler(
            "generate_content",
            handle_generate_content
        )
