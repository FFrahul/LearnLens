# LearnLens Architecture

## Scope

LearnLens is a single-process Streamlit application. Uploaded course material is
processed in the browser session, while learner state and video transcript
caches are stored locally in SQLite. Inference is delegated only to Ollama
addresses accepted by `local_ai.py` (`localhost`, loopback, or the Docker host
bridge).

## Runtime flow

```text
PDF/PPTX/video upload
        |
        +-- PyMuPDF / python-pptx / Faster-Whisper
        |
        +-- knowledge units with page, slide, or timestamp citations
        |
        +-- 768-dimensional deterministic feature hashing
        +-- BM25-style lexical score (unified retrieval)
        |
        +-- planner/verifier evidence gate
        |
        +-- Ollama local text generation
        |
        +-- cited answer, refusal, quiz, or learner update
```

`app.py` owns Streamlit orchestration, extraction, retrieval, assessment, and
the UI. `local_ai.py` contains the Ollama client, local feature hashing, image
payload handling, and lazy Faster-Whisper transcription. `persistence.py`
provides `learner_state` and `video_transcripts` SQLite tables. The smaller
modules provide knowledge graphs, recovery plans, deterministic agent workflow,
visual-learning SVG/script helpers, and guarded CPU experiments.

## Data and state

- PDF, slide, and transcript units contain text plus a stable citation.
- Retrieval uses top-k scope-filtered units; the configured constants are
  1200-character chunks, 200-character overlap, top-k 4, and a 0.05 minimum
  retrieval score.
- Learner state is keyed by `LEARNLENS_PROFILE_ID` and defaults to `local`.
- Existing `learner_state.json` is imported when present; new writes use
  `learnlens.db`.
- Video transcripts are cached by file signature and Whisper model size.

## Optional paths and limitations

- Vision Q&A is optional and requires an installed Ollama vision model
  (default `llava:7b`).
- Whisper attempts CUDA and falls back to CPU; it is not guaranteed to use the
  GPU on every Windows installation.
- Feature hashing is lexical, not a semantic embedding model.
- RAGAS evaluation uses Ollama's local OpenAI-compatible endpoint, but a full
  end-to-end RAGAS run is not part of the verified baseline.
- Docker packages the app but expects Ollama to remain on the host through
  `host.docker.internal`; it is not a cloud deployment.
