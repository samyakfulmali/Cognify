"""
Curated catalog of 16 comprehensive academic subjects in Cognify,
spanning Mathematics, Humanities (English, Literature, History), Natural Sciences,
Computer Science, and Social Sciences.
"""

from typing import Dict, List

SUBJECTS_CATALOG: List[Dict[str, str]] = [
    {
        "id": "Fractions",
        "name": "Fractions & Decimals",
        "icon": "🍕",
        "category": "Mathematics",
        "description": "Fractions basics, common denominators (LCM), addition, subtraction, multiplication & division",
    },
    {
        "id": "Pre-Algebra",
        "name": "Pre-Algebra",
        "icon": "🔢",
        "category": "Mathematics",
        "description": "Negative numbers, signed integers, absolute values & PEMDAS order of operations",
    },
    {
        "id": "Algebra Basics",
        "name": "Algebra Basics",
        "icon": "📐",
        "category": "Mathematics",
        "description": "Variables, algebraic expressions, evaluating terms & combining like terms",
    },
    {
        "id": "Equations",
        "name": "Linear Equations",
        "icon": "⚖️",
        "category": "Mathematics",
        "description": "One-step, two-step, and multi-step equations with inverse operations",
    },
    {
        "id": "Inequalities",
        "name": "Linear Inequalities",
        "icon": "📊",
        "category": "Mathematics",
        "description": "Solving and graphing inequalities, sign flipping with negative numbers",
    },
    {
        "id": "English Grammar",
        "name": "English Grammar & Syntax",
        "icon": "📖",
        "category": "Humanities",
        "description": "Subject-verb agreement, clauses, sentence mechanics, and tenses",
    },
    {
        "id": "English Literature",
        "name": "English Literature & Reading",
        "icon": "✍️",
        "category": "Humanities",
        "description": "Literary devices, figurative language, themes, and reading comprehension",
    },
    {
        "id": "World History",
        "name": "World History",
        "icon": "🏛️",
        "category": "Social Studies",
        "description": "Ancient civilizations, Mesopotamia, Classical Greece, Rome, and the Silk Road",
    },
    {
        "id": "Modern History",
        "name": "Modern History & Civics",
        "icon": "🇺🇸",
        "category": "Social Studies",
        "description": "Democratic institutions, American & European revolutions, and global affairs",
    },
    {
        "id": "Physics",
        "name": "Physics (Mechanics & Energy)",
        "icon": "⚡",
        "category": "Science",
        "description": "Newton's laws of motion, velocity, acceleration, force, and energy conservation",
    },
    {
        "id": "Chemistry",
        "name": "Chemistry (Matter & Reactions)",
        "icon": "🧪",
        "category": "Science",
        "description": "Atomic structure, subatomic particles, the periodic table, and chemical bonds",
    },
    {
        "id": "Biology",
        "name": "Biology & Life Sciences",
        "icon": "🧬",
        "category": "Science",
        "description": "Cellular biology, DNA, organelles, genetics, and ecosystems",
    },
    {
        "id": "Computer Science",
        "name": "Computer Science & Python",
        "icon": "💻",
        "category": "Technology",
        "description": "Algorithms, data types, Boolean logic, functions, and Python syntax",
    },
    {
        "id": "Geography",
        "name": "World Geography & Earth Science",
        "icon": "🌍",
        "category": "Social Studies",
        "description": "Physical geography, map reading, continents, climate zones, and river systems",
    },
    {
        "id": "Economics",
        "name": "Economics & Personal Finance",
        "icon": "📈",
        "category": "Social Studies",
        "description": "Microeconomics, supply & demand, market pricing, inflation, and financial literacy",
    },
    {
        "id": "Psychology",
        "name": "Psychology & Cognitive Sciences",
        "icon": "🧠",
        "category": "Social Studies",
        "description": "Memory systems, conditioning, cognitive biases, brain anatomy, and perception",
    },
]


def get_all_subjects() -> List[Dict[str, str]]:
    """Returns the full 16-subject catalog."""
    return SUBJECTS_CATALOG


def get_subject_by_id(subject_id: str) -> Dict[str, str]:
    """Finds subject definition by id (case-insensitive)."""
    clean_id = subject_id.strip().lower()
    for s in SUBJECTS_CATALOG:
        if s["id"].lower() == clean_id or s["name"].lower() == clean_id:
            return s
    return {
        "id": subject_id,
        "name": subject_id,
        "icon": "📚",
        "category": "General",
        "description": f"Curriculum focus on {subject_id}",
    }
