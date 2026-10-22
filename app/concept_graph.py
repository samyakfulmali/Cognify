import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import networkx as nx

from app.config import CONCEPTS_PATH


class ConceptGraph:
    """
    Manages the math concept curriculum graph using NetworkX.
    Nodes represent concepts; directed edges (A -> B) signify that A is a prerequisite for B.
    """

    def __init__(self, concepts_file: Optional[Path] = None):
        self.concepts_file = concepts_file or CONCEPTS_PATH
        self.graph = nx.DiGraph()
        self.concepts_data: Dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        """Loads concepts from JSON file and builds the NetworkX DiGraph."""
        if not self.concepts_file.exists():
            raise FileNotFoundError(f"Concepts file not found at {self.concepts_file}")

        with open(self.concepts_file, "r", encoding="utf-8") as f:
            concepts_list = json.load(f)

        self.graph.clear()
        self.concepts_data.clear()

        # Add all nodes
        for item in concepts_list:
            cid = item["id"]
            self.concepts_data[cid] = item
            self.graph.add_node(
                cid,
                name=item["name"],
                description=item["description"],
                category=item.get("category", "General"),
                difficulty=item.get("difficulty", 1),
                prerequisites=item.get("prerequisites", []),
            )

        # Add prerequisite edges: prereq -> concept
        for item in concepts_list:
            cid = item["id"]
            for prereq in item.get("prerequisites", []):
                if prereq in self.concepts_data:
                    self.graph.add_edge(prereq, cid)
                else:
                    raise ValueError(
                        f"Prerequisite '{prereq}' declared by '{cid}' does not exist."
                    )

        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            raise ValueError(f"Concept graph contains cycles! Cycles: {cycles}")

    @property
    def concepts(self) -> Dict[str, dict]:
        """Provides backward-compatible dictionary of concepts."""
        return self.concepts_data

    def get_concept(self, concept_id: str) -> Optional[dict]:
        """Returns concept metadata for a given concept ID."""
        return self.concepts_data.get(concept_id)

    def get_all_concepts(self) -> List[dict]:
        """Returns list of all concepts in topological order."""
        topo_order = self.topological_order()
        return [self.concepts_data[cid] for cid in topo_order]

    def get_direct_prerequisites(self, concept_id: str) -> List[str]:
        """Returns direct prerequisites (in-edges) for concept_id."""
        if concept_id not in self.graph:
            return []
        return list(self.graph.predecessors(concept_id))

    def get_all_ancestors(self, concept_id: str) -> Set[str]:
        """Returns all transitive prerequisites (both direct and indirect)."""
        if concept_id not in self.graph:
            return set()
        return nx.ancestors(self.graph, concept_id)

    def get_direct_dependents(self, concept_id: str) -> List[str]:
        """Returns concepts that directly depend on concept_id (out-edges)."""
        if concept_id not in self.graph:
            return []
        return list(self.graph.successors(concept_id))

    def get_all_descendants(self, concept_id: str) -> Set[str]:
        """Returns all transitive downstream concepts that require concept_id."""
        if concept_id not in self.graph:
            return set()
        return nx.descendants(self.graph, concept_id)

    def topological_order(self) -> List[str]:
        """Returns concepts ordered from most foundational to most advanced."""
        return list(nx.topological_sort(self.graph))

    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Finds shortest prerequisite path from source to target if one exists."""
        try:
            return nx.shortest_path(self.graph, source=source, target=target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def export_graph_summary(self) -> dict:
        """Returns graph node & edge list suitable for frontend visualization."""
        nodes = []
        for cid in self.topological_order():
            data = self.concepts_data[cid]
            nodes.append({
                "id": cid,
                "name": data["name"],
                "category": data.get("category", "General"),
                "difficulty": data.get("difficulty", 1),
                "prerequisites": data.get("prerequisites", []),
            })

        edges = [{"source": u, "target": v} for u, v in self.graph.edges()]
        return {"nodes": nodes, "edges": edges}


# Singleton instance
concept_graph = ConceptGraph()
