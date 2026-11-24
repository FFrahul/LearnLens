"""Dependency-light local visual learning resource generators."""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def _safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._")
    return name or "learning_resource"


def _write_svg(output_dir: str | Path, name: str, title: str, nodes: list[str]) -> str:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    width = 900
    height = max(220, 130 * len(nodes))
    shapes = []
    for index, node in enumerate(nodes):
        y = 70 + index * 120
        label = html.escape(node[:90])
        shapes.append(
            f'<rect x="250" y="{y}" width="400" height="62" rx="12" '
            'fill="#e8f0fe" stroke="#356ae6" stroke-width="2"/>'
            f'<text x="450" y="{y + 38}" text-anchor="middle" '
            f'font-family="Arial" font-size="18" fill="#172554">{label}</text>'
        )
        if index:
            shapes.append(
                f'<path d="M450 {y - 58} V{y}" stroke="#64748b" '
                'stroke-width="2" marker-end="url(#arrow)"/>'
            )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" '
        'refX="4" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3 z" '
        'fill="#64748b"/></marker></defs>'
        f'<rect width="100%" height="100%" fill="#ffffff"/>'
        f'<text x="450" y="35" text-anchor="middle" font-family="Arial" '
        f'font-size="24" font-weight="bold">{html.escape(title)}</text>'
        + "".join(shapes)
        + "</svg>"
    )
    path = output / f"{_safe_name(name)}.svg"
    path.write_text(svg, encoding="utf-8")
    return str(path)


def generate_concept_map(topic: str, concepts: list[str], output_dir: str | Path) -> str:
    """Create a viewable concept map as a local SVG."""
    nodes = [topic] + [concept for concept in concepts if concept.strip()]
    return _write_svg(output_dir, f"{topic}_concept_map", "Concept Map", nodes[:8])


def generate_flowchart(topic: str, steps: list[str], output_dir: str | Path) -> str:
    """Create a viewable process flowchart as a local SVG."""
    nodes = [step for step in steps if step.strip()]
    if not nodes:
        nodes = [topic]
    return _write_svg(output_dir, f"{topic}_flowchart", "Process Flowchart", nodes[:8])


def generate_revision_infographic(
    topic: str, key_points: list[str], output_dir: str | Path
) -> str:
    """Create a printable revision infographic as a local SVG."""
    return _write_svg(
        output_dir,
        f"{topic}_revision",
        "Revision Infographic",
        [topic] + [point for point in key_points if point.strip()][:7],
    )


def generate_narrated_lesson_script(
    topic: str, key_points: list[str], output_dir: str | Path
) -> str:
    """Write a narration script; audio generation remains optional."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / f"{_safe_name(topic)}_lesson.txt"
    points = "\n".join(
        f"{index}. {point.strip()}"
        for index, point in enumerate(key_points, start=1)
        if point.strip()
    )
    path.write_text(
        f"Lesson: {topic}\n\nToday we will learn {topic}.\n\n"
        f"Key points:\n{points or 'Review the source material and explain the core idea.'}\n\n"
        "Pause and check your understanding before moving on.\n",
        encoding="utf-8",
    )
    return str(path)


def generate_explainer_video(
    topic: str, key_points: list[str], output_dir: str | Path, fps: int = 1
) -> str:
    """Assemble local educational slides into an MP4 using Pillow and FFmpeg."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required for local explainer-video assembly.")
    try:
        from PIL import Image, ImageDraw
    except ImportError as error:
        raise RuntimeError("Pillow is required for local explainer-video assembly.") from error

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    video_path = output / f"{_safe_name(topic)}_explainer.mp4"
    with tempfile.TemporaryDirectory(prefix="learnlens_slides_") as slide_dir:
        points = [topic] + [point for point in key_points if point.strip()][:7]
        for index, point in enumerate(points):
            image = Image.new("RGB", (1280, 720), "white")
            draw = ImageDraw.Draw(image)
            draw.text((80, 80), topic[:70], fill="#172554")
            draw.text((120, 300), point[:100], fill="#1e3a8a")
            image.save(Path(slide_dir) / f"slide_{index:03d}.png")
        command = [
            ffmpeg, "-y", "-framerate", str(fps), "-i",
            str(Path(slide_dir) / "slide_%03d.png"), "-c:v", "libx264",
            "-pix_fmt", "yuv420p", str(video_path),
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, check=False
        )
        if result.returncode:
            raise RuntimeError(
                "FFmpeg could not assemble the explainer video: "
                + (result.stderr.strip()[-500:] or "unknown error")
            )
    return str(video_path)
