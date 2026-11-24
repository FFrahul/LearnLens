"""Honest readiness checks for optional local sequence experiments."""


def assess_sequence_readiness(
    observations,
    minimum_samples=20,
    minimum_topics=2
):
    observations = observations if isinstance(observations, list) else []
    topics = {
        str(item.get("topic", "")).strip()
        for item in observations
        if isinstance(item, dict) and str(item.get("topic", "")).strip()
    }
    reasons = []
    if len(observations) < minimum_samples:
        reasons.append(
            f"Need at least {minimum_samples} labeled observations."
        )
    if len(topics) < minimum_topics:
        reasons.append(
            f"Need at least {minimum_topics} distinct topics."
        )
    return {
        "ready": not reasons,
        "samples": len(observations),
        "topics": len(topics),
        "reasons": reasons,
    }
