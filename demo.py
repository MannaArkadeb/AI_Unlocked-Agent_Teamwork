"""
Demo script showcasing the Intelligent Planning & Execution System.

This demonstrates the complete workflow:
1. Input capture
2. Planning (HTN + MDP)
3. Retrieval
4. Negotiation
5. Execution
6. Learning
7. Audit
"""

from datetime import datetime, timedelta
from src.main import PlanningSystem


def print_separator(title=""):
    """Print a visual separator."""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    else:
        print(f"{'='*70}\n")


def demo_course_completion():
    """Demo: Planning for course completion."""
    print_separator("DEMO 1: Course Completion Planning")
    
    # Initialize the system
    print("Initializing planning system for user 'student_001'...")
    system = PlanningSystem(user_id="student_001")
    print("✓ System initialized\n")
    
    # Prepare some sample resources for retrieval
    print("Indexing sample resources...")
    sample_resources = [
        {
            "id": "syllabus_ds",
            "content": "Data Structures course covers arrays, linked lists, trees, graphs, sorting, and searching algorithms.",
            "metadata": {"source_type": "user_documents", "course": "Data Structures"}
        },
        {
            "id": "study_guide",
            "content": "Recommended study strategy: 2 hours theory, 3 hours practice problems daily.",
            "metadata": {"source_type": "user_documents", "type": "study_guide"}
        },
        {
            "id": "leetcode_practice",
            "content": "Practice problems for data structures: 150 curated problems on arrays, trees, and graphs.",
            "metadata": {"source_type": "web", "platform": "leetcode"}
        }
    ]
    system.retriever.index_resources(sample_resources)
    print(f"✓ Indexed {len(sample_resources)} resources\n")
    
    # Submit a goal
    print("Submitting goal: Complete Data Structures course with A grade")
    goal = "Complete Data Structures course with A grade"
    
    # Define constraints
    exam_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
    hard_constraints = {
        "final_exam_date": exam_date
    }
    soft_constraints = {
        "max_weekly_hours": 10,
        "preferred_study_time": "evening"
    }
    
    print(f"Hard constraints: Final exam on {exam_date}")
    print(f"Soft constraints: Max 10 hours/week, prefer evening study\n")
    
    # Process the goal
    print("Processing goal through pipeline...")
    result = system.process_goal(
        goal=goal,
        hard_constraints=hard_constraints,
        soft_constraints=soft_constraints
    )
    
    print(f"✓ Processing complete. Status: {result['status']}\n")
    
    # Display the plan
    plan = result['plan']
    print_separator("Generated Plan")
    print(f"Plan ID: {plan.id}")
    print(f"Goal: {plan.goal}")
    print(f"Confidence Score: {plan.confidence_score:.2f}")
    print(f"Expected Completion: {plan.expected_completion}\n")
    
    print(f"Milestones ({len(plan.milestones)}):")
    for i, milestone in enumerate(plan.milestones, 1):
        print(f"  {i}. {milestone.name}: {milestone.description}")
        print(f"     Tasks: {len(milestone.tasks)}")
    
    print(f"\nTasks ({len(plan.tasks)}):")
    for i, task in enumerate(plan.tasks, 1):
        print(f"  {i}. {task.name}")
        print(f"     Effort: {task.effort_hours} hours")
        print(f"     Skills: {', '.join(task.skills_required)}")
        if task.dependencies:
            print(f"     Dependencies: {len(task.dependencies)} task(s)")
    
    print(f"\nCritical Path: {len(plan.critical_path)} tasks")
    
    if plan.contingency_branches:
        print(f"\nContingency Scenarios: {len(plan.contingency_branches)}")
        for i, contingency in enumerate(plan.contingency_branches, 1):
            print(f"  {i}. {contingency['trigger']} (p={contingency['probability']})")
            print(f"     Mitigation: {contingency['mitigation']}")
    
    # Display negotiation digest
    print_separator("Negotiation Digest")
    digest = result['digest']
    print(f"Requires Approval: {digest.requires_approval}")
    print(f"\nSuggested Changes ({len(digest.suggested_changes)}):")
    for i, change in enumerate(digest.suggested_changes[:3], 1):  # Show first 3
        print(f"  {i}. {change['action']}")
        print(f"     Impact: {change['impact']}")
    
    if digest.alternatives:
        print(f"\nAlternatives ({len(digest.alternatives)}):")
        for i, alt in enumerate(digest.alternatives, 1):
            print(f"  {i}. {alt['description']}")
            print(f"     Impact: {alt['impact']}")
    
    if digest.expected_risks:
        print(f"\nExpected Risks ({len(digest.expected_risks)}):")
        for i, risk in enumerate(digest.expected_risks, 1):
            print(f"  {i}. {risk}")
    
    # Approve and execute
    print_separator("Approval & Execution")
    print("Requesting approval...")
    approval_result = system.approve_plan(plan.id)
    
    print(f"✓ Status: {approval_result['status']}\n")
    
    if 'execution_result' in approval_result:
        exec_result = approval_result['execution_result']
        print(f"Execution Summary:")
        print(f"  Total Actions: {exec_result['total_actions']}")
        print(f"  Successful: {exec_result['successful']}")
        print(f"  Failed: {exec_result['failed']}")
    
    # Simulate completing a task
    print_separator("Learning from Feedback")
    print("Simulating task completion...")
    
    first_task = plan.tasks[0]
    estimated_hours = first_task.effort_hours
    actual_hours = estimated_hours * 1.3  # Took 30% longer
    
    feedback_result = system.record_task_completion(
        task_id=first_task.id,
        actual_duration_hours=actual_hours
    )
    
    print(f"Task: {first_task.name}")
    print(f"  Estimated: {estimated_hours} hours")
    print(f"  Actual: {actual_hours} hours")
    print(f"  Ratio: {feedback_result['learned_ratio']:.2f}")
    print(f"\n✓ Learning engine updated with feedback")
    
    # Show audit trail
    print_separator("Audit Trail")
    audit_trail = system.get_audit_trail(plan_id=plan.id)
    
    print(f"Total Events: {audit_trail['total_events']}")
    print(f"Chain Integrity: {audit_trail['chain_integrity']['valid']}")
    print(f"\nRecent Events:")
    
    for i, event in enumerate(audit_trail['events'][-5:], 1):  # Last 5 events
        print(f"  {i}. [{event['event_type']}] {event['action']}")
        print(f"     Entity: {event['entity_id'][:40]}...")
        print(f"     Time: {event['timestamp']}")
    
    # Verify integrity
    print_separator("Audit Verification")
    integrity = system.verify_audit_integrity()
    
    print(f"Chain Valid: {integrity['valid']}")
    print(f"Total Events Verified: {integrity['total_events']}")
    
    if integrity['errors']:
        print(f"Errors Found: {len(integrity['errors'])}")
        for error in integrity['errors']:
            print(f"  - {error}")
    else:
        print("✓ No integrity violations detected")
    
    print_separator("Demo Complete")
    print("The system successfully demonstrated:")
    print("  ✓ Input capture and constraint extraction")
    print("  ✓ HTN decomposition and MDP scheduling")
    print("  ✓ Resource retrieval with evidence scoring")
    print("  ✓ Negotiation and human-in-the-loop approval")
    print("  ✓ Verified action execution")
    print("  ✓ Feedback-driven learning")
    print("  ✓ Tamper-evident audit logging")
    print()


