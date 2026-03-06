"""Input capture module for normalizing user input."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from dateutil import parser as date_parser
import re

from src.models import Constraint, ConstraintType


class InputCapture:
    """Captures and normalizes user input into structured constraints."""
    
    def __init__(self):
        self.date_patterns = [
            r'by\s+(\d{4}-\d{2}-\d{2})',
            r'deadline[:\s]+(\d{4}-\d{2}-\d{2})',
            r'due[:\s]+(\d{4}-\d{2}-\d{2})',
        ]
    
    def parse_input(
        self,
        goal: str,
        hard_constraints: Optional[Dict[str, Any]] = None,
        soft_constraints: Optional[Dict[str, Any]] = None,
        external_tokens: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Parse and normalize user input.
        
        Args:
            goal: The user's goal statement
            hard_constraints: Must-satisfy constraints (dates, prerequisites)
            soft_constraints: Optimization targets (workload, preferences)
            external_tokens: External documents (syllabus, calendar invites)
        
        Returns:
            Normalized input structure
        """
        # Normalize goal
        normalized_goal = self._normalize_goal(goal)
        
        # Extract and normalize constraints
        all_constraints = []
        
        # Parse hard constraints
        if hard_constraints:
            for key, value in hard_constraints.items():
                all_constraints.append(
                    Constraint(
                        type=ConstraintType.HARD,
                        key=key,
                        value=self._normalize_value(key, value),
                        priority=1.0
                    )
                )
        
        # Parse soft constraints
        if soft_constraints:
            for key, value in soft_constraints.items():
                all_constraints.append(
                    Constraint(
                        type=ConstraintType.SOFT,
                        key=key,
                        value=self._normalize_value(key, value),
                        priority=0.5  # Lower priority than hard constraints
                    )
                )
        
        # Extract implicit constraints from goal text
        implicit_constraints = self._extract_implicit_constraints(goal)
        all_constraints.extend(implicit_constraints)
        
        # Parse external tokens
        parsed_tokens = []
        if external_tokens:
            for token in external_tokens:
                parsed_tokens.append(self._parse_token(token))
        
        return {
            "goal": normalized_goal,
            "constraints": all_constraints,
            "external_tokens": parsed_tokens,
            "metadata": {
                "captured_at": datetime.now().isoformat(),
                "raw_goal": goal
            }
        }
    
    def _normalize_goal(self, goal: str) -> str:
        """Normalize goal statement."""
        # Remove extra whitespace
        goal = " ".join(goal.split())
        # Ensure it ends with proper punctuation
        if not goal.endswith(('.', '!', '?')):
            goal += '.'
        return goal
    
    def _normalize_value(self, key: str, value: Any) -> Any:
        """Normalize constraint values based on key type."""
        # Date normalization
        if 'date' in key.lower() or 'deadline' in key.lower():
            if isinstance(value, str):
                try:
                    return date_parser.parse(value).isoformat()
                except:
                    pass
            elif isinstance(value, datetime):
                return value.isoformat()
        
        # Numeric normalization
        if 'hours' in key.lower() or 'duration' in key.lower():
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        
        return value
    
    def _extract_implicit_constraints(self, goal: str) -> List[Constraint]:
        """Extract constraints mentioned in the goal text."""
        constraints = []
        
        # Look for deadline patterns
        for pattern in self.date_patterns:
            matches = re.findall(pattern, goal, re.IGNORECASE)
            for match in matches:
                try:
                    date_obj = date_parser.parse(match)
                    constraints.append(
                        Constraint(
                            type=ConstraintType.HARD,
                            key="implicit_deadline",
                            value=date_obj.isoformat(),
                            priority=0.9
                        )
                    )
                except:
                    pass
        
        return constraints
    
    def _parse_token(self, token: str) -> Dict[str, Any]:
        """Parse external token (file path, URL, or raw text)."""
        # For prototype, simplified parsing
        return {
            "type": "text",
            "content": token,
            "metadata": {}
        }
