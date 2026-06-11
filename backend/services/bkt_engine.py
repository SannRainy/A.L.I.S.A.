"""
BKT Engine — Bayesian Knowledge Tracing
Estimates P(mastered) for each node based on observed responses.
"""
import logging
import math
from typing import Optional

logger = logging.getLogger(__name__)


class BKTEngine:
    """
    Bayesian Knowledge Tracing with 4 parameters per skill:
    - P(L0): prior probability of mastery
    - P(T):  probability of transitioning from unlearned to learned
    - P(G):  probability of guessing correctly when unlearned
    - P(S):  probability of slipping (incorrect when learned)
    """

    # Default BKT parameters (can be tuned per skill domain)
    DEFAULT_PARAMS = {
        "vocab": {"p_l0": 0.1, "p_t": 0.15, "p_g": 0.25, "p_s": 0.05},
        "grammar": {"p_l0": 0.05, "p_t": 0.10, "p_g": 0.20, "p_s": 0.10},
        "kanji": {"p_l0": 0.05, "p_t": 0.12, "p_g": 0.10, "p_s": 0.05},
    }

    MASTERY_THRESHOLD = 0.85  # P(L) >= 0.85 → considered mastered

    @staticmethod
    def get_params(node_type: str) -> dict:
        """Get BKT parameters for a skill domain."""
        return BKTEngine.DEFAULT_PARAMS.get(
            node_type.lower(),
            BKTEngine.DEFAULT_PARAMS["vocab"]
        )

    @staticmethod
    def update_belief(p_l: float, correct: bool, params: dict) -> float:
        """
        Update P(L) given an observation (correct/incorrect).

        Bayes update:
        If correct:
            P(L|correct) = P(L) * (1 - P(S)) / P(correct)
            P(correct) = P(L)*(1-P(S)) + (1-P(L))*P(G)
        If incorrect:
            P(L|incorrect) = P(L) * P(S) / P(incorrect)
            P(incorrect) = P(L)*P(S) + (1-P(L))*(1-P(G))

        Then apply transition: P(L_new) = P(L|obs) + (1 - P(L|obs)) * P(T)
        """
        p_s = params["p_s"]
        p_g = params["p_g"]
        p_t = params["p_t"]

        if correct:
            p_obs = p_l * (1 - p_s) + (1 - p_l) * p_g
            if p_obs == 0:
                p_l_given_obs = p_l
            else:
                p_l_given_obs = (p_l * (1 - p_s)) / p_obs
        else:
            p_obs = p_l * p_s + (1 - p_l) * (1 - p_g)
            if p_obs == 0:
                p_l_given_obs = p_l
            else:
                p_l_given_obs = (p_l * p_s) / p_obs

        # Apply learning transition
        p_l_new = p_l_given_obs + (1 - p_l_given_obs) * p_t

        return min(max(p_l_new, 0.001), 0.999)

    @staticmethod
    def compute_mastery(observations: list[bool], node_type: str) -> dict:
        """
        Compute current P(mastered) from sequence of observations.

        observations: list of bool (True=correct, False=incorrect), oldest first.
        Returns dict with p_mastered, is_mastered, confidence.
        """
        params = BKTEngine.get_params(node_type)
        p_l = params["p_l0"]

        for obs in observations:
            p_l = BKTEngine.update_belief(p_l, obs, params)

        return {
            "p_mastered": round(p_l, 4),
            "is_mastered": p_l >= BKTEngine.MASTERY_THRESHOLD,
            "confidence": round(abs(p_l - 0.5) * 2, 4),  # 0=uncertain, 1=certain
            "total_observations": len(observations),
        }

    @staticmethod
    def select_next_questions(
        node_beliefs: dict[str, float],
        available_nodes: list[dict],
        count: int = 5,
    ) -> list[dict]:
        """
        Select optimal questions using Information Gain heuristic.

        Prioritize nodes where:
        1. P(L) is closest to 0.5 (maximum uncertainty → most informative)
        2. P(L) is below mastery threshold (not yet mastered)

        node_beliefs: {node_id: p_mastered}
        available_nodes: list of {id, node_type, ...}
        """
        scored = []
        for node in available_nodes:
            nid = node.get("id", "")
            p_l = node_beliefs.get(nid, 0.1)

            if p_l >= BKTEngine.MASTERY_THRESHOLD:
                continue  # Skip mastered nodes

            # Information gain: entropy is maximized at p=0.5
            # Score = closeness to 0.5 (prefer uncertain nodes)
            uncertainty = 1.0 - abs(p_l - 0.5) * 2
            # Boost struggling nodes slightly
            struggle_boost = 0.2 if p_l < 0.3 else 0.0

            scored.append({
                **node,
                "_score": uncertainty + struggle_boost,
                "_p_mastered": p_l,
            })

        scored.sort(key=lambda x: x["_score"], reverse=True)
        return scored[:count]

    @staticmethod
    def estimate_difficulty(observations: list[bool]) -> str:
        """
        Estimate question difficulty from collective response data.
        Returns 'easy', 'medium', or 'hard'.
        """
        if not observations:
            return "medium"
        accuracy = sum(observations) / len(observations)
        if accuracy >= 0.8:
            return "easy"
        elif accuracy >= 0.5:
            return "medium"
        else:
            return "hard"

    @staticmethod
    def compute_cat_difficulty(p_mastered: float) -> str:
        """
        Computerized Adaptive Testing: select difficulty matching student level.
        Pick difficulty where P(correct) ~ 0.5-0.7 for maximum information.
        """
        if p_mastered < 0.3:
            return "easy"
        elif p_mastered < 0.6:
            return "medium"
        else:
            return "hard"
