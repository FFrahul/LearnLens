"""Validate synthetic sample provenance and gold-set completeness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"


def main() -> None:
    manifest = json.loads(
        (SAMPLES / "manifest.json").read_text(encoding="utf-8")
    )
    files = manifest["files"]
    if manifest["status"] != "SYNTHETIC":
        raise RuntimeError("Manifest is not explicitly labelled SYNTHETIC.")

    counts = {"PDF": 0, "PPTX": 0, "IMAGE": 0, "VIDEO": 0}
    gold_dir = SAMPLES / "gold"
    prefixes = {"PDF": "pdf_", "PPTX": "pptx_", "IMAGE": "image_", "VIDEO": "video_"}
    folders = {"PDF": "pdf", "PPTX": "ppt", "IMAGE": "images", "VIDEO": "videos"}

    for record in files:
        counts[record["type"]] += 1
        path = SAMPLES / folders[record["type"]] / record["filename"]
        if not path.exists():
            raise RuntimeError(f"Missing sample: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise RuntimeError(f"Checksum mismatch: {record['filename']}")
        if record["license"] != "SYNTHETIC - created for LearnLens; no third-party copyrighted content":
            raise RuntimeError(f"Licence not explicit: {record['filename']}")

        gold_name = prefixes[record["type"]] + Path(record["filename"]).stem + ".json"
        gold_path = gold_dir / gold_name
        if not gold_path.exists():
            raise RuntimeError(f"Missing gold set: {gold_name}")
        gold = json.loads(gold_path.read_text(encoding="utf-8"))
        if len(gold["questions"]) < 10:
            raise RuntimeError(f"{gold_name} has fewer than 10 questions.")

    if counts["PDF"] < 6 or counts["PPTX"] < 4 or counts["IMAGE"] < 8 or counts["VIDEO"] < 4:
        raise RuntimeError(f"Minimum sample counts not met: {counts}")

    references = json.loads(
        (SAMPLES / "reference_videos.json").read_text(encoding="utf-8")
    )
    if len(references["videos"]) < 30:
        raise RuntimeError("Fewer than 30 verified reference videos.")
    if any(record["status"] != "VERIFIED_LINK" for record in references["videos"]):
        raise RuntimeError("A reference link was not verified.")

    print(json.dumps({
        "counts": counts,
        "gold_sets": len(list(gold_dir.glob("*.json"))),
        "reference_videos": len(references["videos"]),
    }))


if __name__ == "__main__":
    main()
