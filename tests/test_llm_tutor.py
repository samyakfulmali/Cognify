import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from app.llm_tutor import LLMTutorEngine
from app.database import (
    init_db,
    get_cached_misconception_explanation,
    save_cached_misconception_explanation,
    get_all_cached_misconceptions,
)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_build_cache_key():
    key = LLMTutorEngine.build_cache_key("q_frac_add_01", 1, "add_denominators_directly")
    assert key == "q_frac_add_01:1:add_denominators_directly"


def test_heuristic_fallback_generation():
    engine = LLMTutorEngine()
    exp = engine.get_misconception_explanation(
        question_id="q_frac_add_test",
        question_prompt="What is 1/5 + 2/5?",
        concept_name="Fraction Addition",
        selected_option=1,
        selected_option_text="3/10",
        correct_option_text="3/5",
        misconception="add_denominators_directly",
    )
    assert "denominators" in exp.lower()
    assert len(exp) > 20

    # Ensure it was cached in memory
    cache_key = engine.build_cache_key("q_frac_add_test", 1, "add_denominators_directly")
    assert cache_key in engine._memory_cache

    # Ensure it was persisted in SQLite
    db_row = get_cached_misconception_explanation(cache_key)
    assert db_row is not None
    assert db_row["explanation"] == exp


def test_memory_cache_hit_bypasses_network_and_db():
    engine = LLMTutorEngine()
    cache_key = engine.build_cache_key("q_test_01", 0, "test_misc")
    engine._memory_cache[cache_key] = {
        "explanation": "Pre-cached in-memory explanation.",
        "source": "memory_test",
    }

    result = engine.get_misconception_explanation(
        question_id="q_test_01",
        question_prompt="Any prompt",
        concept_name="Any concept",
        selected_option=0,
        selected_option_text="Choice A",
        correct_option_text="Choice B",
        misconception="test_misc",
    )
    assert result == "Pre-cached in-memory explanation."


def test_sqlite_cache_hit_repopulates_memory_cache():
    engine = LLMTutorEngine()
    cache_key = engine.build_cache_key("q_db_test_01", 2, "inverted_numerator_denominator")
    
    # Save directly in SQLite
    save_cached_misconception_explanation(
        cache_key=cache_key,
        question_id="q_db_test_01",
        selected_option=2,
        misconception="inverted_numerator_denominator",
        explanation="Persisted SQLite explanation.",
        source="sqlite_test",
    )

    # In-memory cache is empty for this key
    assert cache_key not in engine._memory_cache

    result = engine.get_misconception_explanation(
        question_id="q_db_test_01",
        question_prompt="Prompt",
        concept_name="Fractions",
        selected_option=2,
        selected_option_text="8/3",
        correct_option_text="3/8",
        misconception="inverted_numerator_denominator",
    )

    assert result == "Persisted SQLite explanation."
    # Memory cache should now be populated
    assert cache_key in engine._memory_cache
    assert engine._memory_cache[cache_key]["explanation"] == "Persisted SQLite explanation."


def test_mock_gemini_api_call():
    engine = LLMTutorEngine()
    fake_response_text = "You inverted the fraction. The numerator counts selected slices, not the whole."

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": fake_response_text}]
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        exp, source = engine._call_llm_or_fallback(
            question_id="q_gemini_test",
            question_prompt="Prompt",
            concept_name="Fractions Basics",
            selected_option=1,
            selected_option_text="8/3",
            correct_option_text="3/8",
            misconception="inverted_numerator_denominator",
        )
        # Even if no GEMINI_API_KEY is present in env, with patch or mock, let's test _call_gemini directly
        gemini_result = engine._call_gemini(
            api_key="fake-gemini-key",
            concept_name="Fractions Basics",
            question_prompt="Prompt",
            selected_option_text="8/3",
            correct_option_text="3/8",
            misconception="inverted_numerator_denominator",
        )
        assert gemini_result == fake_response_text


def test_mock_openai_api_call():
    engine = LLMTutorEngine()
    fake_response_text = "Remember to flip the inequality sign whenever multiplying or dividing by a negative number."

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {"content": fake_response_text}
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        openai_result = engine._call_openai(
            api_key="fake-openai-key",
            concept_name="Linear Inequalities",
            question_prompt="Solve -2x > 6",
            selected_option_text="x > -3",
            correct_option_text="x < -3",
            misconception="forgot_to_flip_inequality_sign",
        )
        assert openai_result == fake_response_text
