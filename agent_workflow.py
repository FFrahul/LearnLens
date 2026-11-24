"""Small offline orchestration layer for grounded tutor responses."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentDecision:
    """Result of the verifier agent's source-grounding check."""

    accepted_sources: list
    max_score: float
    reason: str


def plan_learning_query(question):
    """Planner role: normalize a question into retrieval terms."""
    return {
        "question": " ".join(str(question).split()),
        "terms": {
            token.casefold()
            for token in str(question).split()
            if token.strip()
        },
    }


def verify_retrieved_sources(sources, minimum_score):
    """Verifier role: reject weak evidence before generation."""
    accepted = [
        source for source in sources
        if float(source.get("score", 0.0)) >= minimum_score
    ]
    max_score = max(
        (float(source.get("score", 0.0)) for source in accepted),
        default=0.0
    )
    return AgentDecision(
        accepted_sources=accepted,
        max_score=max_score,
        reason="grounded" if accepted else "insufficient evidence",
    )
