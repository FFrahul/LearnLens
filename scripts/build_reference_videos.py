"""Verify and catalog YouTube reference videos using YouTube oEmbed."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
DATE_ACCESSED = date.today().isoformat()

CANDIDATES = {
    "Hierarchical Clustering": [
        ("7xHsRkOdVwo", 679, "clear slides and hierarchical merging"),
        ("8QCBl-xdeZI", 502, "easy-to-follow cluster dendrograms"),
        ("4b5d3muPQmA", 510, "comparison with K-means"),
    ],
    "Distance Metrics": [
        ("gwtTM9M6ugU", 0, "Euclidean, Manhattan and Minkowski comparison"),
        ("PdiHBIl-5KQ", 0, "distance formulas and a worked example"),
        ("ofIfXMPem2M", 0, "machine-learning distance lesson"),
    ],
    "K-Means": [
        ("4b5d3muPQmA", 510, "clear algorithm explanation"),
        ("RDZUdRSDOok", 570, "comparison with DBSCAN"),
        ("5FpsGnkbEpM", 471, "numerical worked example"),
    ],
    "PCA": [
        ("HMOI_lkzW08", 365, "five-minute PCA overview"),
        ("FgakZw6K1QQ", 1318, "step-by-step heavy math"),
        ("FD4DeN81ODY", 388, "visual PCA explanation"),
    ],
    "Supervised vs Unsupervised": [
        ("1FZ0A1QCMWc", 387, "broad learning-category comparison"),
        ("W01tIRP_Rqs", 428, "IBM Technology explanation"),
        ("fM8XdC1EweU", 451, "real-life examples"),
    ],
    "Neural Networks": [
        ("aircAruvnKk", 1120, "visual neural-network fundamentals"),
        ("jmmW0F0biz0", 272, "short beginner summary"),
        ("LPZh9BOjkQs", 478, "LLM context for neural-network basics"),
    ],
    "Transformers": [
        ("wjZofJX0v4M", 1634, "clear transformer architecture math"),
        ("eMlx5fFNoYc", 1570, "attention mechanism step-by-step"),
        ("ZhAz268Hdpw", 3451, "long detailed transformer lecture"),
    ],
    "RAG": [
        ("T-D1OfcDW1M", 0, "short RAG conceptual overview"),
        ("Ty8gcCKuwNI", 0, "RAG architecture in 15 minutes"),
        ("2p4wHxJJ7Rs", 7200, "long RAG course-style lecture"),
    ],
    "LangChain": [
        ("nlz9j-r0U9U", 2264, "LangChain beginner introduction"),
        ("cQUUkZnyoD0", 3886, "generative-AI tutorial"),
        ("o126p1QN_RI", 7689, "long RAG and LangChain crash course"),
    ],
    "AI Agents": [
        ("EsTrWCV0Ph4", 7995, "two-hour AI-agent course"),
        ("w0H1-b044KY", 13840, "agent building and sales guidance"),
        ("EH5jx5qPabU", 1558, "first agent in 25 minutes"),
    ],
}


def seconds_label(seconds: int) -> str:
    if seconds <= 0:
        return "UNVERIFIED duration"
    minutes, remaining = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{remaining:02d}"
    return f"{minutes}:{remaining:02d}"


def fetch_oembed(video_id: str) -> dict | None:
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    params = urllib.parse.urlencode({"url": watch_url, "format": "json"})
    request = urllib.request.Request(
        f"https://www.youtube.com/oembed?{params}",
        headers={"User-Agent": "LearnLens-Evaluation/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status != 200:
                return None
            data = json.loads(response.read().decode("utf-8"))
        return {
            "title": str(data["title"]).strip(),
            "channel": str(data["author_name"]).strip(),
        }
    except Exception:
        return None


def main() -> None:
    records = []
    for topic, candidates in CANDIDATES.items():
        for video_id, duration, purpose in candidates:
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            metadata = fetch_oembed(video_id)
            if metadata is None:
                continue
            records.append({
                "topic": topic,
                "title": metadata["title"],
                "channel": metadata["channel"],
                "url": watch_url,
                "duration": seconds_label(duration),
                "language": "English",
                "why_useful": purpose,
                "licence_status": "UNVERIFIED from page metadata; link only",
                "download_status": "link only - download only with explicit reuse permission",
                "date_accessed": DATE_ACCESSED,
                "status": "VERIFIED_LINK",
            })

    SAMPLES.mkdir(parents=True, exist_ok=True)
    (SAMPLES / "reference_videos.json").write_text(
        json.dumps({"date_accessed": DATE_ACCESSED, "videos": records}, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Reference Videos",
        "",
        "These are verified YouTube links; no video files are committed.",
        "Creative-Commons status is not assumed. Standard licence/CC status must",
        "be checked on the YouTube page before downloading.",
        "",
    ]
    current_topic = None
    for record in records:
        if record["topic"] != current_topic:
            current_topic = record["topic"]
            lines.extend(["", f"## {current_topic}", ""])
        lines.extend([
            f"### {record['title']}",
            f"- Channel: {record['channel']}",
            f"- URL: {record['url']}",
            f"- Duration: {record['duration']}",
            f"- Language: {record['language']}",
            f"- Why useful: {record['why_useful']}",
            f"- Licence: {record['licence_status']}",
            f"- Download: {record['download_status']}",
            f"- Verified: {record['date_accessed']}",
            "",
        ])
    (SAMPLES / "reference_videos.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )
    print(json.dumps({"verified_references": len(records)}))


if __name__ == "__main__":
    main()
