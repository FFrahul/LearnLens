"""Deterministic learner recovery planning from measured weak topics."""


def build_recovery_plan(topic_results, graph=None, limit=3):
    graph = graph or {"edges": []}
    prerequisites = {}
    for edge in graph.get("edges", []):
        if edge.get("relation") != "precedes":
            continue
        target = edge["target"].split(":", 1)[-1]
        source = edge["source"].split(":", 1)[-1]
        prerequisites.setdefault(target, []).append(source)

    plan = []
    for result in topic_results:
        if result.get("status") != "🔴 Needs Review":
            continue
        topic = str(result.get("topic", "")).strip()
        if not topic:
            continue
        plan.append({
            "topic": topic,
            "accuracy": float(result.get("accuracy", 0.0)),
            "step": (
                "Review prerequisite concepts first: "
                + ", ".join(prerequisites.get(topic, []))
                if prerequisites.get(topic)
                else "Review the cited material, then retry an easier question."
            ),
        })
        if len(plan) >= limit:
            break
    return plan
