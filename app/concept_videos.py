"""
Curated educational YouTube video directory and search URL generator for Cognify.
Provides high-quality, verified video tutorials for all 16 math concepts in the curriculum
from renowned channels (Math Antics, Khan Academy, Brian McLogan).
"""

import urllib.parse
from typing import Dict, Optional

CONCEPT_VIDEOS: Dict[str, dict] = {
    "fractions_basics": {
        "title": "Fractions Are Parts (Fractions Basics)",
        "channel": "Math Antics",
        "video_id": "CA9XLJpQp3c",
        "url": "https://www.youtube.com/watch?v=CA9XLJpQp3c",
        "embed_url": "https://www.youtube.com/embed/CA9XLJpQp3c",
        "search_query": "fractions basics math antics parts of a whole numerator denominator",
    },
    "equivalent_fractions": {
        "title": "Equivalent Fractions & Simplifying",
        "channel": "Math Antics",
        "video_id": "qcHHhd6H67s",
        "url": "https://www.youtube.com/watch?v=qcHHhd6H67s",
        "embed_url": "https://www.youtube.com/embed/qcHHhd6H67s",
        "search_query": "equivalent fractions simplifying math antics",
    },
    "common_denominators": {
        "title": "Finding Common Denominators (LCM)",
        "channel": "Math Antics",
        "video_id": "pZEmFSP3Z0I",
        "url": "https://www.youtube.com/watch?v=pZEmFSP3Z0I",
        "embed_url": "https://www.youtube.com/embed/pZEmFSP3Z0I",
        "search_query": "finding common denominators LCM math antics",
    },
    "fraction_addition": {
        "title": "Adding & Subtracting Fractions with Unlike Denominators",
        "channel": "Math Antics",
        "video_id": "52ZlXsFJULI",
        "url": "https://www.youtube.com/watch?v=52ZlXsFJULI",
        "embed_url": "https://www.youtube.com/embed/52ZlXsFJULI",
        "search_query": "adding subtracting fractions unlike denominators math antics",
    },
    "fraction_multiplication": {
        "title": "Multiplying Fractions - Step by Step",
        "channel": "Math Antics",
        "video_id": "qmfXyR7Z6Lk",
        "url": "https://www.youtube.com/watch?v=qmfXyR7Z6Lk",
        "embed_url": "https://www.youtube.com/embed/qmfXyR7Z6Lk",
        "search_query": "multiplying fractions step by step math antics",
    },
    "fraction_division": {
        "title": "Dividing Fractions (Keep, Change, Flip)",
        "channel": "Math Antics",
        "video_id": "4lkq3DgvmJo",
        "url": "https://www.youtube.com/watch?v=4lkq3DgvmJo",
        "embed_url": "https://www.youtube.com/embed/4lkq3DgvmJo",
        "search_query": "dividing fractions keep change flip reciprocals math antics",
    },
    "negative_numbers": {
        "title": "Negative Numbers & Integers Rules",
        "channel": "Math Antics",
        "video_id": "OAoLCXpao6s",
        "url": "https://www.youtube.com/watch?v=OAoLCXpao6s",
        "embed_url": "https://www.youtube.com/embed/OAoLCXpao6s",
        "search_query": "negative numbers and integers arithmetic rules math antics",
    },
    "order_of_operations": {
        "title": "Order of Operations (PEMDAS)",
        "channel": "Math Antics",
        "video_id": "dAgfnK528RA",
        "url": "https://www.youtube.com/watch?v=dAgfnK528RA",
        "embed_url": "https://www.youtube.com/embed/dAgfnK528RA",
        "search_query": "order of operations PEMDAS math antics",
    },
    "variables_expressions": {
        "title": "Variables & Algebraic Expressions (What is Algebra?)",
        "channel": "Math Antics",
        "video_id": "tHYis-DP0oU",
        "url": "https://www.youtube.com/watch?v=tHYis-DP0oU",
        "embed_url": "https://www.youtube.com/embed/tHYis-DP0oU",
        "search_query": "what is algebra evaluating expressions variables math antics",
    },
    "combining_like_terms": {
        "title": "Combining Like Terms in Algebra",
        "channel": "Brian McLogan / Khan Academy",
        "video_id": "CLWpkv6ccpA",
        "url": "https://www.youtube.com/watch?v=CLWpkv6ccpA",
        "embed_url": "https://www.youtube.com/embed/CLWpkv6ccpA",
        "search_query": "how to combine like terms algebra tutorial",
    },
    "one_step_equations_add": {
        "title": "Solving One-Step Equations (Addition & Subtraction)",
        "channel": "Math Antics",
        "video_id": "l3XzepN03KQ",
        "url": "https://www.youtube.com/watch?v=l3XzepN03KQ",
        "embed_url": "https://www.youtube.com/embed/l3XzepN03KQ",
        "search_query": "solving one step equations addition subtraction math antics",
    },
    "one_step_equations_mult": {
        "title": "Solving One-Step Equations (Multiplication & Division)",
        "channel": "Math Antics",
        "video_id": "Qyd_v3DGzTM",
        "url": "https://www.youtube.com/watch?v=Qyd_v3DGzTM",
        "embed_url": "https://www.youtube.com/embed/Qyd_v3DGzTM",
        "search_query": "solving one step equations multiplication division math antics",
    },
    "distributive_property": {
        "title": "The Distributive Property in Algebra",
        "channel": "Math Antics",
        "video_id": "v-6MShC82ow",
        "url": "https://www.youtube.com/watch?v=v-6MShC82ow",
        "embed_url": "https://www.youtube.com/embed/v-6MShC82ow",
        "search_query": "the distributive property in algebra math antics",
    },
    "two_step_equations": {
        "title": "Solving Two-Step Linear Equations Step by Step",
        "channel": "Math Antics",
        "video_id": "LDIiYKYvvdA",
        "url": "https://www.youtube.com/watch?v=LDIiYKYvvdA",
        "embed_url": "https://www.youtube.com/embed/LDIiYKYvvdA",
        "search_query": "solving two step equations algebra math antics",
    },
    "multi_step_equations": {
        "title": "Solving Multi-Step Equations with Variables on Both Sides",
        "channel": "Brian McLogan",
        "video_id": "1c5HY3z4k8M",
        "url": "https://www.youtube.com/watch?v=1c5HY3z4k8M",
        "embed_url": "https://www.youtube.com/embed/1c5HY3z4k8M",
        "search_query": "how to solve multi step equations variables on both sides",
    },
    "linear_inequalities": {
        "title": "Solving Linear Inequalities (When to Flip the Sign)",
        "channel": "Khan Academy",
        "video_id": "0X-bMehNhmY",
        "url": "https://www.youtube.com/watch?v=0X-bMehNhmY",
        "embed_url": "https://www.youtube.com/embed/0X-bMehNhmY",
        "search_query": "solving linear inequalities flip inequality sign negative numbers",
    },
}


def get_concept_video(concept_id: str) -> Optional[dict]:
    """Returns the curated YouTube video info for a concept, or None if not found."""
    return CONCEPT_VIDEOS.get(concept_id)


def build_youtube_search_url(concept_name: str, question_prompt: str = "") -> str:
    """
    Constructs a YouTube search URL to verify solutions and view step-by-step video explanations.
    """
    # Clean and combine prompt and concept for relevant results
    clean_prompt = question_prompt.replace("\n", " ").strip()
    if len(clean_prompt) > 80:
        clean_prompt = clean_prompt[:80]
    
    query = f"how to solve {concept_name} {clean_prompt} math step by step"
    encoded = urllib.parse.quote_plus(query.strip())
    return f"https://www.youtube.com/results?search_query={encoded}"
