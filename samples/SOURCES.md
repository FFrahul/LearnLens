# Sample Sources

All committed files under `samples/` are **SYNTHETIC**. They were generated
locally for LearnLens evaluation and contain no third-party copyrighted text,
images or recordings.

The set covers hierarchical clustering, distance metrics, K-Means, PCA,
supervised versus unsupervised learning, neural networks, transformers, RAG,
LangChain and AI agents.

It intentionally includes:

- A two-column PDF and a worked equation
- A slide deck with repeated diagram-only slides
- Handwritten-style, chart, graph, table and low-OCR-quality images
- Narrated, weak-audio and slide-heavy short videos

No real YouTube, university, textbook or publication file is downloaded.
Reference links are maintained in `reference_videos.md` and
`reference_videos.json`.

## Provenance

| File | Origin | Licence | Date accessed | Intended weakness |
|---|---|---|---|---|
| `pdf/*.pdf` | ReportLab-generated locally | SYNTHETIC | 2026-11-22 | Text coverage, equations, reading order and OCR fallback |
| `ppt/*.pptx` | python-pptx-generated locally | SYNTHETIC | 2026-11-22 | Titles, bullets, notes, charts and image-only slides |
| `images/*.png` | Pillow-generated locally | SYNTHETIC | 2026-11-22 | Caption, OCR, handwriting, charts and diagram understanding |
| `videos/*.mp4` | FFmpeg/TTS-generated locally | SYNTHETIC | 2026-11-22 | Transcript, timestamps, silence, weak audio and slide-heavy video |

The machine-readable record is `manifest.json`. Gold question sets are in
`gold/`; filenames include the source modality to avoid collisions.
