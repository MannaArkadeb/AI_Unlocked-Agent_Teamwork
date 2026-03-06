# Planning Master

An intelligent planning system with web and terminal interfaces that creates personalized study plans, project schedules, and semester calendars using advanced MDP (Markov Decision Process) and HTN (Hierarchical Task Network) algorithms.

## Features

### 🌐 Web Interface
- **Interactive Planning**: Question-by-question workflow with real-time chat interface
- **Three Planning Types**: Study plans, project timelines, and semester planning
- **Visual Design**: Modern gradient background with floating decorative animations
- **Export Options**: 
  - Download plans as PDF
  - Export to calendar (.ics format compatible with Google Calendar, Outlook, Apple Calendar)
- **Technical Details**: Expandable MDP and HTN algorithm explanations
- **Session Management**: Start new plans with a single click

### 💻 Terminal Interface
- **Interactive CLI**: Command-line planning tool for quick access
- **Same Planning Types**: Study, project, and semester planning available
- **Professional Output**: Clean, structured output with detailed breakdowns
- **No Dependencies**: Works without browser or GUI

### 📋 Planning Types

#### 1. Study Planning
Create detailed study schedules for exams or courses:
- Subject and exam date
- Total days and hours per day
- Day-by-day task breakdown
- Difficulty progression (Introduction → Practice → Revision → Final Review)
- Realistic phase distribution

#### 2. Project Planning
Organize project work with milestone-based structure:
- Project goals and deadline
- Total days and hours per day
- Phase-based breakdown (Research → Planning → Development → Testing → Finalization)
- Task allocation with priority levels
- Progress tracking timeline

#### 3. Semester Planning
Plan entire semesters with multiple exam dates:
- Up to 5 exam subjects with individual dates
- Hours per day commitment
- Week-by-week study schedule
- Automatic time distribution based on exam proximity
- Balanced workload across subjects

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd AI_Unlocked
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies
- **Flask** (≥3.0.0): Web framework
- **NetworkX**: Graph algorithms for planning
- **NumPy**: Numerical computations
- **SciPy**: Scientific computing for MDP
- **Sentence-Transformers**: Semantic retrieval
- **SQLAlchemy**: Database management
- **Pydantic**: Data validation
- **python-dateutil**: Date parsing
- **iCalendar**: Calendar file generation
- **pytest**: Testing framework

## Usage

### Web Application (Recommended)

#### Windows:
```bash
start_web_app.bat
```

#### Mac/Linux:
```bash
python app.py
```

Then open your browser to: `http://localhost:5000`

**How to Use:**
1. Select planning type (Study, Project, or Semester)
2. Answer questions one by one
3. View your personalized plan
4. Click "Show MDP & HTN Details" to see algorithm explanations
5. Download as PDF or add to calendar
6. Click "Start New Plan" to create another

### Terminal Application

```bash
python examples/interactive_planner.py
```

**How to Use:**
1. Choose planning category (1: Study, 2: Project, 3: Semester)
2. Provide required information when prompted
3. View detailed plan in terminal
4. Plan is automatically saved to audit logs

### Other Examples

```bash
# Simple hardcoded example
python examples/simple_example.py

# Advanced features demo
python examples/advanced_example.py

# Full system demo
python demo.py
```

## Technology Stack

### Backend
- **Flask 3.1.3**: Lightweight WSGI web framework
- **Python 3.8+**: Core programming language
- **Session-based State Management**: Server-side session storage

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients, animations, flexbox, and grid
- **Vanilla JavaScript**: Client-side logic with async/await
- **jsPDF 2.5.1**: PDF generation library (CDN)

### Algorithms
- **MDP (Markov Decision Process)**: Probabilistic planning with state transitions
- **HTN (Hierarchical Task Network)**: Task decomposition and scheduling
- **datetime/timedelta**: Date calculations and scheduling

## File Structure

