import networkx as nx
import pytest
from app.concept_graph import ConceptGraph
from app.gap_detector import RootGapDetector


@pytest.fixture
def graph():
    return ConceptGraph()


@pytest.fixture
def detector(graph):
    return RootGapDetector(graph=graph)


def test_concept_graph_is_dag(graph):
    """The concept curriculum must be a Directed Acyclic Graph with no circular dependencies."""
    assert nx.is_directed_acyclic_graph(graph.graph)
    assert len(graph.concepts_data) >= 15
    
    topo = graph.topological_order()
    assert len(topo) == len(graph.concepts_data)
    
    # Foundational concepts must precede advanced downstream concepts
    assert topo.index("fractions_basics") < topo.index("fraction_addition")
    assert topo.index("negative_numbers") < topo.index("linear_inequalities")
    assert topo.index("distributive_property") < topo.index("multi_step_equations")


def test_foundational_concept_gap(detector):
    """A concept with no prerequisites detected as self-foundational if below threshold."""
    student_mastery = {"fractions_basics": 0.25}
    gap = detector.detect_root_gap("fractions_basics", student_mastery)
    
    assert gap is not None
    assert gap["root_gap_found"] is True
    assert gap["is_foundational"] is True
    assert gap["root_concept_id"] == "fractions_basics"
    assert gap["prerequisite_chain"] == ["fractions_basics"]


def test_single_prerequisite_gap(detector):
    """Failing fraction_addition with weak common_denominators identifies common_denominators."""
    student_mastery = {
        "fractions_basics": 0.90,
        "equivalent_fractions": 0.85,
        "common_denominators": 0.22,  # Root gap
        "fraction_addition": 0.20,
    }
    
    gap = detector.detect_root_gap("fraction_addition", student_mastery)
    assert gap is not None
    assert gap["root_gap_found"] is True
    assert gap["is_foundational"] is False
    assert gap["root_concept_id"] == "common_denominators"
    assert "common_denominators" in gap["prerequisite_chain"]
    assert gap["failed_concept_id"] == "fraction_addition"


def test_multi_hop_prerequisite_gap(detector):
    """
    Traversing multi-hop ancestors:
    multi_step_equations depends on two_step_equations -> one_step_equations_mult -> fraction_division.
    If fraction_division is the weakest link, it should be isolated.
    """
    student_mastery = {
        "fractions_basics": 0.90,
        "fraction_multiplication": 0.88,
        "fraction_division": 0.18,      # Weakest ancestor
        "one_step_equations_add": 0.82,
        "one_step_equations_mult": 0.70,
        "combining_like_terms": 0.85,
        "distributive_property": 0.80,
        "two_step_equations": 0.65,
        "multi_step_equations": 0.20,
    }

    gap = detector.detect_root_gap("multi_step_equations", student_mastery)
    assert gap is not None
    assert gap["root_gap_found"] is True
    assert gap["root_concept_id"] == "fraction_division"
    assert gap["p_known"] == 0.18
    # Prerequisite chain must trace path from root gap to multi_step_equations
    assert gap["prerequisite_chain"][0] == "fraction_division"
    assert gap["prerequisite_chain"][-1] == "multi_step_equations"


def test_branch_prerequisite_isolation(detector):
    """
    two_step_equations requires both one_step_equations_mult AND combining_like_terms.
    If one_step is mastered but combining_like_terms is weak, combining_like_terms is identified.
    """
    student_mastery = {
        "negative_numbers": 0.85,
        "order_of_operations": 0.85,
        "variables_expressions": 0.80,
        "combining_like_terms": 0.15,      # Weak branch
        "fractions_basics": 0.90,
        "fraction_multiplication": 0.88,
        "fraction_division": 0.85,
        "one_step_equations_add": 0.88,
        "one_step_equations_mult": 0.86,   # Strong branch
        "two_step_equations": 0.30,
    }

    gap = detector.detect_root_gap("two_step_equations", student_mastery)
    assert gap is not None
    assert gap["root_concept_id"] == "combining_like_terms"
    assert gap["p_known"] == 0.15


def test_no_gap_when_all_prerequisites_mastered(detector):
    """When all ancestors have high mastery, no prerequisite gap is reported."""
    student_mastery = {
        "fractions_basics": 0.95,
        "equivalent_fractions": 0.92,
        "common_denominators": 0.90,
        "fraction_addition": 0.40,  # Currently learning
    }

    gap = detector.detect_root_gap("fraction_addition", student_mastery)
    assert gap is None
