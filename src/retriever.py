"""Two-stage retrieval pipeline with evidence scoring."""

import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from src.models import Evidence, Task
from src.knowledge_graph import KnowledgeGraph


class SemanticRetriever:
    """
    Fast semantic search using embeddings and cosine similarity.
    In production, would use sentence-transformers or similar.
    """
    
    def __init__(self):
        # Simulated document store
        self.documents = {}
        self.embeddings = {}
    
    def index_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Index a document for semantic search."""
        self.documents[doc_id] = {
            "content": content,
            "metadata": metadata,
            "indexed_at": datetime.now().isoformat()
        }
        # Simplified embedding (in production: use sentence-transformers)
        self.embeddings[doc_id] = self._simple_embed(content)
    
    def search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Semantic search for documents.
        
        Returns:
            List of (doc_id, relevance_score) tuples
        """
        if not self.embeddings:
            return []
        
        # Compute query embedding
        query_embedding = self._simple_embed(query)
        
        # Compute similarities
        similarities = []
        for doc_id, doc_embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((doc_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def _simple_embed(self, text: str) -> np.ndarray:
        """
        Simplified embedding for prototype.
        In production: use sentence-transformers.
        """
        # Simple word-based embedding
        words = text.lower().split()
        # Use hash-based features for simplicity
        vocab_size = 1000
        embedding = np.zeros(vocab_size)
        for word in words:
            idx = hash(word) % vocab_size
            embedding[idx] += 1
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = np.dot(a, b)
        return float(dot_product)


class ConstraintFilter:
    """
    Symbolic constraint filtering and evidence scoring.
    Second stage of the retrieval pipeline.
    """
    
    def __init__(self):
        self.trust_scores = defaultdict(lambda: 0.5)  # Default trust
        # Configure trust scores for different sources
        self.trust_scores.update({
            "user_documents": 1.0,
            "knowledge_graph": 0.95,
            "institutional_api": 0.9,
            "web": 0.6
        })
    
    def filter_and_score(
        self,
        candidates: List[Tuple[str, float]],
        documents: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[Evidence]:
        """
        Apply symbolic constraints and compute evidence scores.
        
        Args:
            candidates: List of (doc_id, relevance_score) from semantic search
            documents: Document metadata store
            constraints: Optional filtering constraints
        
        Returns:
            List of Evidence objects with combined scores
        """
        evidence_list = []
        
        for doc_id, relevance_score in candidates:
            if doc_id not in documents:
                continue
            
            doc = documents[doc_id]
            
            # Apply constraint filters
            if constraints and not self._satisfies_constraints(doc, constraints):
                continue
            
            # Compute trust score
            source_type = doc.get("metadata", {}).get("source_type", "unknown")
            trust_score = self.trust_scores.get(source_type, 0.5)
            
            # Compute recency score
            recency_score = self._compute_recency(doc)
            
            # Create evidence object
            evidence = Evidence(
                source=doc_id,
                content=doc.get("content", ""),
                relevance_score=relevance_score,
                trust_score=trust_score,
                recency_score=recency_score
            )
            
            evidence_list.append(evidence)
        
        # Sort by evidence score
        evidence_list.sort(key=lambda e: e.evidence_score, reverse=True)
        
        return evidence_list
    
    def _satisfies_constraints(
        self,
        doc: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> bool:
        """Check if document satisfies symbolic constraints."""
        metadata = doc.get("metadata", {})
        
        for key, value in constraints.items():
            if key in metadata:
                if metadata[key] != value:
                    return False
        
        return True
    
    def _compute_recency(self, doc: Dict[str, Any]) -> float:
        """
        Compute recency score (1.0 for recent, decays over time).
        """
        indexed_at_str = doc.get("indexed_at")
        if not indexed_at_str:
            return 0.5  # Unknown age
        
        try:
            indexed_at = datetime.fromisoformat(indexed_at_str)
            age_days = (datetime.now() - indexed_at).days
            
            # Exponential decay: half-life of 30 days
            decay_factor = 0.5 ** (age_days / 30.0)
            return max(0.1, min(1.0, decay_factor))
        except:
            return 0.5


class Retriever:
    """
    Two-stage retrieval pipeline orchestrator.
    Combines semantic search with constraint filtering and evidence scoring.
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        self.semantic_retriever = SemanticRetriever()
        self.constraint_filter = ConstraintFilter()
    
    def index_resources(self, resources: List[Dict[str, Any]]) -> None:
        """Index resources for retrieval."""
        for resource in resources:
            self.semantic_retriever.index_document(
                doc_id=resource["id"],
                content=resource["content"],
                metadata=resource.get("metadata", {})
            )
    
    def retrieve_for_task(
        self,
        task: Task,
        constraints: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Evidence]:
        """
        Retrieve relevant resources for a task.
        
        Search order:
        1. Knowledge graph
        2. Personal documents
        3. Institutional APIs (simulated)
        4. Web (simulated, when allowed)
        
        Returns:
            Ranked list of Evidence objects
        """
        # Build query from task
        query = f"{task.name} {task.description} {' '.join(task.skills_required)}"
        
        # Stage 1: Semantic search
        # Search knowledge graph first
        kg_results = self._search_knowledge_graph(task)
        
        # Search document store
        doc_results = self.semantic_retriever.search(query, top_k=top_k * 2)
        
        # Combine results
        all_candidates = doc_results  # KG results integrated separately
        
        # Stage 2: Constraint filtering and evidence scoring
        evidence_list = self.constraint_filter.filter_and_score(
            candidates=all_candidates,
            documents=self.semantic_retriever.documents,
            constraints=constraints
        )
        
        # Add KG evidence
        kg_evidence = self._kg_results_to_evidence(kg_results)
        evidence_list.extend(kg_evidence)
        
        # Re-sort by evidence score
        evidence_list.sort(key=lambda e: e.evidence_score, reverse=True)
        
        return evidence_list[:top_k]
    
    def retrieve_for_tasks(
        self,
        tasks: List[Task],
        constraints: Optional[Dict[str, Any]] = None,
        top_k: int = 3
    ) -> Dict[str, List[Evidence]]:
        """Retrieve resources for multiple tasks."""
        results = {}
        for task in tasks:
            results[task.id] = self.retrieve_for_task(
                task,
                constraints=constraints,
                top_k=top_k
            )
        return results
    
    def _search_knowledge_graph(self, task: Task) -> List[Dict[str, Any]]:
        """Search for relevant entities in knowledge graph."""
        # Look for related resources, concepts, or prerequisites
        results = []
        
        # Query by skills required
        for skill in task.skills_required:
            entities = self.kg.query_by_property("skill", skill)
            results.extend(entities)
        
        # Query by task type
        task_type_entities = self.kg.query_by_property("task_type", task.name.lower())
        results.extend(task_type_entities)
        
        return results
    
    def _kg_results_to_evidence(self, kg_results: List[Dict[str, Any]]) -> List[Evidence]:
        """Convert KG entities to Evidence objects."""
        evidence_list = []
        
        for entity in kg_results:
            # KG results have high trust
            content = str(entity.get("properties", {}))
            evidence = Evidence(
                source=f"kg_{entity['id']}",
                content=content,
                relevance_score=0.8,  # High relevance from KG
                trust_score=0.95,     # High trust in KG
                recency_score=0.9     # Assume relatively current
            )
            evidence_list.append(evidence)
        
        return evidence_list
