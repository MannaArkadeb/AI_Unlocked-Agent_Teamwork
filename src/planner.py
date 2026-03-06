"""Hierarchical Task Network (HTN) planner with MDP scheduling."""

import networkx as nx
import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from copy import deepcopy

from src.models import Constraint, ConstraintType, Milestone, Plan, Task, TaskStatus
from src.knowledge_graph import KnowledgeGraph


class HTNPlanner:
    """
    Hierarchical Task Network planner that decomposes goals into tasks.
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        self.decomposition_rules = self._load_decomposition_rules()
    
    def decompose_goal(
        self,
        goal: str,
        constraints: List[Constraint]
    ) -> Tuple[List[Milestone], List[Task]]:
        """
        Decompose high-level goal into milestones and tasks.
        
        Returns:
            Tuple of (milestones, tasks)
        """
        # Check if we have a known decomposition pattern
        milestones, tasks = self._apply_decomposition_rules(goal, constraints)
        
        # Annotate tasks with effort estimates and skills
        for task in tasks:
            self._annotate_task(task, constraints)
        
        # Build dependency graph
        self._build_dependencies(tasks, milestones)
        
        return milestones, tasks
    
    def _load_decomposition_rules(self) -> Dict[str, Any]:
        """
        Load HTN decomposition rules.
        In a full system, these would be learned or loaded from a knowledge base.
        """
        return {
            "course_completion": {
                "milestones": [
                    {"name": "Foundation", "description": "Build fundamental understanding"},
                    {"name": "Practice", "description": "Apply concepts through exercises"},
                    {"name": "Mastery", "description": "Demonstrate mastery through projects"},
                    {"name": "Assessment", "description": "Prepare and complete final assessment"}
                ],
                "task_templates": [
                    {"name": "Review syllabus", "milestone": 0, "effort": 1.0, "skills": ["reading"]},
                    {"name": "Study core concepts", "milestone": 0, "effort": 8.0, "skills": ["reading", "note-taking"]},
                    {"name": "Complete problem sets", "milestone": 1, "effort": 12.0, "skills": ["problem-solving"]},
                    {"name": "Build practice projects", "milestone": 2, "effort": 20.0, "skills": ["coding", "debugging"]},
                    {"name": "Review materials", "milestone": 3, "effort": 6.0, "skills": ["reading"]},
                    {"name": "Take practice exams", "milestone": 3, "effort": 4.0, "skills": ["problem-solving"]},
                    {"name": "Final exam", "milestone": 3, "effort": 3.0, "skills": ["problem-solving"]}
                ]
            },
            "project_completion": {
                "milestones": [
                    {"name": "Planning", "description": "Define scope and requirements"},
                    {"name": "Implementation", "description": "Build core functionality"},
                    {"name": "Testing", "description": "Verify and validate"},
                    {"name": "Deployment", "description": "Launch and document"}
                ],
                "task_templates": [
                    {"name": "Define requirements", "milestone": 0, "effort": 2.0, "skills": ["planning"]},
                    {"name": "Design architecture", "milestone": 0, "effort": 3.0, "skills": ["design"]},
                    {"name": "Implement core features", "milestone": 1, "effort": 15.0, "skills": ["coding"]},
                    {"name": "Write tests", "milestone": 2, "effort": 5.0, "skills": ["testing"]},
                    {"name": "Document code", "milestone": 3, "effort": 3.0, "skills": ["writing"]},
                    {"name": "Deploy", "milestone": 3, "effort": 2.0, "skills": ["deployment"]}
                ]
            },
            "default": {
                "milestones": [
                    {"name": "Preparation", "description": "Gather resources and plan"},
                    {"name": "Execution", "description": "Complete main work"},
                    {"name": "Completion", "description": "Finalize and review"}
                ],
                "task_templates": [
                    {"name": "Research and plan", "milestone": 0, "effort": 3.0, "skills": ["research"]},
                    {"name": "Execute main task", "milestone": 1, "effort": 10.0, "skills": ["general"]},
                    {"name": "Review and finalize", "milestone": 2, "effort": 2.0, "skills": ["review"]}
                ]
            }
        }
    
    def _apply_decomposition_rules(
        self,
        goal: str,
        constraints: List[Constraint]
    ) -> Tuple[List[Milestone], List[Task]]:
        """Apply HTN decomposition rules based on goal pattern."""
        # Simple pattern matching for prototype
        goal_lower = goal.lower()
        
        if "course" in goal_lower or "class" in goal_lower:
            rule_key = "course_completion"
        elif "project" in goal_lower:
            rule_key = "project_completion"
        else:
            rule_key = "default"
        
        rule = self.decomposition_rules[rule_key]
        
        # Create milestones
        milestones = []
        for i, m_template in enumerate(rule["milestones"]):
            milestone = Milestone(
                name=m_template["name"],
                description=m_template["description"],
                tasks=[]
            )
            milestones.append(milestone)
        
        # Create tasks
        tasks = []
        for t_template in rule["task_templates"]:
            task = Task(
                name=t_template["name"],
                description=f"Task for {goal}",
                effort_hours=t_template["effort"],
                skills_required=t_template["skills"],
                status=TaskStatus.PLANNED
            )
            tasks.append(task)
            
            # Link task to milestone
            milestone_idx = t_template["milestone"]
            milestones[milestone_idx].tasks.append(task.id)
        
        return milestones, tasks
    
    def _annotate_task(self, task: Task, constraints: List[Constraint]) -> None:
        """Annotate task with timing constraints."""
        # Find deadline constraints
        for constraint in constraints:
            if constraint.type == ConstraintType.HARD:
                if "deadline" in constraint.key or "date" in constraint.key:
                    try:
                        deadline = datetime.fromisoformat(constraint.value)
                        task.latest_deadline = deadline
                    except:
                        pass
        
        # Set earliest start to now if not specified
        if task.earliest_start is None:
            task.earliest_start = datetime.now()
    
    def _build_dependencies(self, tasks: List[Task], milestones: List[Milestone]) -> None:
        """Build dependency relationships between tasks."""
        # Simple linear dependencies within milestones for prototype
        for milestone in milestones:
            milestone_tasks = [t for t in tasks if t.id in milestone.tasks]
            for i in range(1, len(milestone_tasks)):
                milestone_tasks[i].dependencies.append(milestone_tasks[i-1].id)
        
        # Milestones depend on previous milestones
        for i in range(1, len(milestones)):
            curr_tasks = [t for t in tasks if t.id in milestones[i].tasks]
            prev_tasks = [t for t in tasks if t.id in milestones[i-1].tasks]
            if curr_tasks and prev_tasks:
                curr_tasks[0].dependencies.append(prev_tasks[-1].id)


class MDPScheduler:
    """
    MDP-based probabilistic scheduler that produces timeline with uncertainty.
    """
    
    def __init__(self, discount_factor: float = 0.95):
        self.gamma = discount_factor  # Discount factor for future rewards
    
    def schedule(
        self,
        tasks: List[Task],
        constraints: List[Constraint],
        horizon_days: int = 90
    ) -> Dict[str, Any]:
        """
        Generate probabilistic schedule using MDP value iteration.
        
        Returns:
            Schedule with expected completion times and contingencies
        """
        # Build MDP state space
        states, actions, transitions = self._build_mdp(tasks, constraints, horizon_days)
        
        # Run value iteration
        values, policy = self._value_iteration(states, actions, transitions)
        
        # Extract schedule from policy
        schedule = self._extract_schedule(tasks, policy, states)
        
        # Compute confidence and slack
        confidence = self._compute_confidence(schedule, values)
        slack = self._compute_slack(schedule, constraints)
        
        return {
            "task_schedule": schedule,
            "confidence_score": confidence,
            "expected_slack_days": slack,
            "contingency_branches": self._generate_contingencies(schedule, transitions)
        }
    
    def _build_mdp(
        self,
        tasks: List[Task],
        constraints: List[Constraint],
        horizon_days: int
    ) -> Tuple[List[Dict], List[str], Dict]:
        """Build MDP state space, actions, and transition model."""
        # Simplified MDP for prototype
        # State: (completed_tasks, current_day)
        # Actions: work_on_task_i or rest
        
        states = []
        actions = ["rest"] + [f"work_{task.id}" for task in tasks]
        
        # Simplified transition model
        # P(s'|s,a) with uncertainty in task completion time
        transitions = {
            "completion_variance": 0.2,  # 20% variance in task duration
            "success_probability": 0.9   # 90% probability task proceeds as expected
        }
        
        return states, actions, transitions
    
    def _value_iteration(
        self,
        states: List[Dict],
        actions: List[str],
        transitions: Dict,
        max_iterations: int = 100,
        threshold: float = 0.01
    ) -> Tuple[Dict, Dict]:
        """
        Run value iteration to find optimal policy.
        
        Returns:
            (values, policy) where policy maps states to actions
        """
        # Simplified value iteration for prototype
        values = {}
        policy = {}
        
        # Initialize
        for i in range(max_iterations):
            delta = 0
            # Update would happen here in full implementation
            if delta < threshold:
                break
        
        return values, policy
    
    def _extract_schedule(
        self,
        tasks: List[Task],
        policy: Dict,
        states: List[Dict]
    ) -> Dict[str, Any]:
        """Extract concrete schedule from optimal policy."""
        schedule = {}
        current_time = datetime.now()
        
        # Simple forward simulation for prototype
        completed = set()
        for task in tasks:
            # Check if dependencies are complete
            if all(dep in completed for dep in task.dependencies):
                # Schedule task
                start_time = max(
                    current_time,
                    task.earliest_start or current_time
                )
                end_time = start_time + timedelta(hours=task.effort_hours)
                
                schedule[task.id] = {
                    "task_id": task.id,
                    "task_name": task.name,
                    "expected_start": start_time.isoformat(),
                    "expected_end": end_time.isoformat(),
                    "probability": 0.85,  # Estimated completion probability
                    "variance_hours": task.effort_hours * 0.2
                }
                
                current_time = end_time
                completed.add(task.id)
        
        return schedule
    
    def _compute_confidence(self, schedule: Dict, values: Dict) -> float:
        """Compute overall confidence score for the schedule."""
        if not schedule:
            return 0.0
        
        # Average of individual task probabilities
        probabilities = [item["probability"] for item in schedule.values()]
        return float(np.mean(probabilities))
    
    def _compute_slack(
        self,
        schedule: Dict,
        constraints: List[Constraint]
    ) -> float:
        """Compute expected slack time before deadline."""
        # Find hard deadline
        deadline = None
        for constraint in constraints:
            if constraint.type == ConstraintType.HARD and "deadline" in constraint.key:
                try:
                    deadline = datetime.fromisoformat(constraint.value)
                    break
                except:
                    pass
        
        if not deadline or not schedule:
            return 0.0
        
        # Find latest expected completion
        latest_end = max(
            datetime.fromisoformat(item["expected_end"])
            for item in schedule.values()
        )
        
        slack = (deadline - latest_end).total_seconds() / (24 * 3600)  # Days
        return max(0.0, slack)
    
    def _generate_contingencies(
        self,
        schedule: Dict,
        transitions: Dict
    ) -> List[Dict[str, Any]]:
        """Generate contingency branches for high-risk scenarios."""
        contingencies = []
        
        # Identify high-variance tasks
        for task_id, sched_item in schedule.items():
            if sched_item["variance_hours"] > 5.0:
                contingencies.append({
                    "trigger": f"task_{task_id}_delayed",
                    "probability": 0.15,
                    "mitigation": "Allocate additional time buffer",
                    "impact": f"+{sched_item['variance_hours']} hours"
                })
        
        return contingencies


class Planner:
    """Main planner orchestrating HTN decomposition and MDP scheduling."""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        self.htn_planner = HTNPlanner(knowledge_graph)
        self.mdp_scheduler = MDPScheduler()
    
    def create_plan(
        self,
        goal: str,
        constraints: List[Constraint]
    ) -> Plan:
        """
        Create a complete plan from goal and constraints.
        
        Returns:
            Complete Plan object with tasks, schedule, and metadata
        """
        # Stage A: Constraint extraction (already done in input capture)
        
        # Stage B: HTN decomposition
        milestones, tasks = self.htn_planner.decompose_goal(goal, constraints)
        
        # Stage C: Probabilistic scheduling
        schedule_result = self.mdp_scheduler.schedule(tasks, constraints)
        
        # Build critical path
        critical_path = self._compute_critical_path(tasks, schedule_result["task_schedule"])
        
        # Find expected completion
        expected_completion = None
        if schedule_result["task_schedule"]:
            latest = max(
                datetime.fromisoformat(item["expected_end"])
                for item in schedule_result["task_schedule"].values()
            )
            expected_completion = latest
        
        # Create plan
        plan = Plan(
            goal=goal,
            milestones=milestones,
            tasks=tasks,
            constraints=constraints,
            critical_path=critical_path,
            confidence_score=schedule_result["confidence_score"],
            expected_completion=expected_completion,
            contingency_branches=schedule_result["contingency_branches"]
        )
        
        return plan
    
    def _compute_critical_path(
        self,
        tasks: List[Task],
        schedule: Dict[str, Any]
    ) -> List[str]:
        """Compute critical path through task network."""
        # Build dependency graph
        G = nx.DiGraph()
        for task in tasks:
            G.add_node(task.id, duration=task.effort_hours)
            for dep in task.dependencies:
                G.add_edge(dep, task.id)
        
        # Find longest path (critical path)
        try:
            # Topological sort
            sorted_tasks = list(nx.topological_sort(G))
            # Return as critical path (simplified)
            return sorted_tasks
        except:
            return [task.id for task in tasks]
