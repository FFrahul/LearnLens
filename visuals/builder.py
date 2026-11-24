"""Build structured visual specifications with retry and deterministic fallback."""

from __future__ import annotations

import json
from typing import Any, Callable

from .schema import (
    repair_json,
    validate_flowchart,
    validate_nodes_edges,
    validate_revision,
    validate_storyboard,
)


def deterministic_concept(topic: str, items: list[str]) -> dict[str, Any]:
    nodes = [{"id": "topic", "label": topic, "group": "Core"}]
    edges = []
    for index, item in enumerate(items[:11], start=1):
        node_id = f"concept_{index}"
        nodes.append({"id": node_id, "label": item, "group": "Supporting"})
        edges.append({"source": "topic", "target": node_id, "label": "includes"})
    return {"nodes": nodes, "edges": edges}


def deterministic_flow(topic: str, items: list[str]) -> dict[str, Any]:
    steps = [{"label": f"Understand {topic}", "shape": "start"}]
    steps.extend(
        {"label": item, "shape": "decision" if index % 3 == 2 else "process", "decision": ""}
        for index, item in enumerate(items[:10])
    )
    steps.append({"label": "Check understanding", "shape": "end"})
    return {"steps": steps}


def deterministic_revision(topic: str, items: list[str]) -> dict[str, Any]:
    return {
        "topic": topic,
        "definitions": items[:3] or [f"Core definition of {topic}"],
        "rule": f"Use the key ideas of {topic} step by step.",
        "remember": (items[:3] or [topic]),
        "example": f"Apply {topic} to one short source-based example.",
    }


def deterministic_storyboard(topic: str, items: list[str]) -> dict[str, Any]:
    points = items[:6] or [topic]
    return {
        "scenes": [
            {
                "script": f"Introduce {point.lower()}.",
                "visual": f"A short labeled diagram for {point}.",
            }
            for point in points
        ]
    }


def build_visual(
    kind: str,
    topic: str,
    items: list[str],
    llm_generate: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    deterministic = {
        "concept": deterministic_concept,
        "flow": deterministic_flow,
        "revision": deterministic_revision,
        "storyboard": deterministic_storyboard,
    }[kind]
    fallback = deterministic(topic, items)
    if llm_generate is None:
        return fallback

    schema_hint = {
        "concept": '{"nodes":[{"id":"topic","label":"...","group":"Core"}],"edges":[{"source":"topic","target":"...","label":"..."}]}',
        "flow": '{"steps":[{"label":"...","shape":"process","decision":""}]}',
        "revision": '{"topic":"...","definitions":["..."],"rule":"...","remember":["...","...","..."],"example":"..."}',
        "storyboard": '{"scenes":[{"script":"...","visual":"..."}]}',
    }[kind]
    prompt = (
        f"Return one valid JSON object only for a {kind} visual.\n"
        f"Topic: {topic}\n"
        f"Source concepts: {json.dumps(items[:12], ensure_ascii=False)}\n"
        f"JSON schema: {schema_hint}\n"
        "Use at most 12 nodes/scenes, labels of 4 words or fewer when possible, "
        "and only information supported by the source concepts."
    )
    for _ in range(2):
        try:
            response = llm_generate(prompt)
            data = repair_json(response)
            if kind == "concept":
                return validate_nodes_edges(data)
            if kind == "flow":
                return validate_flowchart(data)
            if kind == "revision":
                return validate_revision(data)
            return validate_storyboard(data)
        except Exception:
            prompt += "\nRepair: return valid JSON only, with no Markdown or comments."
    return fallback
