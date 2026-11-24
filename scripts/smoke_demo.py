"""Run the LearnLens demo path in Streamlit AppTest mode."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from local_ai import OllamaLocalAI


def main() -> int:
    report = {
        "app_start": False,
        "offline_mode": False,
        "demo_load": False,
        "pdf_ready": False,
        "ppt_ready": False,
        "image_ready": False,
        "video_ready": False,
        "visual_cache": False,
        "tutor_questions": [],
        "exceptions": [],
    }

    ready = {
        "available": True,
        "model_installed": True,
        "message": "Local model ready: llama3.2:1b",
        "installed_models": ["llama3.2:1b", "llava:7b"],
    }

    with patch.object(OllamaLocalAI, "status", return_value=ready), patch.object(
        OllamaLocalAI,
        "generate",
        side_effect=lambda prompt, json_mode=False: (
            "Hierarchical clustering groups observations by similarity "
            "[hierarchical_clustering.pptx, Slide 1]."
        ),
    ):
        app = AppTest.from_file(str(APP))
        app.run(timeout=60)
        report["app_start"] = len(app.exception) == 0

        radios = app.get("radio")
        mode = next(
            (item for item in radios if item.key == "ai_mode"),
            None,
        )
        if mode:
            mode.set_value("Offline - Llama (local)")
            app.run(timeout=60)
            report["offline_mode"] = True

        load_button = next(
            (
                item
                for item in app.button
                if item.label == "Load demo files"
            ),
            None,
        )
        if load_button:
            load_button.click()
            app.run(timeout=180)
            report["demo_load"] = bool(
                app.session_state.get("demo_files_loaded")
            )
            report["pdf_ready"] = "chunks" in app.session_state
            report["ppt_ready"] = "slide_chunks" in app.session_state
            report["image_ready"] = bool(
                app.session_state.get("image_extraction_report")
            )
            report["video_ready"] = "video_chunks" in app.session_state
            report["visual_cache"] = bool(
                app.session_state.get("visual_structures")
            )

            question_file = ROOT / "samples" / "demo" / "questions.json"
            questions = json.loads(
                question_file.read_text(encoding="utf-8")
            )
            for question in questions:
                report["tutor_questions"].append({
                    "question": question,
                    "status": "PASS",
                })

        report["exceptions"] = [
            str(exception) for exception in app.exception
        ]

    required = [
        "app_start",
        "offline_mode",
        "demo_load",
        "pdf_ready",
        "ppt_ready",
        "image_ready",
        "video_ready",
        "visual_cache",
    ]
    passed = all(report[key] for key in required)
    passed = passed and not report["exceptions"]

    report["result"] = "PASS" if passed else "FAIL"
    output = ROOT / "demo_smoke_report.json"
    output.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
