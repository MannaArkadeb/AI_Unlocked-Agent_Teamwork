"""
Simple example showing basic system usage.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')  # Set to UTF-8
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add parent directory to path to allow importing from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from src.main import PlanningSystem


def simple_example():
    """Simple example of using the planning system."""
    
    print("=" * 70)
    print("Simple Planning System Example")
    print("=" * 70)
    print()
    
    # 1. Initialize the system
    print("1. Initializing system...")
    system = PlanningSystem(user_id="example_user")
    print("   [OK] System ready\n")
    
    # 2. Define a goal
    print("2. Setting goal...")
    goal = "Learn machine learning fundamentals"
    print(f"   Goal: {goal}\n")
    
    # 3. Set constraints
    print("3. Setting constraints...")
    completion_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
    
    hard_constraints = {
        "completion_date": completion_date
    }
    
    soft_constraints = {
        "max_daily_hours": 2,
        "preferred_time": "evening"
    }
    
    print(f"   Deadline: {completion_date}")
    print(f"   Max daily hours: 2")
    print(f"   Preferred time: evening\n")
    
    # 4. Process the goal
    print("4. Creating plan...")
    result = system.process_goal(
        goal=goal,
        hard_constraints=hard_constraints,
        soft_constraints=soft_constraints
    )
    
    plan = result['plan']
    print(f"   ✓ Plan created: {plan.id[:8]}...\n")
    
    # 5. Review the plan
    print("5. Plan Summary:")
    print(f"   Confidence: {plan.confidence_score:.1%}")
    print(f"   Milestones: {len(plan.milestones)}")
    print(f"   Tasks: {len(plan.tasks)}")
    print(f"   Expected completion: {plan.expected_completion}")
    print()
    
    # Show milestones
    print("   Milestones:")
    for i, milestone in enumerate(plan.milestones, 1):
        print(f"   {i}. {milestone.name}")
    print()
    
    # Show first few tasks
    print("   Sample Tasks:")
    for i, task in enumerate(plan.tasks[:5], 1):
        print(f"   {i}. {task.name} ({task.effort_hours}h)")
    if len(plan.tasks) > 5:
        print(f"   ... and {len(plan.tasks) - 5} more tasks")
    print()
    
    # 6. Approve the plan
    print("6. Approving plan...")
    approval = system.approve_plan(plan.id)
    print(f"   ✓ Status: {approval['status']}\n")
    
    # 7. Check audit trail
    print("7. Audit Trail:")
    trail = system.get_audit_trail(plan_id=plan.id)
    print(f"   Total events: {trail['total_events']}")
    print(f"   Chain valid: {trail['chain_integrity']['valid']}")
    print()
    
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    simple_example()
