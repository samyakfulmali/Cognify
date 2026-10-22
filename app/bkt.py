from dataclasses import dataclass
from app.config import BKT_P_INIT, BKT_P_LEARN, BKT_P_SLIP, BKT_P_GUESS


@dataclass
class BKTEngine:
    """
    Standard Bayesian Knowledge Tracing (BKT) engine.
    
    Parameters:
        p_init: Prior probability that a student already knows the concept.
        p_learn: Probability that a student transitions from unlearned to learned state.
        p_slip: Probability that a student answers incorrectly despite knowing the concept.
        p_guess: Probability that a student answers correctly by guessing without knowing.
    """
    p_init: float = BKT_P_INIT
    p_learn: float = BKT_P_LEARN
    p_slip: float = BKT_P_SLIP
    p_guess: float = BKT_P_GUESS

    def predict_correct(self, p_known: float) -> float:
        """
        Calculates the marginal probability that the student will answer correctly
        given their current mastery level P(L_t).
        
        P(Correct) = P(L_t) * (1 - P(Slip)) + (1 - P(L_t)) * P(Guess)
        """
        p_known = max(0.0, min(1.0, p_known))
        return (p_known * (1.0 - self.p_slip)) + ((1.0 - p_known) * self.p_guess)

    def calculate_posterior(self, p_known: float, is_correct: bool) -> float:
        """
        Applies Bayes' rule to calculate the posterior probability of knowing P(L_t | obs)
        after observing an answer (correct or incorrect).
        """
        p_known = max(0.0, min(1.0, p_known))
        
        if is_correct:
            numerator = p_known * (1.0 - self.p_slip)
            denominator = numerator + ((1.0 - p_known) * self.p_guess)
        else:
            numerator = p_known * self.p_slip
            denominator = numerator + ((1.0 - p_known) * (1.0 - self.p_guess))

        if denominator <= 0.0:
            return p_known

        posterior = numerator / denominator
        return max(0.0, min(1.0, posterior))

    def update(self, p_known: float, is_correct: bool) -> float:
        """
        Performs a full BKT step:
        1. Observation update (Bayes' rule) -> P(L_t | obs)
        2. State transition (learning step) -> P(L_{t+1}) = P(L_t | obs) + (1 - P(L_t | obs)) * P(learn)
        
        Returns the updated P(L_{t+1}).
        """
        posterior = self.calculate_posterior(p_known, is_correct)
        p_next = posterior + ((1.0 - posterior) * self.p_learn)
        return max(0.0, min(1.0, p_next))


# Default instance
bkt_engine = BKTEngine()
