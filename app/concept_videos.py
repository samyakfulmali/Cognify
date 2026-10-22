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
    "english_grammar": {
        "title": "Subject-Verb Agreement & Syntax Rules",
        "channel": "Khan Academy",
        "video_id": "0k5G6Gq1kYI",
        "url": "https://www.youtube.com/watch?v=0k5G6Gq1kYI",
        "embed_url": "https://www.youtube.com/embed/0k5G6Gq1kYI",
        "search_query": "subject verb agreement english grammar syntax tutorial",
    },
    "english_literature": {
        "title": "How and Why We Read: Crash Course Literature #1",
        "channel": "CrashCourse",
        "video_id": "MSYw502dJNY",
        "url": "https://www.youtube.com/watch?v=MSYw502dJNY",
        "embed_url": "https://www.youtube.com/embed/MSYw502dJNY",
        "search_query": "literary devices figurative language reading comprehension analysis",
    },
    "world_history": {
        "title": "The Agricultural Revolution: Crash Course World History #1",
        "channel": "CrashCourse",
        "video_id": "Yocja_N5s1I",
        "url": "https://www.youtube.com/watch?v=Yocja_N5s1I",
        "embed_url": "https://www.youtube.com/embed/Yocja_N5s1I",
        "search_query": "ancient civilizations world history crash course",
    },
    "modern_history": {
        "title": "The American Revolution: Crash Course US History #7",
        "channel": "CrashCourse",
        "video_id": "3EiSymRrKI4",
        "url": "https://www.youtube.com/watch?v=3EiSymRrKI4",
        "embed_url": "https://www.youtube.com/embed/3EiSymRrKI4",
        "search_query": "modern world history civics and democracy crash course",
    },
    "physics": {
        "title": "Newton's Laws of Motion: Crash Course Physics #5",
        "channel": "CrashCourse",
        "video_id": "kKKM8Y-u7ds",
        "url": "https://www.youtube.com/watch?v=kKKM8Y-u7ds",
        "embed_url": "https://www.youtube.com/embed/kKKM8Y-u7ds",
        "search_query": "newtons laws of motion physics mechanics crash course",
    },
    "chemistry": {
        "title": "The Nucleus & Periodic Table: Crash Course Chemistry #1",
        "channel": "CrashCourse",
        "video_id": "FSyAehMdpyI",
        "url": "https://www.youtube.com/watch?v=FSyAehMdpyI",
        "embed_url": "https://www.youtube.com/embed/FSyAehMdpyI",
        "search_query": "atomic structure periodic table chemical reactions crash course",
    },
    "biology": {
        "title": "DNA, Chromosomes, Genes, and Traits",
        "channel": "Amoeba Sisters",
        "video_id": "8m6hHRlKwxY",
        "url": "https://www.youtube.com/watch?v=8m6hHRlKwxY",
        "embed_url": "https://www.youtube.com/embed/8m6hHRlKwxY",
        "search_query": "cell biology genetics dna organelles amoeba sisters",
    },
    "computer_science": {
        "title": "Python for Beginners - Full Course",
        "channel": "freeCodeCamp.org",
        "video_id": "eWRfhZUzrAc",
        "url": "https://www.youtube.com/watch?v=eWRfhZUzrAc",
        "embed_url": "https://www.youtube.com/embed/eWRfhZUzrAc",
        "search_query": "python programming basics computer science tutorial",
    },
    "geography": {
        "title": "What is Geography? Crash Course Geography #1",
        "channel": "CrashCourse",
        "video_id": "A3x7bMffl40",
        "url": "https://www.youtube.com/watch?v=A3x7bMffl40",
        "embed_url": "https://www.youtube.com/embed/A3x7bMffl40",
        "search_query": "world geography earth science crash course",
    },
    "economics": {
        "title": "Intro to Economics: Crash Course Economics #1",
        "channel": "CrashCourse",
        "video_id": "3ez10ADR_gM",
        "url": "https://www.youtube.com/watch?v=3ez10ADR_gM",
        "embed_url": "https://www.youtube.com/embed/3ez10ADR_gM",
        "search_query": "intro to economics supply and demand crash course",
    },
    "psychology": {
        "title": "Intro to Psychology: Crash Course Psychology #1",
        "channel": "CrashCourse",
        "video_id": "vo4pMVb0R6M",
        "url": "https://www.youtube.com/watch?v=vo4pMVb0R6M",
        "embed_url": "https://www.youtube.com/embed/vo4pMVb0R6M",
        "search_query": "intro to psychology cognitive science memory conditioning",
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
