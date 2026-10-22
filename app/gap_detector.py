from typing import Dict, List, Optional
from app.config import BKT_P_INIT, MASTERY_THRESHOLD, WEAK_PREREQUISITE_THRESHOLD
from app.concept_graph import ConceptGraph, concept_graph as default_graph


class RootGapDetector:
    """
    Detects underlying learning gaps by walking back through the concept prerequisite DAG.
    When a student fails or struggles with a concept, identifies the weakest ancestor prerequisite.
    """

    def __init__(self, graph: Optional[ConceptGraph] = None):
        self.graph = graph or default_graph

    def detect_root_gap(
        self,
        concept_id: str,
        student_mastery: Dict[str, float],
        weak_threshold: float = WEAK_PREREQUISITE_THRESHOLD,
    ) -> Optional[dict]:
        """
        Walks back through prerequisites of concept_id and detects the weakest root gap.
        
        Returns:
            Dict containing root gap diagnosis or None if no prerequisite gap exists.
        """
        current_concept = self.graph.get_concept(concept_id)
        if not current_concept:
            return None

        ancestors = self.graph.get_all_ancestors(concept_id)

        # Case 1: Concept is a foundational root concept (no prerequisites)
        if not ancestors:
            current_p = student_mastery.get(concept_id, BKT_P_INIT)
            if current_p < weak_threshold:
                return {
                    "root_gap_found": True,
                    "is_foundational": True,
                    "root_concept_id": concept_id,
                    "root_concept_name": current_concept["name"],
                    "p_known": round(current_p, 4),
                    "failed_concept_id": concept_id,
                    "failed_concept_name": current_concept["name"],
                    "prerequisite_chain": [concept_id],
                    "unmastered_ancestors": [],
                    "message": (
                        f"Foundational gap detected in '{current_concept['name']}' "
                        f"(Mastery: {round(current_p * 100, 1)}%). This concept has no prior prerequisites "
                        f"and represents a core foundational skill requiring focused reinforcement."
                    ),
                }
            return None

        # Case 2: Concept has prerequisites in the DAG
        ancestor_scores = []
        unmastered_ancestors = []

        for anc in ancestors:
            anc_concept = self.graph.get_concept(anc)
            anc_name = anc_concept["name"] if anc_concept else anc
            anc_p = student_mastery.get(anc, BKT_P_INIT)
            item = {
                "concept_id": anc,
                "concept_name": anc_name,
                "p_known": round(anc_p, 4),
                "is_weak": anc_p < weak_threshold,
            }
            ancestor_scores.append(item)
            if anc_p < weak_threshold:
                unmastered_ancestors.append(item)

        # If all ancestors are satisfactorily mastered, the issue is not a prerequisite root gap
        if not unmastered_ancestors:
            return None

        # Sort unmastered ancestors to find the weakest one.
        # Tie-breaker: prefer ancestors that are deeper/earlier in topological order (more foundational)
        topo_order = {cid: idx for idx, cid in enumerate(self.graph.topological_order())}
        unmastered_ancestors.sort(
            key=lambda x: (x["p_known"], topo_order.get(x["concept_id"], 999))
        )
        weakest = unmastered_ancestors[0]
        weakest_id = weakest["concept_id"]

        # Calculate prerequisite pathway from the weakest root gap to the failed concept
        chain = self.graph.find_path(weakest_id, concept_id) or [weakest_id, concept_id]

        failed_p = student_mastery.get(concept_id, BKT_P_INIT)
        return {
            "root_gap_found": True,
            "is_foundational": False,
            "root_concept_id": weakest_id,
            "root_concept_name": weakest["concept_name"],
            "p_known": round(weakest["p_known"], 4),
            "failed_concept_id": concept_id,
            "failed_concept_name": current_concept["name"],
            "prerequisite_chain": chain,
            "unmastered_ancestors": unmastered_ancestors,
            "message": (
                f"Root learning gap detected in prerequisite '{weakest['concept_name']}' "
                f"(Mastery: {round(weakest['p_known'] * 100, 1)}%). Before mastering "
                f"'{current_concept['name']}' (Mastery: {round(failed_p * 100, 1)}%), the student "
                f"must address gaps in '{weakest['concept_name']}' along the pathway: "
                f"{' -> '.join([self.graph.get_concept(c)['name'] for c in chain])}."
            ),
        }


# Singleton instance
gap_detector = RootGapDetector()
