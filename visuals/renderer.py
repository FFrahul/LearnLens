"""Auto-laid-out SVG renderer for LearnLens visual specifications."""

from __future__ import annotations

import html
import math
from pathlib import Path
from typing import Any


PALETTE = {
    "indigo": "#4F46E5",
    "teal": "#0F766E",
    "amber": "#B45309",
    "navy": "#172554",
    "sky": "#0284C7",
    "light": "#F8FAFC",
    "line": "#CBD5E1",
}


def _wrap(text: str, limit: int = 24) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if len(candidate) > limit and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines[:3]


def _text_lines(x: float, y: float, lines: list[str], fill: str, size: int = 16) -> str:
    parts = []
    for index, line in enumerate(lines):
        parts.append(
            f'<text x="{x:.1f}" y="{y + index * (size + 4):.1f}" '
            f'text-anchor="middle" font-family="Arial, sans-serif" '
            f'font-size="{size}" fill="{fill}">'
            f"{html.escape(line)}</text>"
        )
    return "".join(parts)


def render_concept_map(data: dict[str, Any], title: str, source_caption: str) -> str:
    width, height = 980, 620
    nodes = data["nodes"][:12]
    edges = data["edges"]
    node_by_id = {node["id"]: node for node in nodes}

    center = nodes[0] if nodes else {"id": "topic", "label": title, "group": "Core"}
    branches = nodes[1:]
    angle_step = (2 * math.pi) / max(len(branches), 1)
    positions = {center["id"]: (490, 300)}
    for index, node in enumerate(branches):
        angle = -math.pi / 2 + index * angle_step
        positions[node["id"]] = (
            490 + 330 * math.cos(angle),
            300 + 205 * math.sin(angle),
        )

    shapes = [
        f'<rect width="{width}" height="{height}" rx="16" fill="{PALETTE["light"]}"/>',
        f'<text x="490" y="42" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="24" font-weight="700" fill="{PALETTE["navy"]}">{html.escape(title)}</text>',
    ]
    group_colors = [PALETTE["indigo"], PALETTE["teal"], PALETTE["amber"], PALETTE["sky"]]

    for edge in edges:
        source = positions.get(edge["source"])
        target = positions.get(edge["target"])
        if not source or not target:
            continue
        mx, my = (source[0] + target[0]) / 2, (source[1] + target[1]) / 2
        shapes.append(
            f'<line x1="{source[0]:.1f}" y1="{source[1]:.1f}" '
            f'x2="{target[0]:.1f}" y2="{target[1]:.1f}" '
            f'stroke="{PALETTE["line"]}" stroke-width="3" '
            'marker-end="url(#arrow)"/>'
        )
        if edge["label"]:
            shapes.append(
                f'<rect x="{mx - 55:.1f}" y="{my - 15:.1f}" width="110" height="24" '
                f'rx="10" fill="#FFFFFF" stroke="{PALETTE["line"]}"/>'
                + _text_lines(mx, my + 3, _wrap(edge["label"], 16), PALETTE["navy"], 12)
            )

    for index, node in enumerate(nodes):
        x, y = positions[node["id"]]
        is_center = node["id"] == center["id"]
        width_node = 170 if is_center else 150
        height_node = 74
        color = PALETTE["indigo"] if is_center else group_colors[index % len(group_colors)]
        shapes.append(
            f'<rect x="{x - width_node / 2:.1f}" y="{y - height_node / 2:.1f}" '
            f'width="{width_node}" height="{height_node}" rx="14" '
            f'fill="{color}" stroke="{PALETTE["navy"]}" stroke-width="{3 if is_center else 2}"/>'
            + _text_lines(
                x,
                y - (len(_wrap(node["label"])) - 1) * 10,
                _wrap(node["label"]),
                "#FFFFFF",
                16,
            )
        )

    shapes.append(
        f'<rect x="24" y="575" width="932" height="28" rx="8" fill="#FFFFFF" '
        f'stroke="{PALETTE["line"]}"/>'
        f'<text x="490" y="595" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="14" fill="{PALETTE["navy"]}">{html.escape(source_caption)}</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" '
        'orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#CBD5E1"/></marker></defs>'
        + "".join(shapes)
        + "</svg>"
    )


