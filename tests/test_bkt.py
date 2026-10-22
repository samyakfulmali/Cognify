import pytest
from app.bkt import BKTEngine


def test_bkt_default_parameters():
    engine = BKTEngine()
    assert engine.p_init == 0.3
    assert engine.p_learn == 0.2
    assert engine.p_slip == 0.1
    assert engine.p_guess == 0.25


def test_bkt_update_on_correct_answer():
    """
    Manual verification:
    L_0 = 0.3, Slip = 0.1, Guess = 0.25, Learn = 0.2
    
    Numerator = 0.3 * (1 - 0.1) = 0.27
    Denominator = 0.27 + (1 - 0.3) * 0.25 = 0.27 + 0.175 = 0.445
    Posterior = 0.27 / 0.445 = 0.60674157...
    
    Transition:
    L_1 = Posterior + (1 - Posterior) * 0.2
        = 0.60674157 + (0.39325843 * 0.2)
        = 0.60674157 + 0.07865168
        = 0.68539325...
    """
    engine = BKTEngine(p_init=0.3, p_learn=0.2, p_slip=0.1, p_guess=0.25)
    
    posterior = engine.calculate_posterior(p_known=0.3, is_correct=True)
    expected_posterior = 0.27 / 0.445
    assert pytest.approx(posterior, rel=1e-4) == expected_posterior
    
    p_next = engine.update(p_known=0.3, is_correct=True)
    expected_p_next = expected_posterior + (1.0 - expected_posterior) * 0.2
    assert pytest.approx(p_next, rel=1e-4) == expected_p_next
    assert p_next > 0.3  # Mastery strictly increases on correct answer


def test_bkt_update_on_incorrect_answer():
    """
    Manual verification:
    L_0 = 0.3, Slip = 0.1, Guess = 0.25, Learn = 0.2
    
    Numerator = 0.3 * 0.1 = 0.03
    Denominator = 0.03 + (1 - 0.3) * (1 - 0.25) = 0.03 + 0.7 * 0.75 = 0.03 + 0.525 = 0.555
    Posterior = 0.03 / 0.555 = 0.054054...
    
    Transition:
    L_1 = Posterior + (1 - Posterior) * 0.2
        = 0.05405405 + (0.94594595 * 0.2)
        = 0.05405405 + 0.18918919
        = 0.24324324...
    """
    engine = BKTEngine(p_init=0.3, p_learn=0.2, p_slip=0.1, p_guess=0.25)
    
    posterior = engine.calculate_posterior(p_known=0.3, is_correct=False)
    expected_posterior = 0.03 / 0.555
    assert pytest.approx(posterior, rel=1e-4) == expected_posterior
    
    p_next = engine.update(p_known=0.3, is_correct=False)
    expected_p_next = expected_posterior + (1.0 - expected_posterior) * 0.2
    assert pytest.approx(p_next, rel=1e-4) == expected_p_next
    assert p_next < 0.3  # Mastery decreases from initial prior after failure


def test_bkt_consecutive_successes_converge_to_one():
    engine = BKTEngine(p_init=0.3, p_learn=0.2, p_slip=0.1, p_guess=0.25)
    p = 0.3
    
    for _ in range(8):
        p_next = engine.update(p, is_correct=True)
        assert p_next > p
        p = p_next

    assert p > 0.98


def test_bkt_predict_correctness():
    engine = BKTEngine(p_init=0.3, p_learn=0.2, p_slip=0.1, p_guess=0.25)
    
    # If p_known is 0: P(correct) = 0*(0.9) + 1*(0.25) = 0.25 (pure guess)
    assert pytest.approx(engine.predict_correct(0.0), rel=1e-4) == 0.25
    
    # If p_known is 1: P(correct) = 1*(0.9) + 0*(0.25) = 0.90 (1 - slip)
    assert pytest.approx(engine.predict_correct(1.0), rel=1e-4) == 0.90
    
    # If p_known is 0.5: 0.5*0.9 + 0.5*0.25 = 0.45 + 0.125 = 0.575
    assert pytest.approx(engine.predict_correct(0.5), rel=1e-4) == 0.575


def test_bkt_boundary_clamping():
    engine = BKTEngine()
    # Clamps inputs < 0 and > 1 safely
    p_low = engine.update(-0.5, is_correct=False)
    assert 0.0 <= p_low <= 1.0

    p_high = engine.update(1.5, is_correct=True)
    assert 0.0 <= p_high <= 1.0
