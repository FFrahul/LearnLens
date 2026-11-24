"""Generate clearly labelled synthetic LearnLens evaluation samples."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pyttsx3
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
FFMPEG = shutil.which("ffmpeg") or r"C:\ffmeg\bin\ffmpeg.exe"
GENERATED_AT = date.today().isoformat()

PDF_TOPICS = [
    ("hierarchical_clustering_synthetic.pdf", "Hierarchical Clustering", "easy"),
    ("distance_metrics_synthetic.pdf", "Minkowski, Euclidean and Manhattan Distance", "easy"),
    ("kmeans_synthetic.pdf", "K-Means Clustering", "medium"),
    ("pca_synthetic.pdf", "Principal Component Analysis", "medium"),
    ("neural_networks_synthetic.pdf", "Neural Networks Basics", "medium"),
    ("rag_and_agents_synthetic.pdf", "RAG, Transformers and Agents", "hard"),
]

PPT_TOPICS = [
    ("hierarchical_clustering_synthetic.pptx", "Hierarchical Clustering", "easy"),
    ("kmeans_pca_synthetic.pptx", "K-Means and PCA", "medium"),
    ("diagram_only_synthetic.pptx", "Transformer Diagram Notes", "hard"),
    ("rag_langchain_synthetic.pptx", "RAG and LangChain", "hard"),
]

IMAGE_SPECS = [
    ("handwritten_notes_synthetic.png", "Handwritten-style clustering notes", "hard"),
    ("chart_synthetic.png", "Elbow chart for K selection", "medium"),
    ("dendrogram_synthetic.png", "Hierarchical clustering dendrogram", "easy"),
    ("transformer_diagram_synthetic.png", "Transformer block diagram", "hard"),
    ("rag_flow_synthetic.png", "RAG retrieval flowchart", "medium"),
    ("table_synthetic.png", "Distance measure table", "easy"),
    ("low_quality_ocr_synthetic.png", "Low quality OCR text", "hard"),
    ("supervised_unsupervised_synthetic.png", "Supervised versus unsupervised learning", "easy"),
]

VIDEO_SPECS = [
    ("hierarchical_clustering_synthetic.mp4", "Hierarchical Clustering", "clear slides, narrated"),
    ("kmeans_synthetic.mp4", "K-Means", "weak audio synthetic"),
    ("rag_synthetic.mp4", "RAG", "slide-heavy, no speech"),
    ("pca_synthetic.mp4", "PCA", "short narrated lesson"),
]


def draw_text_lines(draw: ImageDraw.ImageDraw, lines: list[str], start_y: int = 40) -> None:
    font = _font(34)
    y = start_y
    for line in lines:
        draw.text((40, y), line, fill="#172554", font=font)
        y += 52


def _font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def build_pdfs() -> list[dict]:
    folder = SAMPLES / "pdf"
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for filename, topic, difficulty in PDF_TOPICS:
        path = folder / filename
        pdf = canvas.Canvas(str(path))
        pdf.setTitle(topic)
        pdf.setAuthor("LearnLens Synthetic Dataset")
        pdf.drawString(50, 800, f"SYNTHETIC - {topic}")
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 760, topic)
        pdf.setFont("Helvetica", 11)
        lines = [
            f"This synthetic open-license sample teaches {topic}.",
            "Key fact 1: The material is generated for LearnLens QA testing.",
            "Key fact 2: Each statement is intentionally source-grounded.",
            "Key fact 3: The content includes equations and a short worked example.",
            "Hierarchical clustering merges nearby observations until a dendrogram is complete.",
            "Minkowski distance generalizes Euclidean and Manhattan distances.",
            "K-Means minimizes within-cluster squared error.",
            "PCA finds orthogonal directions that capture variance.",
            "Supervised learning uses labeled examples; unsupervised learning does not.",
            "RAG retrieves grounded context before answer generation.",
        ]
        y = 720
        for line in lines:
            pdf.drawString(55, y, line[:92])
            y -= 24
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(55, 440, "Worked example:")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(55, 416, "For points (1,1) and (4,5), Euclidean distance is 5.")
        pdf.drawString(55, 392, "Formula: d(x,y) = sqrt((x2-x1)^2 + (y2-y1)^2)")
        pdf.showPage()
        pdf.drawString(50, 800, f"SYNTHETIC - {topic}")
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(55, 760, "Two-column review page")
        pdf.setFont("Helvetica", 10)
        left = [
            "Left column:",
            "Definition",
            "Distance metric",
            "Cluster linkage",
            "Variance",
        ]
        right = [
            "Right column:",
            "Source-grounded answer",
            "Expected citation",
            "Worked calculation",
            "Common misconception",
        ]
        for index, line in enumerate(left):
            pdf.drawString(55, 720 - index * 28, line)
        for index, line in enumerate(right):
            pdf.drawString(330, 720 - index * 28, line)
        pdf.save()
        records.append({
            "filename": filename,
            "title": f"Synthetic {topic}",
            "topic": topic,
            "difficulty": difficulty,
            "type": "PDF",
            "author": "LearnLens Synthetic Dataset",
            "source_url": "LOCAL_GENERATED",
            "license": "SYNTHETIC - created for LearnLens; no third-party copyrighted content",
            "date_accessed": GENERATED_AT,
            "weakness": "text extraction, equations, two-column reading and OCR robustness",
        })
    return records


def build_ppts() -> list[dict]:
    folder = SAMPLES / "ppt"
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for filename, topic, difficulty in PPT_TOPICS:
        path = folder / filename
        presentation = Presentation()
        presentation.core_properties.title = f"Synthetic {topic}"
        presentation.core_properties.author = "LearnLens Synthetic Dataset"
        for slide_number in range(1, 9):
            slide = presentation.slides.add_slide(presentation.slide_layouts[1])
            slide.shapes.title.text = f"{topic} - Slide {slide_number}"
            body = slide.shapes.placeholders[1].text_frame
            body.text = f"Key idea {slide_number}: {topic}"
            body.add_paragraph().text = "Source-grounded synthetic bullet"
            body.add_paragraph().text = "Expected citation: this slide"
            if slide_number in (3, 6):
                notes = slide.notes_slide.notes_text_frame
                notes.text = f"Speaker note {slide_number}: Explain the {topic} concept with a worked example."
        presentation.save(str(path))
        records.append({
            "filename": filename,
            "title": f"Synthetic {topic}",
            "topic": topic,
            "difficulty": difficulty,
            "type": "PPTX",
            "author": "LearnLens Synthetic Dataset",
            "source_url": "LOCAL_GENERATED",
            "license": "SYNTHETIC - created for LearnLens; no third-party copyrighted content",
            "date_accessed": GENERATED_AT,
            "weakness": "titles, bullets, speaker notes, charts and image-only slides",
        })
    return records


def build_images() -> list[dict]:
    folder = SAMPLES / "images"
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for filename, title, difficulty in IMAGE_SPECS:
        path = folder / filename
        image = Image.new("RGB", (1000, 700), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((20, 20, 980, 680), outline="#4F46E5", width=4)
        draw_text_lines(draw, [f"SYNTHETIC - {title}", "Topic: educational QA", "Source: LearnLens sample"])
        if "chart" in filename or "table" in filename:
            draw.line((140, 560, 850, 560), fill="#64748B", width=3)
            draw.line((140, 560, 140, 180), fill="#64748B", width=3)
            for x, y in [(220, 500), (350, 420), (480, 360), (610, 300), (740, 250)]:
                draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill="#0F766E")
        elif "diagram" in filename or "flow" in filename or "dendrogram" in filename:
            for x, y, label in [(500, 150, "START"), (500, 300, "PROCESS"), (500, 450, "END")]:
                draw.ellipse((x - 100, y - 50, x + 100, y + 50), outline="#0F766E", width=4)
                draw.text((x - 45, y - 12), label, fill="#172554", font=_font(24))
            draw.line((500, 200, 500, 250), fill="#0F766E", width=4)
            draw.line((500, 350, 500, 400), fill="#0F766E", width=4)
        image.save(path)
        records.append({
            "filename": filename,
            "title": f"Synthetic {title}",
            "topic": title,
            "difficulty": difficulty,
            "type": "IMAGE",
            "author": "LearnLens Synthetic Dataset",
            "source_url": "LOCAL_GENERATED",
            "license": "SYNTHETIC - created for LearnLens; no third-party copyrighted content",
            "date_accessed": GENERATED_AT,
            "weakness": "captioning, OCR accuracy, handwriting, charts and diagrams",
        })
    return records


def synthesize_tts(text: str, wav_path: Path) -> bool:
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 155)
        engine.save_to_file(text, str(wav_path))
        engine.runAndWait()
        return wav_path.exists()
    except Exception:
        return False


def build_videos() -> list[dict]:
    folder = SAMPLES / "videos"
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for filename, topic, difficulty in VIDEO_SPECS:
        path = folder / filename
        wav = folder / f"{path.stem}.wav"
        narration = (
            f"This synthetic lesson explains {topic}. "
            f"Hierarchical clustering merges clusters. "
            f"K means minimizes squared error. "
            f"PCA finds directions of maximum variance. "
            f"RAG combines retrieval with answer generation."
        )
        has_voice = synthesize_tts(narration, wav)
        if filename == "rag_synthetic.mp4":
            command = [
                FFMPEG, "-y", "-f", "lavfi", "-i",
                "color=c=navy:s=960x540:d=36",
                "-vf", "drawtext=text='SYNTHETIC RAG SLIDE':fontcolor=white:fontsize=38:x=150:y=240",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
            ]
        else:
            command = [FFMPEG, "-y"]
            if has_voice:
                command.extend(["-i", str(wav)])
            command.extend([
                "-f", "lavfi", "-i", "color=c=navy:s=960x540:d=36",
                "-vf", "drawtext=text='SYNTHETIC " + topic.replace("'", "") + "':fontcolor=white:fontsize=38:x=150:y=240",
            ])
            if has_voice:
                command.extend(["-shortest"])
            command.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p"])
            if has_voice:
                command.extend(["-c:a", "aac"])
            command.append(str(path))
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if wav.exists():
            wav.unlink()
        if result.returncode != 0:
            raise RuntimeError("Video generation failed: " + result.stderr[-500:])
        records.append({
            "filename": filename,
            "title": f"Synthetic {topic} lecture",
            "topic": topic,
            "difficulty": difficulty,
            "type": "VIDEO",
            "author": "LearnLens Synthetic Dataset",
            "source_url": "LOCAL_GENERATED",
            "license": "SYNTHETIC - created for LearnLens; no third-party copyrighted content",
            "date_accessed": GENERATED_AT,
            "weakness": "timestamping, speech quality, silence and slide-heavy video",
        })
    return records


def build_gold(complete_records: list[dict]) -> None:
    folder = SAMPLES / "gold"
    folder.mkdir(parents=True, exist_ok=True)
    for record in complete_records:
        source = record["filename"]
        stem = Path(source).stem
        topic = record["topic"]
        questions = []
        for number in range(1, 11):
            if record["type"] == "PDF":
                expected = "Page 1" if number <= 7 else "Page 2"
            elif record["type"] == "PPTX":
                expected = f"Slide {((number - 1) % 8) + 1}"
            elif record["type"] == "VIDEO":
                start = (number - 1) * 3
                expected = f"{start:02d}:00-{start + 3:02d}:00"
            else:
                expected = "Whole image"
            questions.append({
                "id": f"{stem}_{number:02d}",
                "question": f"What is key fact {number} about {topic}?",
                "expected_source": expected,
                "expected_key_facts": [
                    f"{topic} key fact {number}",
                    "Definition",
                    "Worked example",
                ],
                "difficulty": record["difficulty"],
            })
        type_prefix = record["type"].lower()
        (folder / f"{type_prefix}_{stem}.json").write_text(
            json.dumps({
                "source": source,
                "topic": topic,
                "questions": questions,
            }, indent=2),
            encoding="utf-8",
        )


def main() -> None:
    records = build_pdfs() + build_ppts() + build_images() + build_videos()
    build_gold(records)
    manifest = {
        "generated_at": GENERATED_AT,
        "status": "SYNTHETIC",
        "license": "LearnLens synthetic data created for this repository; no third-party copyrighted text or media",
        "counts": {
            "pdf": len(PDF_TOPICS),
            "ppt": len(PPT_TOPICS),
            "images": len(IMAGE_SPECS),
            "videos": len(VIDEO_SPECS),
        },
        "files": records,
    }
    (SAMPLES / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest["counts"]))


if __name__ == "__main__":
    main()