```
AI_Unlocked/
│
├── app.py                          # Flask web application
├── start_web_app.bat              # Windows launcher
├── requirements.txt               # Python dependencies
├── demo.py                        # System demo
├── README.md                      # This file
│
├── templates/
│   └── index.html                 # Web interface UI
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # Core planning system
│   ├── planner.py                 # HTN and MDP algorithms
│   ├── executor.py                # Task execution engine
│   ├── knowledge_graph.py         # Context management
│   ├── retriever.py               # Information retrieval
│   ├── negotiation.py             # Human-in-the-loop approval
│   ├── learning.py                # Feedback adaptation
│   ├── audit.py                   # Event logging
│   ├── input_capture.py           # User input normalization
│   └── models.py                  # Data models
│
├── examples/
│   ├── interactive_planner.py     # Terminal planning tool
│   ├── simple_example.py          # Basic usage example
│   ├── advanced_example.py        # Advanced features demo
│   └── test_realistic_planner.py  # Testing script
│
├── tests/
│   ├── __init__.py
│   └── test_system.py             # System tests
│
└── audit_logs/                    # User planning history
    └── [user_id]/
        └── audit.jsonl            # JSONL audit trail
```

## Planning Algorithms

### MDP (Markov Decision Process)

The MDP algorithm treats planning as a probabilistic decision-making problem:

- **States**: Different phases of the plan (e.g., Introduction, Practice, Revision)
- **Actions**: Choosing which tasks to schedule
- **Transitions**: Probability of moving between phases
- **Rewards**: Optimizing for completion likelihood and learning efficiency
- **Value Iteration**: Computing optimal task scheduling

**Benefits:**
- Adapts to uncertainty in task completion
- Optimizes for long-term success
- Handles probabilistic constraints

### HTN (Hierarchical Task Network)

The HTN algorithm decomposes high-level goals into actionable subtasks:

- **Compound Tasks**: High-level objectives (e.g., "Master subject")
- **Primitive Tasks**: Specific actions (e.g., "Read Chapter 3")
- **Methods**: Decomposition rules for breaking down tasks
- **Preconditions**: Requirements for task execution
- **Effects**: Outcomes of completed tasks

**Benefits:**
- Structured task breakdown
- Maintains logical dependencies
- Ensures prerequisite completion

### Integration

Both algorithms work together:
1. **HTN** decomposes goals into task hierarchies
2. **MDP** optimizes task scheduling and resource allocation
3. Result: Realistic, achievable plans with logical structure

## Export Features

### PDF Export
- Click "Download as PDF" button
- Generates formatted document with:
  - Plan title and creation date
  - Complete task breakdown
  - Day-by-day or week-by-week schedule
  - Professional formatting

### Calendar Export
- Click "Add to Calendar" button
- Downloads `.ics` file compatible with:
  - Google Calendar
  - Microsoft Outlook
  - Apple Calendar
  - Any iCalendar-compatible application
- Each task becomes a calendar event with:
  - Task description
  - Start and end times
  - Automatic scheduling based on plan

## Core Components

### 1. Input Capture (`src/input_capture.py`)
Normalizes user goals, constraints, and external information into structured format.

### 2. Knowledge Graph (`src/knowledge_graph.py`)
Maintains user-specific context, preferences, and historical planning data.

### 3. Planner (`src/planner.py`)
Implements HTN decomposition and MDP-based probabilistic scheduling algorithms.

### 4. Retriever (`src/retriever.py`)
Two-stage retrieval system with semantic search and evidence scoring.

### 5. Executor (`src/executor.py`)
Verifiable action engine with preconditions and postconditions validation.

### 6. Negotiation (`src/negotiation.py`)
Human-in-the-loop approval workflow for plan modifications.

### 7. Learning (`src/learning.py`)
Feedback-driven adaptation based on plan execution success.

### 8. Audit (`src/audit.py`)
Append-only event logging with privacy controls and JSONL format.

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific tests:
```bash
python -m pytest tests/test_system.py -v
```

## Development

### Adding New Planning Types

1. Update `get_question_flow()` in `app.py` and `interactive_planner.py`
2. Create new `_create_[type]_plan()` method in `WebPlanner` class
3. Add corresponding logic in terminal planner
4. Update frontend UI if needed

### Customizing Algorithms

- **MDP**: Modify `_generate_mdp_details()` in `app.py`
- **HTN**: Modify `_generate_htn_details()` in `app.py`
- **Core Logic**: Edit `src/planner.py` for underlying algorithms

## License

This project is a prototype implementation for educational and research purposes.

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style conventions
- Tests pass before submitting
- Documentation is updated for new features

## Support

For issues, questions, or feature requests, please open an issue in the repository.

---

**Made with Planning Master - Your Personal Planning Assistant**