def demo_project_planning():
    """Demo: Planning for a project."""
    print_separator("DEMO 2: Project Planning")
    
    system = PlanningSystem(user_id="developer_001")
    print("✓ System initialized for developer_001\n")
    
    # Index project resources
    resources = [
        {
            "id": "proj_requirements",
            "content": "Build a REST API with authentication, CRUD operations, and rate limiting.",
            "metadata": {"source_type": "user_documents", "type": "requirements"}
        },
        {
            "id": "tech_stack",
            "content": "Recommended: Python FastAPI, PostgreSQL, Redis, Docker",
            "metadata": {"source_type": "institutional_api", "type": "tech_guide"}
        }
    ]
    system.retriever.index_resources(resources)
    
    # Submit project goal
    deadline = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    result = system.process_goal(
        goal="Build and deploy a production-ready REST API",
        hard_constraints={"deployment_date": deadline},
        soft_constraints={"max_daily_hours": 4}
    )
    
    plan = result['plan']
    print(f"Created plan: {plan.id}")
    print(f"Milestones: {len(plan.milestones)}")
    print(f"Tasks: {len(plan.tasks)}")
    print(f"Confidence: {plan.confidence_score:.2f}")
    
    print("\nTask Breakdown:")
    for milestone in plan.milestones:
        print(f"\n{milestone.name}:")
        milestone_tasks = [t for t in plan.tasks if t.id in milestone.tasks]
        for task in milestone_tasks:
            print(f"  - {task.name} ({task.effort_hours}h)")
    
    print_separator("Demo 2 Complete")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        Intelligent Planning & Execution System                       ║
║        Prototype Demonstration                                       ║
║                                                                      ║
║  A composable, verifiable, audit-ready planning architecture         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run demos
    demo_course_completion()
    
    print("\n" * 2)
    
    demo_project_planning()
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  All demonstrations completed successfully!                          ║
║                                                                      ║
║  The prototype shows:                                                ║
║    • Hierarchical task decomposition                                 ║
║    • Probabilistic scheduling with MDP                               ║
║    • Two-stage retrieval with evidence scoring                       ║
║    • Formal verification of actions                                  ║
║    • Human-in-the-loop negotiation                                   ║
║    • Online learning from feedback                                   ║
║    • Tamper-evident audit logging                                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