def render_flowchart(data: dict[str, Any], title: str, source_caption: str) -> str:
    width, height = 980, 660
    steps = data["steps"][:12]
    top = 70
    y_step = 92
    shapes = [
        f'<rect width="{width}" height="{height}" rx="16" fill="{PALETTE["light"]}"/>',
        f'<text x="490" y="42" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="24" font-weight="700" fill="{PALETTE["navy"]}">{html.escape(title)}</text>',
    ]
    for index, step in enumerate(steps):
        y = top + index * y_step
        label_lines = _wrap(f"{index + 1}. {step['label']}", 34)
        shape = str(step.get("shape", "process")).lower()
        if index == 0:
            shapes.append(
                f'<rect x="390" y="{y - 32}" width="200" height="64" rx="32" '
                f'fill="#DCFCE7" stroke="{PALETTE["teal"]}" stroke-width="3"/>'
            )
        elif index == len(steps) - 1:
            shapes.append(
                f'<rect x="390" y="{y - 32}" width="200" height="64" rx="32" '
                f'fill="#FEE2E2" stroke="#B91C1C" stroke-width="3"/>'
            )
        elif shape == "decision":
            points = f"490,{y - 42} 560,{y} 490,{y + 42} 420,{y}"
            shapes.append(
                f'<polygon points="{points}" fill="#FEF3C7" '
                f'stroke="{PALETTE["amber"]}" stroke-width="3"/>'
            )
        else:
            shapes.append(
                f'<rect x="390" y="{y - 32}" width="200" height="64" rx="10" '
                f'fill="#EEF2FF" stroke="{PALETTE["indigo"]}" stroke-width="3"/>'
            )
        shapes.append(
            _text_lines(490, y - (len(label_lines) - 1) * 10, label_lines, PALETTE["navy"], 16)
        )
        if index + 1 < len(steps):
            shapes.append(
                f'<line x1="490" y1="{y + 42}" x2="490" y2="{y + y_step - 42}" '
                f'stroke="{PALETTE["indigo"]}" stroke-width="3" marker-end="url(#arrow)"/>'
            )

    shapes.append(
        f'<text x="490" y="638" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="14" fill="{PALETTE["navy"]}">{html.escape(source_caption)}</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" '
        'orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#4F46E5"/></marker></defs>'
        + "".join(shapes)
        + "</svg>"
    )


