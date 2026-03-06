"""
Advanced example showing retrieval and learning features.
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


def advanced_example():
    """Advanced example with retrieval and learning."""
    
    print("\n" + "=" * 70)
    print("Advanced Example: Retrieval & Learning")
    print("=" * 70 + "\n")
    
    # Initialize
    system = PlanningSystem(user_id="advanced_user")
    
    # Index some learning resources
    print("Indexing learning resources...")
    resources = [
        {
            "id": "ml_textbook",
            "content": "Machine Learning: A Probabilistic Perspective covers supervised learning, unsupervised learning, and deep learning fundamentals.",
            "metadata": {
                "source_type": "user_documents",
                "type": "textbook",
                "difficulty": "intermediate"
            }
        },
        {
            "id": "online_course",
            "content": "Andrew Ng's Machine Learning course covers linear regression, logistic regression, neural networks, and practical tips.",
            "metadata": {
                "source_type": "web",
                "platform": "coursera",
                "difficulty": "beginner"
            }
        },
        {
            "id": "practice_problems",
            "content": "100 machine learning interview questions covering algorithms, mathematics, and implementation details.",
            "metadata": {
                "source_type": "web",
                "type": "practice",
                "difficulty": "advanced"
            }
        },
        {
            "id": "kaggle_datasets",
            "content": "Real-world datasets for practicing classification, regression, and clustering problems.",
            "metadata": {
                "source_type": "institutional_api",
                "platform": "kaggle",
                "type": "datasets"
            }
        }
    ]
    
    system.retriever.index_resources(resources)
    print(f"[OK] Indexed {len(resources)} resources\n")
    
    # Create a plan
    print("Creating learning plan...")
    result = system.process_goal(
        goal="Master machine learning algorithms and applications",
        hard_constraints={"project_deadline": "2026-06-01"},
        soft_constraints={"max_weekly_hours": 15}
    )
    
    plan = result['plan']
    task_resources = result['task_resources']
    
    print(f"[OK] Plan created with {len(plan.tasks)} tasks\n")
    
    # Show retrieved resources for tasks
    print("Resources retrieved for tasks:")
    for task_id, evidence_list in list(task_resources.items())[:3]:  # First 3 tasks
        task = next(t for t in plan.tasks if t.id == task_id)
        print(f"\n  Task: {task.name}")
        print(f"  Resources:")
        
        for i, evidence in enumerate(evidence_list, 1):
            print(f"    {i}. {evidence.source}")
            print(f"       Relevance: {evidence.relevance_score:.2f}")
            print(f"       Trust: {evidence.trust_score:.2f}")
            print(f"       Evidence Score: {evidence.evidence_score:.2f}")
    
    print("\n" + "-" * 70)
    
    # Simulate completing tasks with learning
    print("\nSimulating task completions for learning...\n")
    
    completed_tasks = []
    for i, task in enumerate(plan.tasks[:3]):  # Complete first 3 tasks
        # Simulate varying completion times
        variance = [0.9, 1.2, 1.1][i]  # First task faster, second slower, third on-time
        actual_hours = task.effort_hours * variance
        
        result = system.record_task_completion(task.id, actual_hours)
        
        print(f"Task {i+1}: {task.name}")
        print(f"  Estimated: {task.effort_hours:.1f}h")
        print(f"  Actual: {actual_hours:.1f}h")
        print(f"  Ratio: {result['learned_ratio']:.2f}")
        
        completed_tasks.append({
            'task': task,
            'ratio': result['learned_ratio']
        })
    
    # Show learning statistics
    print("\n" + "-" * 70)
    print("\nLearning Statistics:")
    
    stats = system.learning_engine.stats
    print(f"  Total feedback events: {stats['total_feedback_events']}")
    print(f"  Average completion ratio: {stats['avg_task_completion_ratio']:.2f}")
    
    params = system.learning_engine.user_params
    print(f"  Scheduling aggression: {params['scheduling_aggression']:.2f}")
    
    if params['task_duration_multipliers']:
        print(f"  Learned multipliers:")
        for skill, mult in params['task_duration_multipliers'].items():
            print(f"    {skill}: {mult:.2f}x")
    
    # Show how estimates would adjust
    print("\n" + "-" * 70)
    print("\nAdjusted Estimates for Future Tasks:")
    
    sample_estimates = [
        ("reading", ["reading", "note-taking"], 5.0),
        ("coding", ["python", "coding"], 8.0),
        ("problem-solving", ["algorithms", "problem-solving"], 6.0)
    ]
    
    for task_type, skills, base_estimate in sample_estimates:
        adjusted = system.learning_engine.get_adjusted_estimate(
            base_estimate=base_estimate,
            task_type=task_type,
            skills=skills
        )
        
        print(f"  {task_type}:")
        print(f"    Base: {base_estimate}h → Adjusted: {adjusted:.1f}h")
        print(f"    Change: {((adjusted/base_estimate - 1) * 100):+.1f}%")
    
    print("\n" + "=" * 70)
    print("Advanced example completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    advanced_example()
