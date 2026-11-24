"""Validation and deterministic fallback schemas for LearnLens visuals."""

from __future__ import annotations

import json
from typing import Any


MAX_NODES = 12


def validate_nodes_edges(data: dict[str, Any]) -> dict[str, Any]:
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("A concept map needs nodes and edges arrays.")

    clean_nodes = []
    clean_edges = []
    for node in nodes[:MAX_NODES]:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id", "")).strip()
        label = str(node.get("label", "")).strip()
        if not node_id or not label:
            continue
        clean_nodes.append({
            "id": node_id[:40],
            "label": label[:48],
            "group": str(node.get("group", "Core"))[:24],
        })

    node_ids = {node["id"] for node in clean_nodes}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source = str(edge.get("source", "")).strip()
        target = str(edge.get("target", "")).strip()
        if source not in node_ids or target not in node_ids:
            continue
        clean_edges.append({
            "source": source,
            "target": target,
            "label": str(edge.get("label", "")).strip()[:28],
        })

    if not clean_nodes:
        raise ValueError("The visual has no valid nodes.")
    return {"nodes": clean_nodes, "edges": clean_edges[:MAX_NODES]}


def validate_flowchart(data: dict[str, Any]) -> dict[str, Any]:
    steps = data.get("steps")
    if not isinstance(steps, list):
        raise ValueError("A flowchart needs a steps array.")
    clean_steps = []
    for step in steps[:MAX_NODES]:
        if not isinstance(step, dict):
            continue
        label = str(step.get("label", "")).strip()
        if not label:
            continue
        clean_steps.append({
            "label": label[:60],
            "shape": str(step.get("shape", "process")).lower(),
            "decision": str(step.get("decision", "")).strip()[:40],
        })
    if not clean_steps:
        raise ValueError("The flowchart has no valid steps.")
    return {"steps": clean_steps}


def validate_revision(data: dict[str, Any]) -> dict[str, Any]:
    clean = {
        "topic": str(data.get("topic", "Revision")).strip()[:80] or "Revision",
        "definitions": [],
        "rule": str(data.get("rule", "")).strip()[:160],
        "remember": [],
        "example": str(data.get("example", "")).strip()[:240],
    }
    if isinstance(data.get("definitions"), list):
        clean["definitions"] = [
            str(item).strip()[:100]
            for item in data["definitions"][:6]
            if str(item).strip()
        ]
    if isinstance(data.get("remember"), list):
        clean["remember"] = [
            str(item).strip()[:100]
            for item in data["remember"][:3]
            if str(item).strip()
        ]
    return clean


def validate_storyboard(data: dict[str, Any]) -> dict[str, Any]:
    scenes = data.get("scenes")
    if not isinstance(scenes, list):
        raise ValueError("A storyboard needs a scenes array.")
    clean_scenes = []
    for scene in scenes[:12]:
        if not isinstance(scene, dict):
            continue
        script = str(scene.get("script", "")).strip()
        visual = str(scene.get("visual", "")).strip()
        if script or visual:
            clean_scenes.append({
                "script": script[:180],
                "visual": visual[:140],
            })
    if not clean_scenes:
        raise ValueError("The storyboard has no valid scenes.")
    return {"scenes": clean_scenes}


def repair_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    return json.loads(text)
