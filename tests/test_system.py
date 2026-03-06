"""Unit tests for the planning system."""

import pytest
from datetime import datetime, timedelta

from src.models import Constraint, ConstraintType, Task, TaskStatus
from src.input_capture import InputCapture
from src.knowledge_graph import KnowledgeGraph
from src.planner import HTNPlanner, MDPScheduler, Planner
from src.retriever import SemanticRetriever, ConstraintFilter, Retriever
from src.executor import ActionExecutor
from src.models import Action, ActionType


class TestInputCapture:
    """Test input capture functionality."""
    
    def test_parse_simple_input(self):
        """Test basic input parsing."""
        ic = InputCapture()
        result = ic.parse_input(
            goal="Complete course by 2026-05-15",
            hard_constraints={"deadline": "2026-05-15"},
            soft_constraints={"max_hours": 10}
        )
        
        assert result["goal"] == "Complete course by 2026-05-15."
        assert len(result["constraints"]) >= 2
        assert result["metadata"]["raw_goal"] == "Complete course by 2026-05-15"
    
    def test_extract_implicit_constraints(self):
        """Test extraction of constraints from goal text."""
        ic = InputCapture()
        result = ic.parse_input(
            goal="Finish project by 2026-06-01"
        )
        
        # Should extract implicit deadline
        constraint_keys = [c.key for c in result["constraints"]]
        assert any("deadline" in key for key in constraint_keys)


class TestKnowledgeGraph:
    """Test knowledge graph functionality."""
    
    def test_create_kg(self):
        """Test KG creation."""
        kg = KnowledgeGraph("test_user")
        assert kg.user_id == "test_user"
        assert kg.graph.number_of_nodes() == 0
    
    def test_add_entity(self):
        """Test adding entities."""
        kg = KnowledgeGraph("test_user")
        kg.add_entity(
            entity_id="task_1",
            entity_type="task",
            properties={"name": "Study algorithms"}
        )
        
        assert kg.graph.number_of_nodes() == 1
        
        entity = kg.get_entity("task_1")
        assert entity is not None
        assert entity["type"] == "task"
        assert entity["properties"]["name"] == "Study algorithms"
    
    def test_add_relationship(self):
        """Test adding relationships."""
        kg = KnowledgeGraph("test_user")
        kg.add_entity("task_1", "task", {"name": "Task 1"})
        kg.add_entity("task_2", "task", {"name": "Task 2"})
        kg.add_relationship("task_1", "task_2", "prerequisite")
        
        assert kg.graph.number_of_edges() == 1
        
        related = kg.get_related_entities("task_1", relationship_type="prerequisite")
        assert len(related) == 1
        assert related[0]["id"] == "task_2"


class TestPlanner:
    """Test planning functionality."""
    
    def test_htn_decomposition(self):
        """Test HTN decomposition."""
        kg = KnowledgeGraph("test_user")
        planner = HTNPlanner(kg)
        
        constraints = [
            Constraint(type=ConstraintType.HARD, key="deadline", value="2026-06-01")
        ]
        
        milestones, tasks = planner.decompose_goal(
            "Complete Data Structures course",
            constraints
        )
        
        assert len(milestones) > 0
        assert len(tasks) > 0
        
        # Check that tasks are linked to milestones
        task_ids = set(t.id for t in tasks)
        milestone_task_ids = set()
        for m in milestones:
            milestone_task_ids.update(m.tasks)
        
        assert task_ids == milestone_task_ids
    
    def test_mdp_scheduler(self):
        """Test MDP scheduling."""
        scheduler = MDPScheduler()
        
        tasks = [
            Task(
                name="Task 1",
                description="First task",
                effort_hours=5.0,
                earliest_start=datetime.now()
            ),
            Task(
                name="Task 2",
                description="Second task",
                effort_hours=8.0,
                dependencies=[]
            )
        ]
        
        constraints = [
            Constraint(type=ConstraintType.HARD, key="deadline", value="2026-06-01")
        ]
        
        result = scheduler.schedule(tasks, constraints)
        
        assert "task_schedule" in result
        assert "confidence_score" in result
        assert 0.0 <= result["confidence_score"] <= 1.0


class TestRetriever:
    """Test retrieval functionality."""
    
    def test_semantic_search(self):
        """Test semantic search."""
        retriever = SemanticRetriever()
        
        # Index documents
        retriever.index_document(
            "doc1",
            "Python programming tutorial for beginners",
            {"source_type": "web"}
        )
        retriever.index_document(
            "doc2",
            "Advanced Python: decorators and generators",
            {"source_type": "web"}
        )
        
        # Search
        results = retriever.search("Python tutorial", top_k=2)
        
        assert len(results) <= 2
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
    
    def test_constraint_filter(self):
        """Test constraint filtering."""
        cf = ConstraintFilter()
        
        documents = {
            "doc1": {
                "content": "Test content",
                "metadata": {"source_type": "user_documents", "course": "CS101"},
                "indexed_at": datetime.now().isoformat()
            }
        }
        
        candidates = [("doc1", 0.9)]
        
        # Filter with matching constraint
        results = cf.filter_and_score(
            candidates,
            documents,
            constraints={"course": "CS101"}
        )
        
        assert len(results) == 1
        assert results[0].evidence_score > 0
        
        # Filter with non-matching constraint
        results = cf.filter_and_score(
            candidates,
            documents,
            constraints={"course": "CS202"}
        )
        
        assert len(results) == 0


class TestExecutor:
    """Test action execution."""
    
    def test_soft_action_execution(self):
        """Test execution of soft action."""
        executor = ActionExecutor()
        
        action = Action(
            type=ActionType.SOFT,
            task_id="task_1",
            description="generate_content",
            parameters={"type": "study_plan"}
        )
        
        result = executor.execute_action(action, dry_run=False)
        
        assert result["status"] == "success"
        assert "execution" in result
    
    def test_hard_action_dry_run(self):
        """Test dry run for hard action."""
        executor = ActionExecutor()
        
        action = Action(
            type=ActionType.HARD,
            task_id="task_1",
            description="create_calendar_event",
            parameters={
                "title": "Study Session",
                "start": datetime.now().isoformat(),
                "end": (datetime.now() + timedelta(hours=2)).isoformat()
            },
            preconditions=["calendar_slot_available"]
        )
        
        result = executor.execute_action(action, dry_run=True)
        
        assert "execution" in result
        assert result["execution"]["simulated"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
