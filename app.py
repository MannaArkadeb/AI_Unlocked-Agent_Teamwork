"""Flask web application for Planning Master."""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

class WebPlanner:
    """Planning system for web interface."""
    
    def __init__(self):
        self.questions = [
            {
                'id': 'category',
                'question': 'What would you like to plan?',
                'type': 'choice',
                'options': [
                    {'value': 'study', 'label': 'Study a subject'},
                    {'value': 'project', 'label': 'Complete a project at company'},
                    {'value': 'semester', 'label': 'Plan my semester'}
                ]
            }
        ]
        
        self.study_questions = [
            {
                'id': 'subject',
                'question': 'Which subject do you want to study? (e.g., Physics, Mathematics, Computer Science, Chemistry)',
                'type': 'text',
                'placeholder': 'Enter subject name'
            },
            {
                'id': 'topics',
                'question': 'What topics do you want to cover? (separate by commas)',
                'type': 'text',
                'placeholder': 'e.g., Mechanics, Thermodynamics, Electromagnetism'
            },
            {
                'id': 'level',
                'question': 'What is your current level?',
                'type': 'choice',
                'options': [
                    {'value': 'beginner', 'label': 'Beginner (starting from basics)'},
                    {'value': 'intermediate', 'label': 'Intermediate (some prior knowledge)'},
                    {'value': 'advanced', 'label': 'Advanced (deep dive/revision)'}
                ]
            }
        ]
        
        self.project_questions = [
            {
                'id': 'project_name',
                'question': 'What is the project name or description?',
                'type': 'text',
                'placeholder': 'Enter project name'
            },
            {
                'id': 'project_type',
                'question': 'What type of project is this?',
                'type': 'choice',
                'options': [
                    {'value': 'software', 'label': 'Software Development'},
                    {'value': 'research', 'label': 'Data Analysis / Research'},
                    {'value': 'presentation', 'label': 'Presentation / Report'},
                    {'value': 'general', 'label': 'Other'}
                ]
            },
            {
                'id': 'components',
                'question': 'What are the main components/phases? (leave blank for defaults based on project type)',
                'type': 'text',
                'placeholder': 'e.g., Design, Implementation, Testing',
                'required': False
            }
        ]
        
        self.semester_questions = [
            {
                'id': 'subjects',
                'question': 'What subjects do you have this semester? (separate by commas)',
                'type': 'text',
                'placeholder': 'e.g., Mathematics, Physics, Chemistry, Computer Science'
            },
            {
                'id': 'midsem_start',
                'question': 'When does your mid-semester exam START? (YYYY-MM-DD)',
                'type': 'text',
                'placeholder': 'e.g., 2026-04-15'
            },
            {
                'id': 'midsem_end',
                'question': 'When does your mid-semester exam END? (YYYY-MM-DD)',
                'type': 'text',
                'placeholder': 'e.g., 2026-04-20'
            },
            {
                'id': 'endsem_start',
                'question': 'When does your end-semester exam START? (YYYY-MM-DD)',
                'type': 'text',
                'placeholder': 'e.g., 2026-06-01'
            },
            {
                'id': 'endsem_end',
                'question': 'When does your end-semester exam END? (YYYY-MM-DD)',
                'type': 'text',
                'placeholder': 'e.g., 2026-06-10'
            }
        ]
        
        self.timeline_questions = [
            {
                'id': 'days',
                'question': 'How many days do you have to complete this?',
                'type': 'number',
                'placeholder': 'Enter number of days'
            },
            {
                'id': 'hours_per_day',
                'question': 'How many hours can you dedicate per day?',
                'type': 'number',
                'placeholder': 'Enter hours per day (0-24)',
                'min': 0.5,
                'max': 24,
                'step': 0.5
            }
        ]
    
    def get_question_flow(self, category: str = None) -> List[Dict]:
        """Get the complete question flow based on category."""
        flow = self.questions.copy()
        
        if category == 'study':
            flow.extend(self.study_questions)
            flow.extend(self.timeline_questions)  # Add both days and hours
        elif category == 'project':
            flow.extend(self.project_questions)
            flow.extend(self.timeline_questions)  # Add both days and hours
        elif category == 'semester':
            flow.extend(self.semester_questions)
            # Only add hours_per_day question, not days
            flow.append(self.timeline_questions[1])  # hours_per_day only
        
        return flow
    
    def create_plan(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Create a plan based on user answers."""
        category = answers.get('category')
        days = int(answers.get('days', 7))
        hours_per_day = float(answers.get('hours_per_day', 2))
        
        if category == 'study':
            return self._create_study_plan(answers, days, hours_per_day)
        elif category == 'project':
            return self._create_project_plan(answers, days, hours_per_day)
        elif category == 'semester':
            return self._create_semester_plan(answers, days, hours_per_day)
        else:
            return self._create_study_plan(answers, days, hours_per_day)
    
    def _create_study_plan(self, answers: Dict, days: int, hours_per_day: float) -> Dict:
        """Create study plan."""
        subject = answers.get('subject', 'Unknown Subject')
        topics_str = answers.get('topics', '')
        topics = [t.strip() for t in topics_str.split(',') if t.strip()]
        if not topics:
            topics = ['Introduction', 'Core Concepts', 'Advanced Topics', 'Practice']
        level = answers.get('level', 'intermediate')
        
        # Calculate phase distribution
        foundation_days = max(1, int(days * 0.2))
        core_days = max(1, int(days * 0.5))
        practice_days = max(1, int(days * 0.2))
        review_days = days - (foundation_days + core_days + practice_days)
        if review_days < 1:
            review_days = 1
            practice_days = days - (foundation_days + core_days + review_days)
        
        plan = []
        current_day = 1
        
        # Foundation phase
        for day in range(foundation_days):
            day_num = current_day + day
            focus = topics[0] if topics else "Basic Concepts"
            plan.append({
                'phase': f'Day {day_num}: Foundation - {focus}',
                'day': day_num,
                'difficulty': 'Easy',
                'description': f'Build fundamental understanding of {focus}' if day > 0 else f'Understand the basics of {subject}',
                'tasks': [
                    f'Review course syllabus and objectives' if day == 0 else f'Study core concepts of {focus}',
                    f'Understand basic terminology in {subject}' if day == 0 else f'Work through basic examples',
                    f'Identify prerequisite knowledge gaps' if day == 0 else f'Create summary notes and diagrams',
                    f'Set up study materials and resources' if day == 0 else f'Complete simple practice problems'
                ],
                'hours': hours_per_day
            })
        
        current_day += foundation_days
        
        # Core learning phase
        topics_to_cover = topics[1:] if len(topics) > 1 else topics
        days_per_topic = max(1, core_days // max(len(topics_to_cover), 1))
        
        for topic_idx, topic in enumerate(topics_to_cover):
            topic_start = current_day + (topic_idx * days_per_topic)
            topic_end = min(topic_start + days_per_topic, current_day + core_days)
            
            for day_in_topic in range(topic_end - topic_start):
                day_num = topic_start + day_in_topic
                if day_num >= current_day + core_days:
                    break
                
                phase_type = 'Theory' if day_in_topic == 0 else 'Practice'
                plan.append({
                    'phase': f'Day {day_num}: Core Learning - {topic} ({phase_type})',
                    'day': day_num,
                    'difficulty': 'Medium',
                    'description': f'Master theoretical concepts of {topic}' if day_in_topic == 0 else f'Apply knowledge through problem-solving',
                    'tasks': [
                        f'Study theory and principles of {topic}' if day_in_topic == 0 else f'Work through example problems on {topic}',
                        f'Understand key formulas and definitions' if day_in_topic == 0 else f'Complete practice exercises',
                        f'Watch video lectures or read textbook chapters' if day_in_topic == 0 else f'Solve numerical problems and derivations',
                        f'Create detailed notes with examples' if day_in_topic == 0 else f'Review and understand mistake patterns'
                    ],
                    'hours': hours_per_day
                })
        
        current_day += core_days
        
        # Practice phase
        for day in range(practice_days):
            day_num = current_day + day
            plan.append({
                'phase': f'Day {day_num}: Advanced Practice',
                'day': day_num,
                'difficulty': 'Hard',
                'description': 'Integrate knowledge across all topics' if day == 0 else 'Master advanced problem-solving',
                'tasks': [
                    f'Solve mixed problems combining multiple topics' if day == 0 else f'Tackle challenging problems',
                    f'Work on application-based scenarios' if day == 0 else f'Time yourself on practice tests',
                    f'Attempt previous exam papers' if level != 'beginner' else f'Work on challenging exercises',
                    f'Identify connections between topics' if day == 0 else f'Create problem-solving strategy notes'
                ],
                'hours': hours_per_day
            })
        
        current_day += practice_days
        
        # Review phase
        for day in range(review_days):
            day_num = current_day + day
            plan.append({
                'phase': f'Day {day_num}: Final Review',
                'day': day_num,
                'difficulty': 'Medium',
                'description': 'Comprehensive revision and preparation',
                'tasks': [
                    'Quick revision of all topics covered',
                    'Review all summary notes and formulas',
                    'Take a full-length practice test',
                    'Review mistakes and clarify remaining doubts'
                ],
                'hours': hours_per_day
            })
        
        # Generate MDP/HTN details
        mdp_details = self._generate_mdp_details(plan, 'study', subject)
        htn_details = self._generate_htn_details(plan, 'study', subject)
        
        return {
            'category': 'study',
            'subject': subject,
            'topics': topics,
            'level': level,
            'timeline': {
                'total_days': days,
                'hours_per_day': hours_per_day,
                'total_hours': days * hours_per_day,
                'deadline': (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            },
            'plan': plan,
            'mdp_details': mdp_details,
            'htn_details': htn_details
        }
    
    def _create_project_plan(self, answers: Dict, days: int, hours_per_day: float) -> Dict:
        """Create project plan."""
        project_name = answers.get('project_name', 'Unnamed Project')
        project_type = answers.get('project_type', 'general')
        components_str = answers.get('components', '')
        
        # Get components
        if components_str and components_str.strip():
            components = [c.strip() for c in components_str.split(',') if c.strip()]
        else:
            if project_type == 'software':
                components = ['Requirements Analysis', 'Design', 'Implementation', 
                            'Testing', 'Documentation', 'Final Presentation']
            elif project_type == 'research':
                components = ['Literature Review', 'Data Collection', 'Analysis',
                            'Results Compilation', 'Report Writing', 'Presentation']
            elif project_type == 'presentation':
                components = ['Research Topic', 'Outline Creation', 'Content Development',
                            'Slide Design', 'Practice', 'Final Presentation']
            else:
                components = ['Planning & Research', 'Main Work', 'Review & Finalization', 'Delivery']
        
        # Calculate phase distribution
        planning_days = max(1, int(days * 0.15))
        implementation_days = max(1, int(days * 0.60))
        testing_days = max(1, int(days * 0.15))
        presentation_days = days - (planning_days + implementation_days + testing_days)
        if presentation_days < 1:
            presentation_days = 1
            testing_days = days - (planning_days + implementation_days + presentation_days)
        
        plan = []
        current_day = 1
        
        # Planning phase
        for day in range(planning_days):
            day_num = current_day + day
            plan.append({
                'phase': f'Day {day_num}: Planning & Setup',
                'day': day_num,
                'difficulty': 'Easy',
                'description': 'Define scope and requirements',
                'tasks': [
                    f'Define project requirements and scope',
                    f'Research and gather necessary resources',
                    f'Create initial project timeline',
                    f'Set up development environment and tools'
                ],
                'hours': hours_per_day
            })
        
        current_day += planning_days
        
        # Implementation phase
        days_per_component = max(1, implementation_days // len(components))
        for comp_idx, component in enumerate(components[:-1]):  # Exclude last component (usually presentation)
            comp_start = current_day + (comp_idx * days_per_component)
            comp_end = min(comp_start + days_per_component, current_day + implementation_days)
            
            for day_in_comp in range(comp_end - comp_start):
                day_num = comp_start + day_in_comp
                if day_num >= current_day + implementation_days:
                    break
                
                plan.append({
                    'phase': f'Day {day_num}: {component}',
                    'day': day_num,
                    'difficulty': 'Hard',
                    'description': f'Work on {component}',
                    'tasks': [
                        f'Complete main work for {component}',
                        f'Document progress and decisions',
                        f'Review and refine output',
                        f'Prepare for next phase'
                    ],
                    'hours': hours_per_day
                })
        
        current_day += implementation_days
        
        # Testing/Review phase
        for day in range(testing_days):
            day_num = current_day + day
            plan.append({
                'phase': f'Day {day_num}: Testing & Review',
                'day': day_num,
                'difficulty': 'Medium',
                'description': 'Verify and validate work',
                'tasks': [
                    'Test all components thoroughly',
                    'Identify and fix issues',
                    'Get feedback from stakeholders',
                    'Refine based on feedback'
                ],
                'hours': hours_per_day
            })
        
        current_day += testing_days
        
        # Presentation/Final phase
        for day in range(presentation_days):
            day_num = current_day + day
            plan.append({
                'phase': f'Day {day_num}: Final Preparation',
                'day': day_num,
                'difficulty': 'Medium',
                'description': 'Prepare for delivery',
                'tasks': [
                    'Create final presentation/documentation',
                    'Practice delivery',
                    'Final review and polishing',
                    'Submit/Present final work'
                ],
                'hours': hours_per_day
            })
        
        # Generate MDP/HTN details
        mdp_details = self._generate_mdp_details(plan, 'project', project_name)
        htn_details = self._generate_htn_details(plan, 'project', project_name)
        
        return {
            'category': 'project',
            'project_name': project_name,
            'project_type': project_type,
            'components': components,
            'timeline': {
                'total_days': days,
                'hours_per_day': hours_per_day,
                'total_hours': days * hours_per_day,
                'deadline': (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            },
            'plan': plan,
            'mdp_details': mdp_details,
            'htn_details': htn_details
        }
    
    def _create_semester_plan(self, answers: Dict, days: int, hours_per_day: float) -> Dict:
        """Create semester plan organized by months and weeks."""
        subjects_str = answers.get('subjects', '')
        subjects = [s.strip() for s in subjects_str.split(',') if s.strip()]
        if not subjects:
            subjects = ['Subject 1', 'Subject 2', 'Subject 3']
        
        midsem_start = answers.get('midsem_start', '')
        midsem_end = answers.get('midsem_end', '')
        endsem_start = answers.get('endsem_start', '')
        endsem_end = answers.get('endsem_end', '')
        
        # Parse dates
        from datetime import datetime, timedelta
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
        total_days_to_endsem = (endsem_end_date - start_date).days
        
        plan = []
        
        # Phase 1: Initial Learning (First 40% of time before midsem)
        days_to_midsem = (midsem_start_date - start_date).days
        initial_learning_weeks = max(1, days_to_midsem // 7 - 2)
        
        subjects_per_week = max(1, len(subjects) // max(1, initial_learning_weeks))
        
        current_week = 1
        for week in range(initial_learning_weeks):
            week_subjects = subjects[week * subjects_per_week:(week + 1) * subjects_per_week]
            if not week_subjects and subjects:
                week_subjects = [subjects[week % len(subjects)]]
            
            month_name = (start_date + timedelta(weeks=week)).strftime('%B')
            
            plan.append({
                'phase': f'Week {current_week} ({month_name}): Regular Classes - {", ".join(week_subjects)}',
                'week': current_week,
                'month': month_name,
                'difficulty': 'Easy',
                'description': f'Attend classes and build foundation in {", ".join(week_subjects)}',
                'tasks': [
                    f'Attend all lectures for {", ".join(week_subjects)}',
                    'Complete homework and assignments',
                    'Review lecture notes daily',
                    'Clarify doubts with professors/peers',
                    'Practice problems from textbooks'
                ],
                'hours': hours_per_day * 7
            })
            current_week += 1
        
        # Phase 2: Mid-sem Preparation (2 weeks before midsem)
        for week in range(2):
            month_name = (midsem_start_date - timedelta(weeks=2-week)).strftime('%B')
            plan.append({
                'phase': f'Week {current_week} ({month_name}): Mid-Sem Preparation',
                'week': current_week,
                'month': month_name,
                'difficulty': 'Medium',
                'description': 'Intensive revision for mid-semester exams',
                'tasks': [
                    'Complete revision of all subjects covered so far',
                    'Solve previous year mid-sem papers',
                    'Create summary notes and formula sheets',
                    'Focus on weak topics identified',
                    'Take mock tests and time yourself'
                ],
                'hours': hours_per_day * 7
            })
            current_week += 1
        
        # Phase 3: Mid-sem Week
        plan.append({
            'phase': f'Week {current_week} ({midsem_start_date.strftime("%B")}): Mid-Semester Exams',
            'week': current_week,
            'month': midsem_start_date.strftime('%B'),
            'difficulty': 'Hard',
            'description': 'Mid-semester examination week',
            'tasks': [
                'Take mid-semester exams as per schedule',
                'Quick revision 1-2 hours before each exam',
                'Stay calm and manage exam stress',
                'Review each exam after completion',
                'Get adequate rest between exams'
            ],
            'hours': hours_per_day * 7
        })
        current_week += 1
        
        # Phase 4: Post-midsem Regular Classes
        days_between_exams = (endsem_start_date - midsem_end_date).days
        regular_weeks = max(1, days_between_exams // 7 - 3)
        
        for week in range(regular_weeks):
            week_date = midsem_end_date + timedelta(weeks=week+1)
            month_name = week_date.strftime('%B')
            week_subjects = subjects[week % len(subjects):(week % len(subjects)) + 2] if subjects else subjects[:2]
            if not week_subjects and subjects:
                week_subjects = [subjects[0]]
            
            plan.append({
                'phase': f'Week {current_week} ({month_name}): Advanced Topics - {", ".join(week_subjects)}',
                'week': current_week,
                'month': month_name,
                'difficulty': 'Medium',
                'description': f'Learn advanced concepts in {", ".join(week_subjects)}',
                'tasks': [
                    f'Attend classes for {", ".join(week_subjects)}',
                    'Work on course projects and assignments',
                    'Study advanced topics and applications',
                    'Participate in tutorials and labs',
                    'Build comprehensive notes'
                ],
                'hours': hours_per_day * 7
            })
            current_week += 1
        
        # Phase 5: End-sem Preparation (3 weeks before endsem)
        for week in range(3):
            week_date = endsem_start_date - timedelta(weeks=3-week)
            month_name = week_date.strftime('%B')
            intensity = 'Hard' if week == 2 else 'Medium'
            
            plan.append({
                'phase': f'Week {current_week} ({month_name}): End-Sem Preparation - Round {week + 1}',
                'week': current_week,
                'month': month_name,
                'difficulty': intensity,
                'description': f'Comprehensive revision for end-semester exams (Round {week + 1})',
                'tasks': [
                    f'Complete revision of all subjects - Round {week + 1}',
                    'Solve previous year question papers',
                    'Focus on important topics and likely questions',
                    'Create mind maps and summary sheets',
                    'Take full-length mock tests' if week == 2 else 'Group study sessions',
                    'Clarify all remaining doubts'
                ],
                'hours': hours_per_day * 7
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
                'month': month_name,
                'difficulty': 'Hard',
                'description': 'End-semester examination period',
                'tasks': [
                    'Take end-semester exams as scheduled',
                    'Last-minute revision before each exam',
                    'Stay focused and manage time in exams',
                    'Maintain healthy sleep schedule',
                    'Stay hydrated and eat well'
                ],
                'hours': hours_per_day * 7
            })
            current_week += 1
        
        # Generate MDP/HTN details
        mdp_details = self._generate_mdp_details(plan, 'semester', f'Semester with {len(subjects)} subjects')
        htn_details = self._generate_htn_details(plan, 'semester', f'Semester Planning')
        
        return {
            'category': 'semester',
            'subjects': subjects,
            'num_subjects': len(subjects),
            'midsem_dates': f'{midsem_start} to {midsem_end}',
            'endsem_dates': f'{endsem_start} to {endsem_end}',
            'timeline': {
                'total_days': total_days_to_endsem,
                'total_weeks': current_week - 1,
                'hours_per_day': hours_per_day,
                'total_hours': (current_week - 1) * 7 * hours_per_day,
                'deadline': endsem_end_date.strftime('%Y-%m-%d')
            },
            'plan': plan,
            'mdp_details': mdp_details,
            'htn_details': htn_details
        }
    
    def _generate_mdp_details(self, plan: List[Dict], category: str, name: str) -> Dict:
        """Generate MDP (Markov Decision Process) details."""
        states = []
        transitions = []
        
        # Create states from plan phases
        for idx, phase in enumerate(plan):
            states.append({
                'id': f'S{idx}',
                'name': phase['phase'],
                'description': phase['description'],
                'difficulty': phase['difficulty']
            })
        
        # Create transitions between consecutive states
        for idx in range(len(plan) - 1):
            transitions.append({
                'from': f'S{idx}',
                'to': f'S{idx + 1}',
                'action': f'Complete {plan[idx]["phase"]}',
                'reward': 10 if plan[idx]['difficulty'] == 'Hard' else 5 if plan[idx]['difficulty'] == 'Medium' else 3,
                'probability': 0.95
            })
        
        return {
            'description': 'MDP models the planning process as a sequence of states and transitions with associated rewards',
            'total_states': len(states),
            'states': states,
            'transitions': transitions,
            'reward_function': 'Reward based on task difficulty: Hard=10, Medium=5, Easy=3',
            'discount_factor': 0.9,
            'optimal_policy': f'Follow the sequential plan from Day 1 to Day {len(plan)}'
        }
    
    def _generate_htn_details(self, plan: List[Dict], category: str, name: str) -> Dict:
        """Generate HTN (Hierarchical Task Network) details."""
        # Group plan into hierarchical milestones
        milestones = []
        
        # Extract unique phase types
        phase_types = {}
        for phase in plan:
            phase_name = phase['phase'].split(':')[1].strip().split('-')[0].strip() if ':' in phase['phase'] else 'Work'
            if phase_name not in phase_types:
                phase_types[phase_name] = []
            phase_types[phase_name].append(phase)
        
        # Create milestone hierarchy
        for milestone_name, phases in phase_types.items():
            tasks = []
            for phase in phases:
                tasks.append({
                    'name': phase['phase'],
                    'subtasks': phase['tasks'],
                    'effort_hours': phase['hours'],
                    'skills_required': self._infer_skills(phase)
                })
            
            milestones.append({
                'milestone': milestone_name,
                'description': f'Complete all {milestone_name.lower()} activities',
                'task_count': len(tasks),
                'tasks': tasks
            })
        
        return {
            'description': 'HTN decomposes the high-level goal into hierarchical milestones and tasks',
            'goal': f'Complete {name}',
            'total_milestones': len(milestones),
            'milestones': milestones,
            'decomposition_method': 'Top-down goal decomposition with task dependencies',
            'task_dependencies': 'Sequential with some parallel opportunities within milestones'
        }
    
    def _infer_skills(self, phase: Dict) -> List[str]:
        """Infer required skills from phase."""
        difficulty = phase['difficulty']
        phase_name = phase['phase'].lower()
        
        skills = []
        if 'foundation' in phase_name or 'review' in phase_name:
            skills = ['Reading', 'Note-taking', 'Comprehension']
        elif 'theory' in phase_name or 'learning' in phase_name:
            skills = ['Analysis', 'Critical thinking', 'Memory']
        elif 'practice' in phase_name or 'problem' in phase_name:
            skills = ['Problem-solving', 'Application', 'Practice']
        elif 'planning' in phase_name or 'design' in phase_name:
            skills = ['Planning', 'Design', 'Organization']
        elif 'implementation' in phase_name or 'coding' in phase_name:
            skills = ['Coding', 'Implementation', 'Debugging']
        elif 'testing' in phase_name:
            skills = ['Testing', 'Quality assurance', 'Debugging']
        else:
            skills = ['General', 'Organization', 'Execution']
        
        return skills

planner = WebPlanner()

@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_planning():
    """Start a new planning session."""
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    session['answers'] = {}
    session['question_index'] = 0
    
    # Get first question
    questions = planner.get_question_flow()
    
    return jsonify({
        'session_id': session_id,
        'question': questions[0],
        'question_index': 0,
        'total_questions': 1  # Initially we don't know total
    })

@app.route('/api/answer', methods=['POST'])
def submit_answer():
    """Submit answer and get next question."""
    data = request.json
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    # Store answer
    if 'answers' not in session:
        session['answers'] = {}
    session['answers'][question_id] = answer
    session.modified = True
    
    # Determine next question
    answers = session['answers']
    category = answers.get('category')
    
    # Get appropriate question flow
    questions = planner.get_question_flow(category)
    
    # Find current question index
    current_index = next((i for i, q in enumerate(questions) if q['id'] == question_id), -1)
    next_index = current_index + 1
    
    if next_index < len(questions):
        # More questions
        return jsonify({
            'question': questions[next_index],
            'question_index': next_index,
            'total_questions': len(questions),
            'complete': False
        })
    else:
        # Planning complete, generate plan
        plan_result = planner.create_plan(answers)
        session['plan'] = plan_result
        session.modified = True
        
        return jsonify({
            'complete': True,
            'plan': plan_result
        })

@app.route('/api/plan', methods=['GET'])
def get_plan():
    """Get the generated plan."""
    plan = session.get('plan')
    if not plan:
        return jsonify({'error': 'No plan found'}), 404
    
    return jsonify(plan)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