def render_revision_sheet(data: dict[str, Any], source_caption: str) -> str:
    width, height = 980, 620
    topic = data["topic"]
    definitions = data["definitions"][:6]
    remember = data["remember"][:3]
    shapes = [
        f'<rect width="{width}" height="{height}" rx="16" fill="{PALETTE["light"]}"/>',
        f'<rect x="40" y="40" width="900" height="70" rx="12" fill="{PALETTE["navy"]}"/>',
        f'<text x="490" y="84" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="26" font-weight="700" fill="#FFFFFF">{html.escape(topic)}</text>',
        f'<rect x="40" y="130" width="430" height="330" rx="12" fill="#FFFFFF" '
        f'stroke="{PALETTE["line"]}"/>',
        f'<text x="255" y="165" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="19" font-weight="700" fill="{PALETTE["indigo"]}">Key definitions</text>',
        f'<rect x="510" y="130" width="430" height="150" rx="12" fill="#ECFEFF" '
        f'stroke="{PALETTE["teal"]}" stroke-width="2"/>',
        f'<text x="725" y="165" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="19" font-weight="700" fill="{PALETTE["teal"]}">Rule / formula</text>',
        f'<rect x="510" y="300" width="430" height="160" rx="12" fill="#FFFBEB" '
        f'stroke="{PALETTE["amber"]}" stroke-width="2"/>',
        f'<text x="725" y="335" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="19" font-weight="700" fill="{PALETTE["amber"]}">Worked example</text>',
    ]
    for index, definition in enumerate(definitions):
        y = 195 + index * 42
        shapes.append(
            f'<circle cx="75" cy="{y - 5}" r="9" fill="{PALETTE["indigo"]}"/>'
            + _text_lines(95, y, _wrap(definition, 42), PALETTE["navy"], 15).replace(
                f'<text x="95.0"', '<text x="95.0" text-anchor="start"'
            )
        )
    for index, line in enumerate(_wrap(data["rule"] or "Review the defining rule.", 48)):
        shapes.append(
            _text_lines(725, 200 + index * 24, [line], PALETTE["navy"], 16)
        )
    for index, line in enumerate(_wrap(data["example"] or "Use the rule on one worked example.", 48)):
        shapes.append(
            _text_lines(725, 370 + index * 24, [line], PALETTE["navy"], 16)
        )

    shapes.append(
        f'<rect x="40" y="480" width="900" height="95" rx="12" fill="#EEF2FF" '
        f'stroke="{PALETTE["indigo"]}" stroke-width="2"/>'
        f'<text x="70" y="512" font-family="Arial, sans-serif" font-size="18" '
        f'font-weight="700" fill="{PALETTE["indigo"]}">Remember this</text>'
    )
    for index, item in enumerate(remember or ["Recall the core idea.", "Check the rule.", "Try one example."]):
        shapes.append(
            f'<text x="{70 + index * 290}" y="545" font-family="Arial, sans-serif" '
            f'font-size="15" fill="{PALETTE["navy"]}">• {html.escape(_wrap(item, 28)[0])}</text>'
        )
    shapes.append(
        f'<text x="490" y="600" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="14" fill="{PALETTE["navy"]}">{html.escape(source_caption)}</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        + "".join(shapes)
        + "</svg>"
    )


def render_storyboard_svg(topic: str, scenes: list[dict[str, str]], source_caption: str) -> str:
    width, height = 980, 660
    shapes = [
        f'<rect width="{width}" height="{height}" rx="16" fill="{PALETTE["light"]}"/>',
        f'<text x="490" y="42" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="24" font-weight="700" fill="{PALETTE["navy"]}">'
        f'{html.escape(topic)} — Lesson storyboard</text>',
    ]
    for index, scene in enumerate(scenes[:6]):
        y = 75 + index * 88
        shapes.append(
            f'<rect x="40" y="{y}" width="900" height="72" rx="12" fill="#FFFFFF" '
            f'stroke="{PALETTE["line"]}"/>'
            f'<rect x="58" y="{y + 14}" width="44" height="44" rx="22" '
            f'fill="{PALETTE["indigo"]}"/>'
            f'<text x="80" y="{y + 42}" text-anchor="middle" font-family="Arial, sans-serif" '
            f'font-size="16" font-weight="700" fill="#FFFFFF">{index + 1}</text>'
            f'<text x="125" y="{y + 24}" font-family="Arial, sans-serif" '
            f'font-size="15" font-weight="700" fill="{PALETTE["navy"]}">Narration</text>'
            f'<text x="125" y="{y + 48}" font-family="Arial, sans-serif" '
            f'font-size="14" fill="{PALETTE["navy"]}">'
            f'{html.escape(scene["script"][:80])}</text>'
            f'<text x="700" y="{y + 24}" font-family="Arial, sans-serif" '
            f'font-size="15" font-weight="700" fill="{PALETTE["teal"]}">Suggested visual</text>'
            f'<text x="700" y="{y + 48}" font-family="Arial, sans-serif" '
            f'font-size="14" fill="{PALETTE["navy"]}">'
            f'{html.escape(scene["visual"][:60])}</text>'
        )
    shapes.append(
        f'<text x="490" y="640" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="14" fill="{PALETTE["navy"]}">{html.escape(source_caption)}</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        + "".join(shapes)
        + "</svg>"
    )
