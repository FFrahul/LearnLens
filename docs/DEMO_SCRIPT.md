# LearnLens 3-Minute Demo Script

## Setup

1. Start Ollama:
   ```powershell
   ollama serve
   ```
2. Start the app:
   ```powershell
   .venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
   ```
3. Open http://localhost:8502.

## 3-Minute Flow

### 0:00-0:25 — Opening
Say: “LearnLens turns course files into grounded tutoring, practice and visuals.”

Show:
- The four groups: **Upload**, **Learn**, **Practice**, **Progress**
- The compact sidebar status

### 0:25-0:55 — Load Demo
Click **Load demo files** in the sidebar.

Say: “The demo bundle loads one PDF, one PPTX, one dendrogram image and one lecture video.”

Expected:
- PDF: two pages
- PPTX: eight slides
- Image: one dendrogram
- Video: timestamped transcript segments

### 0:55-1:35 — Extraction Transparency
Open **Upload > PDF**, **Slides**, **Image** and **Video**.

Say: “The report shows exactly what was parsed and chunked.”

Show a PDF page, a slide, the image text beside its preview, and a video timestamp.

### 1:35-2:15 — Tutor
Open **Learn > Unified Tutor**.

Click one suggested question:

- “What is hierarchical clustering?”
- “How should a dendrogram be read?”
- “How is hierarchical clustering different from K-Means?”

Say: “The answer uses uploaded sources and displays clickable citations.”

### 2:15-2:40 — Visual Studio
Open **Learn > Visual Studio**.

The demo structure should already be cached. Generate or inspect:

- Concept map
- Flowchart
- Revision sheet
- Lesson storyboard

Say: “These visuals are rendered from validated structure, not raw model-generated SVG.”

### 2:40-3:00 — Practice and Close
Open **Practice > Adaptive Assessment** and start one question.
Open **Progress > Mastery Dashboard**.

Close with the offline/local engine status and cite that assessment and mastery
state remain local.

## Backup Plan

- If Ollama is slow, switch to **Offline** and use short questions.
- If Gemini quota/rate limit appears, the app should fall back to Ollama.
- If transcription is slow, show the cached PDF/PPTX and pre-generated visual
  instead of replaying the video.
- If the browser reloads unexpectedly, use the **Load demo files** button
  first, then continue from Tutor.
- Keep the screenshot set in `docs/screenshots/` as a fallback. Do not improvise
  if a live action fails.

## Known Limitations

- OCR is optional and depends on Tesseract.
- PPT embedded chart text and PDF equations may not be fully interpreted.
- Local 1B JSON/visual generation can be weaker than Gemini.
- Live Gemini mode depends on key and network.
- The demo’s safest mode is Offline with the preloaded demo bundle.
