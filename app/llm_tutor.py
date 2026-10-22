import json
import logging
import os
import re
from typing import Dict, Optional, Tuple
import urllib.error
import urllib.request

try:
    import httpx
except ImportError:
    httpx = None


from app.config import (
    GEMINI_API_KEY,
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    OPENAI_API_KEY,
)
from app.database import (
    get_cached_misconception_explanation,
    save_cached_misconception_explanation,
)

logger = logging.getLogger("cognify.llm_tutor")


class LLMTutorEngine:
    """
    Intelligent LLM-powered tutor engine for generating targeted misconception explanations.
    Features:
    - Multi-tier caching: In-memory LRU-like dictionary + persistent SQLite table.
    - Multi-provider support: Google Gemini, OpenAI, or compatible APIs (configured via .env).
    - Robust fallback: High-fidelity pedagogical heuristic engine if no API key or on timeout/network errors.
    """

    def __init__(self):
        # In-memory fast cache: cache_key -> {"explanation": str, "source": str}
        self._memory_cache: Dict[str, dict] = {}

    @staticmethod
    def build_cache_key(question_id: str, selected_option: int, misconception: str) -> str:
        """Deterministic cache key based on question, selected option, and tagged misconception."""
        clean_misc = (misconception or "unknown").strip().lower()
        return f"{question_id}:{selected_option}:{clean_misc}"

    def get_misconception_explanation(
        self,
        question_id: str,
        question_prompt: str,
        concept_name: str,
        selected_option: int,
        selected_option_text: str,
        correct_option_text: str,
        misconception: Optional[str],
        remediation: Optional[str] = None,
    ) -> str:
        """
        Retrieves or generates a short, empathetic explanation targeting the student's specific misconception.
        Uses in-memory cache first, then SQLite cache, then live LLM call, and falls back to specific remediation.
        """
        if not misconception:
            return remediation or "Review the solution steps carefully to understand where the calculation diverged."

        cache_key = self.build_cache_key(question_id, selected_option, misconception)

        # 1. Tier 1 Cache: In-memory
        if cache_key in self._memory_cache:
            logger.debug(f"[LLM Tutor Cache] Memory Hit for key: {cache_key}")
            return self._memory_cache[cache_key]["explanation"]

        # 2. Tier 2 Cache: SQLite persistence
        db_cached = get_cached_misconception_explanation(cache_key)
        if db_cached:
            logger.debug(f"[LLM Tutor Cache] SQLite Hit for key: {cache_key}")
            explanation = db_cached["explanation"]
            self._memory_cache[cache_key] = {
                "explanation": explanation,
                "source": db_cached.get("source", "db_cache"),
            }
            return explanation

        # 3. Live LLM Call (Gemini, OpenAI, or custom endpoint) or Remediation Fallback
        explanation, source = self._call_llm_or_fallback(
            question_id=question_id,
            question_prompt=question_prompt,
            concept_name=concept_name,
            selected_option=selected_option,
            selected_option_text=selected_option_text,
            correct_option_text=correct_option_text,
            misconception=misconception,
            remediation=remediation,
        )

        # 4. Cache the result in both SQLite and Memory
        try:
            save_cached_misconception_explanation(
                cache_key=cache_key,
                question_id=question_id,
                selected_option=selected_option,
                misconception=misconception,
                explanation=explanation,
                source=source,
            )
        except Exception as e:
            logger.warning(f"Failed to persist misconception explanation cache to SQLite: {e}")

        self._memory_cache[cache_key] = {"explanation": explanation, "source": source}
        return explanation

    def _call_llm_or_fallback(
        self,
        question_id: str,
        question_prompt: str,
        concept_name: str,
        selected_option: int,
        selected_option_text: str,
        correct_option_text: str,
        misconception: str,
        remediation: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Attempts to invoke configured LLM provider; falls back to specific remediation if unavailable."""
        # Check active API keys (from .env or os.environ)
        gemini_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "").strip()
        openai_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "").strip()
        generic_llm_key = LLM_API_KEY or os.getenv("LLM_API_KEY", "").strip()

        # Try Google Gemini if configured
        if gemini_key:
            try:
                res = self._call_gemini(
                    api_key=gemini_key,
                    concept_name=concept_name,
                    question_prompt=question_prompt,
                    selected_option_text=selected_option_text,
                    correct_option_text=correct_option_text,
                    misconception=misconception,
                    remediation=remediation,
                )
                if res:
                    return res, "gemini"
            except Exception as e:
                logger.warning(f"Gemini LLM call failed ({e}); falling back to remediation.")

        # Try OpenAI (or compatible provider) if configured
        effective_openai_key = openai_key or generic_llm_key
        if effective_openai_key:
            try:
                res = self._call_openai(
                    api_key=effective_openai_key,
                    concept_name=concept_name,
                    question_prompt=question_prompt,
                    selected_option_text=selected_option_text,
                    correct_option_text=correct_option_text,
                    misconception=misconception,
                    remediation=remediation,
                )
                if res:
                    return res, "openai"
            except Exception as e:
                logger.warning(f"OpenAI LLM call failed ({e}); falling back to remediation.")

        # Fallback: specific remediation text from questions.json
        if remediation:
            return remediation, "remediation"

        # Heuristic engine fallback if remediation not provided
        fallback = self._generate_heuristic_explanation(
            misconception=misconception,
            concept_name=concept_name,
            selected_option_text=selected_option_text,
            correct_option_text=correct_option_text,
        )
        return fallback, "heuristic_fallback"

    def _build_tutor_prompt(
        self,
        concept_name: str,
        question_prompt: str,
        selected_option_text: str,
        correct_option_text: str,
        misconception: str,
        remediation: Optional[str] = None,
    ) -> str:
        """Constructs a pedagogically structured prompt for the LLM."""
        human_readable_misc = misconception.replace("_", " ").title()
        remediation_hint = f"\nCurriculum Remediation Guidance: {remediation}" if remediation else ""
        return (
            "You are an encouraging, expert math tutor. A student just answered a multiple-choice question "
            "incorrectly because of a specific cognitive misconception. "
            "Write a concise, friendly 1 to 2 sentence explanation directly addressing this exact misconception. "
            "Name the exact mistake they made and explain the correct mathematical method clearly. "
            "Do NOT repeat the entire question prompt.\n\n"
            f"Concept: {concept_name}\n"
            f"Question Prompt: {question_prompt}\n"
            f"Student's Incorrect Choice: {selected_option_text}\n"
            f"Correct Answer: {correct_option_text}\n"
            f"Diagnosed Cognitive Misconception: {misconception} ({human_readable_misc})"
            f"{remediation_hint}\n\n"
            "Tutor Explanation (1-2 sentences):"
        )

    def _call_gemini(
        self,
        api_key: str,
        concept_name: str,
        question_prompt: str,
        selected_option_text: str,
        correct_option_text: str,
        misconception: str,
        remediation: Optional[str] = None,
    ) -> Optional[str]:
        """Calls Google Gemini API using httpx."""
        model = LLM_MODEL or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        # Support fallback models if user provided older model name
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        prompt = self._build_tutor_prompt(
            concept_name, question_prompt, selected_option_text, correct_option_text, misconception, remediation
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 200,
            },
        }

        if httpx is not None:
            with httpx.Client(timeout=8.0) as client:
                response = client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "").strip()
                            return self._clean_llm_text(text)
                else:
                    logger.warning(f"Gemini API returned status {response.status_code}: {response.text[:200]}")
        else:
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=8.0) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[0].get("text", "").strip()
                                return self._clean_llm_text(text)
            except Exception as e:
                logger.warning(f"Gemini API request failed via urllib: {e}")
        return None

    def _call_openai(
        self,
        api_key: str,
        concept_name: str,
        question_prompt: str,
        selected_option_text: str,
        correct_option_text: str,
        misconception: str,
        remediation: Optional[str] = None,
    ) -> Optional[str]:
        """Calls OpenAI or OpenAI-compatible endpoint using httpx or urllib."""
        model = LLM_MODEL or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        base_url = (LLM_BASE_URL or os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        url = f"{base_url}/chat/completions"
        prompt = self._build_tutor_prompt(
            concept_name, question_prompt, selected_option_text, correct_option_text, misconception, remediation
        )
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an encouraging, empathetic math tutor. When a student chooses an incorrect "
                        "answer due to a specific misconception, provide a short 1-2 sentence coaching tip "
                        "directly addressing their misunderstanding."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 150,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        if httpx is not None:
            with httpx.Client(timeout=8.0) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices:
                        text = choices[0].get("message", {}).get("content", "").strip()
                        return self._clean_llm_text(text)
                else:
                    logger.warning(f"OpenAI API returned status {response.status_code}: {response.text[:200]}")
        else:
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=8.0) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        choices = data.get("choices", [])
                        if choices:
                            text = choices[0].get("message", {}).get("content", "").strip()
                            return self._clean_llm_text(text)
            except Exception as e:
                logger.warning(f"OpenAI API request failed via urllib: {e}")
        return None

    @staticmethod
    def _clean_llm_text(text: str) -> str:
        """Cleans quotes, markdown prefixes, and extraneous whitespaces from LLM responses."""
        cleaned = text.strip()
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
            cleaned = cleaned[1:-1].strip()
        cleaned = re.sub(r"^(Tutor Explanation:\s*|Explanation:\s*)", "", cleaned, flags=re.IGNORECASE).strip()
        return cleaned

    def _generate_heuristic_explanation(
        self,
        misconception: str,
        concept_name: str,
        selected_option_text: str,
        correct_option_text: str,
    ) -> str:
        """
        High-fidelity pedagogical heuristic engine providing targeted explanations
        tailored to the cognitive misconception pattern.
        """
        misc = misconception.lower()

        # Dedicated heuristics for core curriculum misconceptions
        rules = {
            "add_denominators_directly": (
                f"You chose '{selected_option_text}' by adding the denominators directly. "
                "Remember that when adding fractions, you must find a common denominator; you never add the bottom numbers!"
            ),
            "added_denominators": (
                f"You added the denominators together. In fraction operations, denominators indicate partition size "
                f"and remain constant once common denominators are established ({correct_option_text})."
            ),
            "inverted_numerator_denominator": (
                f"You inverted the numerator and denominator ({selected_option_text}). "
                "The numerator represents parts counted, while the denominator represents total equal parts in the whole."
            ),
            "forgot_to_flip_inequality_sign": (
                f"You chose '{selected_option_text}' because you didn't flip the inequality sign. "
                "Crucial rule: whenever you multiply or divide both sides of an inequality by a negative number, the inequality sign must flip!"
            ),
            "multiplied_denominators_instead_of_lcm": (
                f"You multiplied the denominators directly rather than finding the Least Common Multiple (LCM). "
                f"While valid for finding a common denominator, simplifying reveals the true lowest term ({correct_option_text})."
            ),
            "evaluated_left_to_right_without_precedence": (
                f"You evaluated from left to right to get '{selected_option_text}'. "
                "Follow Order of Operations (PEMDAS): multiplication and division must be performed before addition and subtraction."
            ),
            "ratio_part_to_remaining_part": (
                f"You compared the selected parts to the remaining parts ({selected_option_text}). "
                f"Standard fractions compare selected parts to the entire whole ({correct_option_text})."
            ),
            "confused_numerator_and_denominator": (
                "The numerator is on top (parts selected) and the denominator is on the bottom (total whole parts)."
            ),
            "distributed_only_to_first_term": (
                f"You chose '{selected_option_text}' by distributing only to the first term. "
                "Remember to multiply the term outside parentheses by EVERY term inside."
            ),
            "combined_unlike_terms": (
                f"You combined terms that are not like terms ({selected_option_text}). "
                "Only terms with matching variable powers can be added or subtracted together."
            ),
            "subtracted_instead_of_added": (
                f"You subtracted instead of adding to invert the operation ({selected_option_text}). "
                "Always apply the inverse operation to isolate the variable."
            ),
            "divided_instead_of_multiplied": (
                f"You divided instead of multiplying ({selected_option_text}). "
                "Use the reciprocal operation to isolate terms with fractional coefficients."
            ),
            "forgot_negative_sign": (
                f"Be careful with signs! You missed the negative sign leading to '{selected_option_text}'. "
                f"The correct value is {correct_option_text}."
            ),
            "added_to_both_terms": (
                f"Adding the same number to numerator and denominator changes the fraction value. "
                "To find equivalent fractions, you must multiply or divide both by the same non-zero number."
            ),
        }

        for key, exp in rules.items():
            if key in misc:
                return exp

        # Generative pattern for any other misconception tag
        readable_label = misc.replace("_", " ")
        return (
            f"You selected '{selected_option_text}' reflecting a common misunderstanding in {concept_name} "
            f"({readable_label}). Carefully review how the inverse operation or definition applies to reach {correct_option_text}."
        )


# Global singleton instance
llm_tutor = LLMTutorEngine()
