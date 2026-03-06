"""Knowledge Graph for maintaining user context and relationships."""

import networkx as nx
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
import json


class KnowledgeGraph:
    """
    Maintains user-specific knowledge graph for grounded planning.
    
    Nodes represent entities (tasks, concepts, resources, constraints).
    Edges represent relationships (prerequisite, related_to, supports).
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.graph = nx.DiGraph()
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        properties: Dict[str, Any]
    ) -> None:
        """Add or update an entity in the knowledge graph."""
        self.graph.add_node(
            entity_id,
            type=entity_type,
            properties=properties,
            created_at=datetime.now().isoformat()
        )
        self._update_timestamp()
    
    def add_relationship(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a directed relationship between entities."""
        self.graph.add_edge(
            from_id,
            to_id,
            type=relationship_type,
            properties=properties or {},
            created_at=datetime.now().isoformat()
        )
        self._update_timestamp()
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity and its properties."""
        if entity_id in self.graph:
            node_data = self.graph.nodes[entity_id]
            return {
                "id": entity_id,
                "type": node_data.get("type"),
                "properties": node_data.get("properties", {}),
                "created_at": node_data.get("created_at")
            }
        return None
    
    def get_related_entities(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "out"
    ) -> List[Dict[str, Any]]:
        """
        Get entities related to the given entity.
        
        Args:
            entity_id: The source entity
            relationship_type: Filter by relationship type
            direction: "out" for outgoing, "in" for incoming, "both" for both
        """
        related = []
        
        if entity_id not in self.graph:
            return related
        
        # Get neighbors based on direction
        if direction == "out":
            neighbors = self.graph.successors(entity_id)
        elif direction == "in":
            neighbors = self.graph.predecessors(entity_id)
        else:  # both
            neighbors = set(self.graph.successors(entity_id)) | set(self.graph.predecessors(entity_id))
        
        for neighbor_id in neighbors:
            # Check relationship type if specified
            if relationship_type:
                edge_data = self.graph.edges.get((entity_id, neighbor_id), {})
                if edge_data.get("type") != relationship_type:
                    continue
            
            entity_data = self.get_entity(neighbor_id)
            if entity_data:
                related.append(entity_data)
        
        return related
    
    def find_prerequisites(self, entity_id: str) -> List[str]:
        """Find all prerequisite entities (transitive dependencies)."""
        if entity_id not in self.graph:
            return []
        
        prerequisites = []
        for node in self.graph.predecessors(entity_id):
            edge_data = self.graph.edges.get((node, entity_id), {})
            if edge_data.get("type") == "prerequisite":
                prerequisites.append(node)
                # Recursively find prerequisites of prerequisites
                prerequisites.extend(self.find_prerequisites(node))
        
        return list(set(prerequisites))  # Remove duplicates
    
    def query_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get all entities of a specific type."""
        results = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get("type") == entity_type:
                results.append({
                    "id": node_id,
                    "type": entity_type,
                    "properties": data.get("properties", {}),
                    "created_at": data.get("created_at")
                })
        return results
    
    def query_by_property(
        self,
        property_name: str,
        property_value: Any
    ) -> List[Dict[str, Any]]:
        """Find entities with matching property value."""
        results = []
        for node_id, data in self.graph.nodes(data=True):
            properties = data.get("properties", {})
            if properties.get(property_name) == property_value:
                results.append({
                    "id": node_id,
                    "type": data.get("type"),
                    "properties": properties,
                    "created_at": data.get("created_at")
                })
        return results
    
    def get_subgraph(self, entity_ids: List[str]) -> nx.DiGraph:
        """Extract a subgraph containing specified entities and their relationships."""
        return self.graph.subgraph(entity_ids).copy()
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export the knowledge graph to a dictionary."""
        return {
            "user_id": self.user_id,
            "metadata": self.metadata,
            "nodes": [
                {
                    "id": node_id,
                    **data
                }
                for node_id, data in self.graph.nodes(data=True)
            ],
            "edges": [
                {
                    "from": u,
                    "to": v,
                    **data
                }
                for u, v, data in self.graph.edges(data=True)
            ]
        }
    
    def import_from_dict(self, data: Dict[str, Any]) -> None:
        """Import knowledge graph from a dictionary."""
        self.user_id = data["user_id"]
        self.metadata = data["metadata"]
        
        # Clear existing graph
        self.graph.clear()
        
        # Add nodes
        for node in data["nodes"]:
            node_id = node.pop("id")
            self.graph.add_node(node_id, **node)
        
        # Add edges
        for edge in data["edges"]:
            from_id = edge.pop("from")
            to_id = edge.pop("to")
            self.graph.add_edge(from_id, to_id, **edge)
    
    def _update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.metadata["last_updated"] = datetime.now().isoformat()
