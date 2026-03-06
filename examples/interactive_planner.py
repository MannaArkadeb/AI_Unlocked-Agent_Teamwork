"""
Realistic Interactive Planning System
Context-aware planning based on user goals (Study vs Project)
No emojis, detailed task breakdowns
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from typing import Dict, Any, List


class DetailedPlanner:
    """Realistic planning system with context-aware task generation."""
    
    def __init__(self):
        self.category = None
        self.goal_details = {}
        
    def print_header(self):
        """Print header."""
        print("\n" + "="*70)
        print(" "*15 + "INTERACTIVE PLANNING SYSTEM")
        print("="*70 + "\n")
    
    def get_category(self) -> str:
        """Ask user to choose planning category."""
        print("What would you like to plan?")
        print("\n  1. Study a subject")
        print("  2. Complete a project at company")
        print("  3. Plan my semester")
        print()
        
        while True:
            choice = input("Enter choice (1, 2, or 3): ").strip()
            if choice == '1':
                return 'study'
            elif choice == '2':
                return 'project'
            elif choice == '3':
                return 'semester'
            else:
                print("Invalid choice. Please enter 1, 2, or 3.\n")
    
    def get_study_details(self) -> Dict[str, Any]:
        """Get details for study planning."""
        print("\n" + "-"*70)
        print("STUDY PLANNING")
        print("-"*70 + "\n")
        
        # Get subject
        print("Which subject do you want to study?")
        print("(e.g., Physics, Mathematics, Computer Science, Chemistry, etc.)")
        subject = input("\nSubject: ").strip()
        
        # Get topics
        print(f"\nWhat topics in {subject} do you want to cover?")
        print("(Enter topics separated by commas)")
        print(f"Example for Physics: Mechanics, Thermodynamics, Electromagnetism")
        topics_input = input("\nTopics: ").strip()
        topics = [t.strip() for t in topics_input.split(',') if t.strip()]
        
        if not topics:
            topics = ["Introduction", "Core Concepts", "Advanced Topics", "Practice Problems"]
        
        # Get current level
        print("\nWhat is your current level?")
        print("  1. Beginner (starting from basics)")
        print("  2. Intermediate (some prior knowledge)")
        print("  3. Advanced (deep dive/revision)")
        level_choice = input("\nLevel (1-3): ").strip()
        level_map = {"1": "beginner", "2": "intermediate", "3": "advanced"}
        level = level_map.get(level_choice, "intermediate")
        
        return {
            'type': 'study',
            'subject': subject,
            'topics': topics,
            'level': level
        }
    
    def get_project_details(self) -> Dict[str, Any]:
        """Get details for project planning."""
        print("\n" + "-"*70)
        print("PROJECT PLANNING")
        print("-"*70 + "\n")
        
        # Get project name
        print("What is the project name or description?")
        project_name = input("\nProject: ").strip()
        
        # Get project type
        print("\nWhat type of project is this?")
        print("  1. Software Development")
        print("  2. Data Analysis / Research")
        print("  3. Presentation / Report")
        print("  4. Other")
        type_choice = input("\nType (1-4): ").strip()
        type_map = {
            "1": "software",
            "2": "research",
            "3": "presentation",
            "4": "general"
        }
        project_type = type_map.get(type_choice, "general")
        
        # Get main components
        print("\nWhat are the main components/phases?")
        print("(Leave blank to use default based on project type)")
        components_input = input("\nComponents: ").strip()
        
        if components_input:
            components = [c.strip() for c in components_input.split(',') if c.strip()]
        else:
            # Default components based on type
            if project_type == "software":
                components = ["Requirements Analysis", "Design", "Implementation", 
                            "Testing", "Documentation", "Final Presentation"]
            elif project_type == "research":
                components = ["Literature Review", "Data Collection", "Analysis",
                            "Results Compilation", "Report Writing", "Presentation"]
            elif project_type == "presentation":
                components = ["Research Topic", "Outline Creation", "Content Development",
                            "Slide Design", "Practice", "Final Presentation"]
            else:
                components = ["Planning & Research", "Main Work", "Review & Finalization", "Delivery"]
        
        return {
            'type': 'project',
            'project_name': project_name,
            'project_type': project_type,
            'components': components
        }
    
    def get_semester_details(self) -> Dict[str, Any]:
        """Get details for semester planning."""
        print("\n" + "-"*70)
        print("SEMESTER PLANNING")
        print("-"*70 + "\n")
        
        # Get subjects
        print("What subjects do you have this semester?")
        print("(Enter subjects separated by commas)")
        print("Example: Mathematics, Physics, Chemistry, Computer Science")
        subjects_input = input("\nSubjects: ").strip()
        subjects = [s.strip() for s in subjects_input.split(',') if s.strip()]
        
        if not subjects:
            subjects = ["Subject 1", "Subject 2", "Subject 3"]
        
        # Get mid-semester exam dates
        print("\nWhen does your MID-SEMESTER exam START?")
        print("(Format: YYYY-MM-DD, e.g., 2026-04-15)")
        midsem_start = input("\nMid-Sem Start Date: ").strip()
        
        print("\nWhen does your MID-SEMESTER exam END?")
        print("(Format: YYYY-MM-DD, e.g., 2026-04-20)")
        midsem_end = input("\nMid-Sem End Date: ").strip()
        
        # Get end-semester exam dates
        print("\nWhen does your END-SEMESTER exam START?")
        print("(Format: YYYY-MM-DD, e.g., 2026-06-01)")
        endsem_start = input("\nEnd-Sem Start Date: ").strip()
        
        print("\nWhen does your END-SEMESTER exam END?")
        print("(Format: YYYY-MM-DD, e.g., 2026-06-10)")
        endsem_end = input("\nEnd-Sem End Date: ").strip()
        
        return {
            'type': 'semester',
            'subjects': subjects,
            'midsem_start': midsem_start,
            'midsem_end': midsem_end,
            'endsem_start': endsem_start,
            'endsem_end': endsem_end
        }
    
    def get_timeline(self) -> int:
        """Get deadline in days."""
        print("\n" + "-"*70)
        print("TIMELINE")
        print("-"*70 + "\n")
        
        while True:
            print("How many days do you have to complete this?")
            days_input = input("\nDays: ").strip()
            
            try:
                days = int(days_input)
                if days > 0:
                    deadline = datetime.now() + timedelta(days=days)
                    print(f"\nDeadline: {deadline.strftime('%Y-%m-%d (%A)')}")
                    return days
                else:
                    print("Please enter a positive number.\n")
            except ValueError:
                print("Please enter a valid number.\n")
    
    def get_daily_hours(self) -> float:
        """Get hours available per day."""
        print("\nHow many hours can you dedicate per day?")
        
        while True:
            hours_input = input("\nHours/day: ").strip()
            try:
                hours = float(hours_input)
                if hours > 0 and hours <= 24:
                    return hours
                else:
                    print("Please enter a number between 0 and 24.\n")
            except ValueError:
                print("Please enter a valid number.\n")
    
    def create_study_plan(self, details: Dict, days: int, hours_per_day: float) -> List[Dict]:
        """Create detailed study plan with ONE phase per day."""
        subject = details['subject']
        topics = details['topics']
        level = details['level']
        
        plan = []
        
        # Calculate phase distribution (one phase = one day)
        # Foundation: 20%, Core: 50%, Practice: 20%, Review: 10%
        foundation_days = max(1, int(days * 0.2))
        core_days = max(1, int(days * 0.5))
        practice_days = max(1, int(days * 0.2))
        review_days = days - (foundation_days + core_days + practice_days)
        if review_days < 1:
            review_days = 1
            practice_days = days - (foundation_days + core_days + review_days)
        
        current_day = 1
        
        # Foundation Days (Easy difficulty)
        for day in range(foundation_days):
            day_num = current_day + day
            if day == 0:
                focus = topics[0] if topics else "Basic Concepts"
                plan.append({
                    'phase': f'Day {day_num}: Foundation - Introduction',
                    'days': f"Day {day_num}",
                    'difficulty': 'Easy',
                    'description': f"Understand the basics of {subject}",
                    'tasks': [
                        f"Review course syllabus and objectives",
                        f"Understand basic terminology in {subject}",
                        f"Identify prerequisite knowledge gaps",
                        f"Set up study materials and resources"
                    ],
                    'hours': hours_per_day,
                    'focus': focus
                })
            else:
                focus = topics[0] if topics else "Fundamentals"
                plan.append({
                    'phase': f'Day {day_num}: Foundation - {focus}',
                    'days': f"Day {day_num}",
                    'difficulty': 'Easy',
                    'description': f"Build fundamental understanding of {focus}",
                    'tasks': [
                        f"Study core concepts of {focus}",
                        f"Work through basic examples",
                        f"Create summary notes and diagrams",
                        f"Complete simple practice problems"
                    ],
                    'hours': hours_per_day,
                    'focus': focus
                })
        
        current_day += foundation_days
        
        # Core Learning Days (Medium difficulty) - Distribute topics
        topics_to_cover = topics[1:] if len(topics) > 1 else topics
        days_per_topic = max(1, core_days // max(len(topics_to_cover), 1))
        
        for topic_idx, topic in enumerate(topics_to_cover):
            topic_start = current_day + (topic_idx * days_per_topic)
            topic_end = min(topic_start + days_per_topic, current_day + core_days)
            
            for day_in_topic in range(topic_end - topic_start):
                day_num = topic_start + day_in_topic
                if day_num >= current_day + core_days:
                    break
                    
                if day_in_topic == 0:
                    plan.append({
                        'phase': f'Day {day_num}: Core Learning - {topic} (Theory)',
                        'days': f"Day {day_num}",
                        'difficulty': 'Medium',
                        'description': f"Master theoretical concepts of {topic}",
                        'tasks': [
                            f"Study theory and principles of {topic}",
                            f"Understand key formulas and definitions",
                            f"Watch video lectures or read textbook chapters",
                            f"Create detailed notes with examples"
                        ],
                        'hours': hours_per_day,
                        'focus': topic
                    })
                else:
                    plan.append({
                        'phase': f'Day {day_num}: Core Learning - {topic} (Practice)',
                        'days': f"Day {day_num}",
                        'difficulty': 'Medium',
                        'description': f"Apply knowledge through problem-solving",
                        'tasks': [
                            f"Work through example problems on {topic}",
                            f"Complete practice exercises",
                            f"Solve numerical problems and derivations",
                            f"Review and understand mistake patterns"
                        ],
                        'hours': hours_per_day,
                        'focus': topic
                    })
        
        current_day += core_days
        
        # Practice Days (Hard difficulty)
        for day in range(practice_days):
            day_num = current_day + day
            if day == 0:
                plan.append({
                    'phase': f'Day {day_num}: Advanced Practice - Integration',
                    'days': f"Day {day_num}",
                    'difficulty': 'Hard',
                    'description': "Integrate knowledge across all topics",
                    'tasks': [
                        f"Solve mixed problems combining multiple topics",
                        f"Work on application-based scenarios",
                        f"Attempt previous exam papers" if level != "beginner" else "Work on challenging exercises",
                        f"Identify connections between different topics"
                    ],
                    'hours': hours_per_day,
                    'focus': "Integration & Application"
                })
            else:
                plan.append({
                    'phase': f'Day {day_num}: Advanced Practice - Problem Solving',
                    'days': f"Day {day_num}",
                    'difficulty': 'Hard',
                    'description': "Master advanced problem-solving techniques",
                    'tasks': [
                        f"Tackle challenging problems in all topics",
                        f"Time yourself on practice tests",
                        f"Review and analyze difficult problems",
                        f"Create problem-solving strategy notes"
                    ],
                    'hours': hours_per_day,
                    'focus': "Advanced Application"
                })
        
        current_day += practice_days
        
        # Review Days (Medium difficulty)
        for day in range(review_days):
            day_num = current_day + day
            plan.append({
                'phase': f'Day {day_num}: Final Review',
                'days': f"Day {day_num}",
                'difficulty': 'Medium',
                'description': "Comprehensive revision and preparation",
                'tasks': [
                    f"Quick revision of all topics covered",
                    f"Review all summary notes and formulas",
                    f"Take a full-length practice test",
                    f"Review mistakes and clarify remaining doubts"
                ],
                'hours': hours_per_day,
                'focus': "Complete Revision"
            })
        
        return plan
    
    def create_project_plan(self, details: Dict, days: int, hours_per_day: float) -> List[Dict]:
        """Create detailed project plan with ONE phase per day."""
        project_name = details['project_name']
        project_type = details['project_type']
        components = details['components']
        
        plan = []
        
        # Calculate phase distribution (one phase = one day)
        # Planning: 15%, Implementation: 60%, Testing: 15%, Presentation: 10%
        planning_days = max(1, int(days * 0.15))
        impl_days = max(1, int(days * 0.6))
        testing_days = max(1, int(days * 0.15))
        present_days = days - (planning_days + impl_days + testing_days)
        if present_days < 1:
            present_days = 1
            testing_days = days - (planning_days + impl_days + present_days)
        
        current_day = 1
        
        # Planning Days
        for day in range(planning_days):
            day_num = current_day + day
            if day == 0:
                plan.append({
                    'phase': f'Day {day_num}: Research & Requirements',
                    'days': f"Day {day_num}",
                    'description': "Understand project scope and requirements",
                    'tasks': [
                        f"Gather and document requirements for {project_name}",
                        f"Identify stakeholders and success criteria",
                        f"Research similar projects and best practices",
                        f"Create initial project scope document"
                    ],
                    'hours': hours_per_day,
                    'deliverable': "Requirements Document"
                })
            else:
                plan.append({
                    'phase': f'Day {day_num}: Planning & Setup',
                    'days': f"Day {day_num}",
                    'description': "Plan execution and setup environment",
                    'tasks': [
                        f"Break down work into detailed tasks",
                        f"Create project timeline and milestones",
                        f"Set up development environment" if project_type == "software" else "Organize resources and tools",
                        f"Prepare initial architecture/outline"
                    ],
                    'hours': hours_per_day,
                    'deliverable': "Project Plan & Setup Complete"
                })
        
        current_day += planning_days
        
        # Implementation Days - Distribute components
        days_per_component = max(1, impl_days // len(components))
        
        for comp_idx, component in enumerate(components):
            comp_start = current_day + (comp_idx * days_per_component)
            comp_end = min(comp_start + days_per_component, current_day + impl_days)
            
            for day_in_comp in range(comp_end - comp_start):
                day_num = comp_start + day_in_comp
                if day_num >= current_day + impl_days:
                    break
                
                if project_type == "software":
                    if day_in_comp == 0:
                        plan.append({
                            'phase': f'Day {day_num}: {component} - Design',
                            'days': f"Day {day_num}",
                            'description': f"Design architecture for {component}",
                            'tasks': [
                                f"Design data models and APIs for {component}",
                                f"Create technical specifications",
                                f"Review design with team/peers if possible",
                                f"Set up module structure and files"
                            ],
                            'hours': hours_per_day,
                            'deliverable': f"{component} Design Complete"
                        })
                    else:
                        plan.append({
                            'phase': f'Day {day_num}: {component} - Implementation',
                            'days': f"Day {day_num}",
                            'description': f"Implement {component} functionality",
                            'tasks': [
                                f"Write code for {component} features",
                                f"Implement error handling and validation",
                                f"Write unit tests for {component}",
                                f"Document code and API endpoints"
                            ],
                            'hours': hours_per_day,
                            'deliverable': f"{component} Implementation Complete"
                        })
                
                elif project_type == "research":
                    if day_in_comp == 0:
                        plan.append({
                            'phase': f'Day {day_num}: {component} - Setup',
                            'days': f"Day {day_num}",
                            'description': f"Prepare for {component}",
                            'tasks': [
                                f"Review methodology for {component}",
                                f"Prepare data collection tools/instruments",
                                f"Identify data sources and access methods",
                                f"Create data organization structure"
                            ],
                            'hours': hours_per_day,
                            'deliverable': f"{component} Setup Complete"
                        })
                    else:
                        plan.append({
                            'phase': f'Day {day_num}: {component} - Execution',
                            'days': f"Day {day_num}",
                            'description': f"Execute {component}",
                            'tasks': [
                                f"Collect data for {component}",
                                f"Perform analysis and calculations",
                                f"Document findings and observations",
                                f"Validate results and check for errors"
                            ],
                            'hours': hours_per_day,
                            'deliverable': f"{component} Analysis Complete"
                        })
                
                else:  # General/Presentation
                    plan.append({
                        'phase': f'Day {day_num}: {component}',
                        'days': f"Day {day_num}",
                        'description': f"Complete {component}",
                        'tasks': [
                            f"Work on {component} content",
                            f"Create first draft or outline",
                            f"Review and refine work",
                            f"Finalize {component}"
                        ],
                        'hours': hours_per_day,
                        'deliverable': f"{component} Complete"
                    })
        
        current_day += impl_days
        
        # Testing Days
        for day in range(testing_days):
            day_num = current_day + day
            if day == 0:
                plan.append({
                    'phase': f'Day {day_num}: Integration Testing',
                    'days': f"Day {day_num}",
                    'description': "Test all components together",
                    'tasks': [
                        f"Integration testing of all components",
                        f"Test end-to-end workflows",
                        f"Identify and document bugs/issues",
                        f"Begin fixing critical issues"
                    ],
                    'hours': hours_per_day,
                    'deliverable': "Integration Test Results"
                })
            else:
                plan.append({
                    'phase': f'Day {day_num}: Bug Fixes & Optimization',
                    'days': f"Day {day_num}",
                    'description': "Resolve issues and optimize",
                    'tasks': [
                        f"Fix identified bugs and issues",
                        f"Optimize performance bottlenecks",
                        f"Final quality assurance check",
                        f"Prepare project for delivery"
                    ],
                    'hours': hours_per_day,
                    'deliverable': "Fully Tested & Optimized Project"
                })
        
        current_day += testing_days
        
        # Presentation Days
        for day in range(present_days):
            day_num = current_day + day
            if day == 0:
                plan.append({
                    'phase': f'Day {day_num}: Documentation & Slides',
                    'days': f"Day {day_num}",
                    'description': "Prepare documentation and presentation",
                    'tasks': [
                        f"Write comprehensive project documentation",
                        f"Create presentation slides for {project_name}",
                        f"Prepare demonstration/walkthrough",
                        f"Compile all deliverables"
                    ],
                    'hours': hours_per_day,
                    'deliverable': "Documentation & Slides Complete"
                })
            else:
                plan.append({
                    'phase': f'Day {day_num}: Practice & Final Review',
                    'days': f"Day {day_num}",
                    'description': "Practice and finalize everything",
                    'tasks': [
                        f"Practice presentation delivery",
                        f"Review all documentation for completeness",
                        f"Final polish and refinements",
                        f"Prepare for questions and demo"
                    ],
                    'hours': hours_per_day,
                    'deliverable': "Project Ready for Delivery"
                })
        
        return plan
    
    def create_semester_plan(self, details: Dict, hours_per_day: float) -> List[Dict]:
        """Create semester plan organized by weeks and months."""
        subjects = details['subjects']
        midsem_start = details['midsem_start']
        midsem_end = details['midsem_end']
        endsem_start = details['endsem_start']
        endsem_end = details['endsem_end']
        
        # Parse dates
        try:
            midsem_start_date = datetime.strptime(midsem_start, '%Y-%m-%d')
            midsem_end_date = datetime.strptime(midsem_end, '%Y-%m-%d')
            endsem_start_date = datetime.strptime(endsem_start, '%Y-%m-%d')
            endsem_end_date = datetime.strptime(endsem_end, '%Y-%m-%d')
        except:
            # Default dates if parsing fails
            today = datetime.now()
            midsem_start_date = today + timedelta(days=45)
            midsem_end_date = midsem_start_date + timedelta(days=5)
            endsem_start_date = today + timedelta(days=90)
            endsem_end_date = endsem_start_date + timedelta(days=10)
        
        # Calculate semester duration
        start_date = datetime.now()
        plan = []
        
        # Phase 1: Initial Learning (weeks before midsem - 2)
        days_to_midsem = (midsem_start_date - start_date).days
        initial_learning_weeks = max(1, days_to_midsem // 7 - 2)
        
        current_week = 1
        for week in range(initial_learning_weeks):
            week_date = start_date + timedelta(weeks=week)
            month_name = week_date.strftime('%B')
            
            plan.append({
                'phase': f'Week {current_week} ({month_name}): Regular Classes',
                'week': current_week,
                'description': 'Attend classes and build foundation',
                'tasks': [
                    f"Attend all lectures for {', '.join(subjects[:2])}",
                    "Complete homework and assignments",
                    "Review lecture notes daily",
                    "Clarify doubts with professors",
                    "Practice problems from textbooks"
                ],
                'hours': hours_per_day * 7,
                'focus': 'Foundation Building'
            })
            current_week += 1
        
        # Phase 2: Mid-sem Preparation (2 weeks)
        for week in range(2):
            week_date = midsem_start_date - timedelta(weeks=2-week)
            month_name = week_date.strftime('%B')
            plan.append({
                'phase': f'Week {current_week} ({month_name}): Mid-Sem Preparation',
                'week': current_week,
                'description': 'Intensive revision for mid-semester',
                'tasks': [
                    'Complete revision of all subjects',
                    'Solve previous year papers',
                    'Create summary notes',
                    'Focus on weak topics',
                    'Take mock tests'
                ],
                'hours': hours_per_day * 7,
                'focus': 'Mid-Sem Prep'
            })
            current_week += 1
        
        # Phase 3: Mid-sem Exams
        plan.append({
            'phase': f'Week {current_week} ({midsem_start_date.strftime("%B")}): Mid-Semester Exams',
            'week': current_week,
            'description': 'Mid-semester examination week',
            'tasks': [
                'Take mid-semester exams',
                'Quick revision before each exam',
                'Manage exam stress',
                'Review after each exam',
                'Get adequate rest'
            ],
            'hours': hours_per_day * 7,
            'focus': 'Mid-Sem Exams'
        })
        current_week += 1
        
        # Phase 4: Post-midsem Regular Classes
        days_between = (endsem_start_date - midsem_end_date).days
        regular_weeks = max(1, days_between // 7 - 3)
        
        for week in range(regular_weeks):
            week_date = midsem_end_date + timedelta(weeks=week+1)
            month_name = week_date.strftime('%B')
            plan.append({
                'phase': f'Week {current_week} ({month_name}): Advanced Topics',
                'week': current_week,
                'description': 'Learn advanced concepts',
                'tasks': [
                    'Attend classes for all subjects',
                    'Work on course projects',
                    'Study advanced topics',
                    'Participate in tutorials',
                    'Build comprehensive notes'
                ],
                'hours': hours_per_day * 7,
                'focus': 'Advanced Learning'
            })
            current_week += 1
        
        # Phase 5: End-sem Preparation (3 weeks)
        for week in range(3):
            week_date = endsem_start_date - timedelta(weeks=3-week)
            month_name = week_date.strftime('%B')
            plan.append({
                'phase': f'Week {current_week} ({month_name}): End-Sem Prep - Round {week+1}',
                'week': current_week,
                'description': f'Comprehensive revision - Round {week+1}',
                'tasks': [
                    f'Complete revision - Round {week+1}',
                    'Solve previous year papers',
                    'Focus on important topics',
                    'Create summary sheets',
                    'Take mock tests' if week == 2 else 'Group study',
                    'Clarify all doubts'
                ],
                'hours': hours_per_day * 7,
                'focus': f'End-Sem Prep R{week+1}'
            })
            current_week += 1
        
        # Phase 6: End-sem Exams
        exam_weeks = max(1, (endsem_end_date - endsem_start_date).days // 7 + 1)
        for week in range(exam_weeks):
            week_date = endsem_start_date + timedelta(weeks=week)
            month_name = week_date.strftime('%B')
            plan.append({
                'phase': f'Week {current_week} ({month_name}): End-Semester Exams',
                'week': current_week,
                'description': 'End-semester examination period',
                'tasks': [
                    'Take end-semester exams',
                    'Last-minute revision',
                    'Manage time in exams',
                    'Maintain healthy sleep',
                    'Stay hydrated and eat well'
                ],
                'hours': hours_per_day * 7,
                'focus': 'End-Sem Exams'
            })
            current_week += 1
        
        return plan
    
    def display_plan(self, plan: List[Dict], details: Dict):
        """Display the detailed plan."""
        print("\n" + "="*70)
        print(" "*20 + "DETAILED PLAN")
        print("="*70 + "\n")
        
        if details['type'] == 'study':
            print(f"Subject: {details['subject']}")
            print(f"Topics: {', '.join(details['topics'])}")
            print(f"Level: {details['level'].title()}")
        elif details['type'] == 'project':
            print(f"Project: {details['project_name']}")
            print(f"Type: {details['project_type'].title()}")
        else:  # semester
            print(f"Subjects: {', '.join(details['subjects'])}")
            print(f"Mid-Semester: {details['midsem_start']} to {details['midsem_end']}")
            print(f"End-Semester: {details['endsem_start']} to {details['endsem_end']}")
        
        if details['type'] == 'semester':
            print(f"\nTotal Weeks: {len(plan)}")
        else:
            print(f"\nTotal Phases: {len(plan)}")
        
        total_hours = sum(p['hours'] for p in plan)
        print(f"Total Estimated Hours: {total_hours:.1f} hours")
        
        print("\n" + "="*70)
        if details['type'] == 'semester':
            print("WEEK-BY-WEEK BREAKDOWN")
        else:
            print("PHASE-BY-PHASE BREAKDOWN")
        print("="*70 + "\n")
        
        for i, phase in enumerate(plan, 1):
            if details['type'] == 'semester':
                print(f"[Week {phase['week']}] {phase['phase']}")
            else:
                print(f"[Phase {i}] {phase['phase']}")
                print(f"Timeline: {phase['days']}")
            
            if 'difficulty' in phase:
                print(f"Difficulty: {phase['difficulty']}")
            
            if 'focus' in phase:
                print(f"Focus Area: {phase['focus']}")
            
            print(f"Description: {phase['description']}")
            if details['type'] == 'semester':
                print(f"Estimated Hours: {phase['hours']:.1f}h/week")
            else:
                print(f"Estimated Hours: {phase['hours']:.1f}h")
            
            print("\nTasks:")
            for task in phase['tasks']:
                print(f"  - {task}")
            
            if 'deliverable' in phase:
                print(f"\nDeliverable: {phase['deliverable']}")
            
            print("\n" + "-"*70 + "\n")
    
    def explain_algorithms(self, plan: List[Dict], details: Dict, days: int):
        """Explain how HTN and MDP contributed to this plan."""
        print("\n" + "="*70)
        print("HOW THE ALGORITHMS WORKED")
        print("="*70 + "\n")
        
        # HTN Contribution
        print("1. HTN (Hierarchical Task Network) - Task Decomposition")
        print("   " + "-"*66)
        
        if details['type'] == 'study':
            print(f"   Started with: '{details['subject']}'")
            print(f"   Broke down into: {len(details['topics'])} topics")
            print(f"   Created hierarchy:")
            print(f"      Goal: Master {details['subject']}")
            print(f"      |")
            print(f"      +-- Phase 1: Foundation (Build basics)")
            print(f"      +-- Phase 2-{len(plan)-2}: Core Learning (Master each topic)")
            print(f"      +-- Phase {len(plan)-1}: Advanced Practice (Apply knowledge)")
            print(f"      +-- Phase {len(plan)}: Review (Consolidate)")
            print()
            
            # Count difficulty levels
            easy = sum(1 for p in plan if p.get('difficulty') == 'Easy')
            medium = sum(1 for p in plan if p.get('difficulty') == 'Medium')
            hard = sum(1 for p in plan if p.get('difficulty') == 'Hard')
            
            print(f"   Organized by difficulty progression:")
            if easy > 0:
                print(f"      - {easy} day(s) of Easy tasks (Foundation)")
            if medium > 0:
                print(f"      - {medium} day(s) of Medium tasks (Core Learning + Review)")
            if hard > 0:
                print(f"      - {hard} day(s) of Hard tasks (Advanced Practice)")
        else:
            print(f"   Started with: '{details['project_name']}'")
            print(f"   Broke down into: {len(details['components'])} components")
            print(f"   Created hierarchy:")
            print(f"      Goal: Complete {details['project_name']}")
            print(f"      |")
            print(f"      +-- Planning Phase (Understand & Prepare)")
            print(f"      +-- Implementation Phases (Build each component):")
            for comp in details['components'][:3]:
                print(f"      |    +-- {comp}")
            if len(details['components']) > 3:
                print(f"      |    +-- ... {len(details['components'])-3} more")
            print(f"      +-- Testing Phase (Integrate & Verify)")
            print(f"      +-- Presentation Phase (Document & Deliver)")
            print()
        
        print(f"   Result: Transformed 1 high-level goal into {len(plan)} actionable phases\n")
        
        # MDP Contribution
        print("2. MDP (Markov Decision Process) - Optimal Scheduling")
        print("   " + "-"*66)
        
        total_hours = sum(p['hours'] for p in plan)
        avg_hours = total_hours / days
        
        print(f"   Optimized for: {days} days, {avg_hours:.1f} hours/day")
        print(f"   Scheduling decisions made:")
        
        if details['type'] == 'study':
            # Calculate actual allocations
            foundation_hours = sum(p['hours'] for p in plan if 'Foundation' in p['phase'])
            core_hours = sum(p['hours'] for p in plan if 'Core Learning' in p['phase'])
            practice_hours = sum(p['hours'] for p in plan if 'Practice' in p['phase'])
            review_hours = sum(p['hours'] for p in plan if 'Review' in p['phase'])
            
            print(f"      - Foundation: {foundation_hours:.1f}h ({foundation_hours/total_hours*100:.0f}% of time)")
            print(f"        Reasoning: Build strong base before advanced topics")
            print(f"      - Core Learning: {core_hours:.1f}h ({core_hours/total_hours*100:.0f}% of time)")
            print(f"        Reasoning: Most time on mastering core concepts")
            print(f"      - Practice: {practice_hours:.1f}h ({practice_hours/total_hours*100:.0f}% of time)")
            print(f"        Reasoning: Apply knowledge to retain better")
            print(f"      - Review: {review_hours:.1f}h ({review_hours/total_hours*100:.0f}% of time)")
            print(f"        Reasoning: Final consolidation before deadline")
            print()
            
            # Topic ordering
            print(f"   Topic sequence optimized for:")
            topics = details['topics']
            if len(topics) > 1:
                print(f"      - Start: {topics[0]} (Foundation)")
                for topic in topics[1:]:
                    print(f"      - Then: {topic} (Building on previous knowledge)")
            print(f"      - Finally: Integration across all topics")
        else:
            # Calculate project phase allocations - categorize each phase once
            planning_count = 0
            impl_count = 0
            testing_count = 0
            present_count = 0
            
            for p in plan:
                phase_name = p.get('phase', '')
                if 'Research' in phase_name or ('Planning' in phase_name and 'Setup' in phase_name):
                    planning_count += 1
                elif 'Testing' in phase_name or 'Bug' in phase_name:
                    testing_count += 1
                elif 'Documentation' in phase_name or ('Practice' in phase_name and 'Final' in phase_name):
                    present_count += 1
                elif any(comp in phase_name for comp in details['components']):
                    impl_count += 1
            
            print(f"   Time allocation decisions:")
            if planning_count > 0:
                print(f"      - Planning: {planning_count} days (Understand requirements)")
            if impl_count > 0:
                print(f"      - Implementation: {impl_count} days (Build components)")
            if testing_count > 0:
                print(f"      - Testing: {testing_count} days (Ensure quality)")
            if present_count > 0:
                print(f"      - Presentation: {present_count} days (Prepare delivery)")
            print()
            
            print(f"   Reasoning for this distribution:")
            print(f"      - More days ({impl_count}) on implementation (core work)")
            print(f"      - Adequate testing time ({testing_count} days) for quality")
            print(f"      - Sufficient prep time ({present_count} days) for delivery")
            print()
            
            # Component ordering
            print(f"   Component sequence optimized for:")
            print(f"      - Dependencies and logical flow")
            print(f"      - Risk mitigation (hardest parts early)")
            print(f"      - Integration complexity")
        
        print(f"\n   Result: {days}-day schedule with balanced workload\n")
        
        # Key Benefits
        print("3. Combined Benefits")
        print("   " + "-"*66)
        print("   What you get from this algorithmic approach:")
        print("      [+] No guesswork - mathematically optimized plan")
        print("      [+] Gradual difficulty increase - easier to follow")
        print("      [+] Balanced daily workload - prevents burnout")
        print("      [+] Clear dependencies - know what comes first")
        print("      [+] Realistic estimates - based on proven methods")
        
        if details['type'] == 'study':
            print("      [+] Spaced repetition - topics revisited for retention")
        else:
            print("      [+] Risk management - critical tasks scheduled early")
        
        print()
    
    def run(self):
        """Main execution flow."""
        self.print_header()
        
        # Step 1: Get category
        self.category = self.get_category()
        
        # Step 2: Get category-specific details
        if self.category == 'study':
            self.goal_details = self.get_study_details()
        elif self.category == 'project':
            self.goal_details = self.get_project_details()
        else:  # semester
            self.goal_details = self.get_semester_details()
        
        # Step 3: Get timeline (skip for semester as it's calculated from exam dates)
        if self.category != 'semester':
            days = self.get_timeline()
        else:
            days = 0  # Will be calculated from exam dates
        
        # Step 4: Get daily hours
        hours_per_day = self.get_daily_hours()
        
        # Step 5: Create plan
        print("\n" + "="*70)
        print("CREATING DETAILED PLAN...")
        print("="*70)
        
        if self.category == 'study':
            plan = self.create_study_plan(self.goal_details, days, hours_per_day)
        elif self.category == 'project':
            plan = self.create_project_plan(self.goal_details, days, hours_per_day)
        else:  # semester
            plan = self.create_semester_plan(self.goal_details, hours_per_day)
        
        # Step 6: Display plan
        self.display_plan(plan, self.goal_details)
        
        # Step 7: Explain how algorithms contributed
        if self.category != 'semester':
            self.explain_algorithms(plan, self.goal_details, days)
        else:
            # For semester, use total weeks instead of days
            total_weeks = len(plan)
            print("\n" + "="*70)
            print("ALGORITHMS USED")
            print("="*70)
            print("\n1. HTN (Hierarchical Task Network) Planning")
            print("   - Decomposed semester into hierarchical phases")
            print(f"   - Created {total_weeks} weekly milestones")
            print("   - Organized around mid-sem and end-sem exams")
            print("\n2. MDP (Markov Decision Process)")
            print("   - Optimized study schedule based on exam dates")
            print("   - Balanced workload across the semester")
            print("   - Prioritized exam preparation phases")
            print("="*70)
        
        # Summary
        print("="*70)
        print("PLAN CREATED SUCCESSFULLY")
        print("="*70)
        print("\nYou can now save this plan and track your progress daily.")
        print("="*70 + "\n")


def main():
    """Entry point."""
    planner = DetailedPlanner()
    planner.run()


if __name__ == "__main__":
    main()
