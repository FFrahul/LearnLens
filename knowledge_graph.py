"""Deterministic knowledge graph construction from local source tags."""


def build_knowledge_graph(items):
    nodes = {}
    edges = set()

    def add_node(label, kind):
        key = f"{kind}:{label}"
        nodes.setdefault(key, {"id": key, "label": label, "kind": kind})
        return key

    for item in items:
        topic = str(item.get("topic", "")).strip()
        subtopic = str(item.get("subtopic", "")).strip()
        if not topic or topic == "General":
            continue

        topic_id = add_node(topic, "topic")
        if subtopic:
            subtopic_id = add_node(subtopic, "subtopic")
            edges.add((topic_id, subtopic_id, "contains"))

        parent_id = subtopic_id if subtopic else topic_id
        for concept in item.get("key_concepts", []):
            concept = str(concept).strip()
            if not concept:
                continue
            concept_id = add_node(concept, "concept")
            edges.add((parent_id, concept_id, "covers"))

        for prerequisite in item.get("prerequisites", []):
            prerequisite = str(prerequisite).strip()
            if prerequisite:
                prerequisite_id = add_node(prerequisite, "prerequisite")
                edges.add((prerequisite_id, topic_id, "precedes"))

    return {
        "nodes": sorted(nodes.values(), key=lambda node: (node["kind"], node["label"].casefold())),
        "edges": [
            {"source": source, "target": target, "relation": relation}
            for source, target, relation in sorted(edges)
        ],
    }
