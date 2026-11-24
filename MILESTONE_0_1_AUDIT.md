# Milestones 0–1 audit and implementation status

## Milestone 0 — repository and machine audit

- Repository baseline: `35f1370` on `main`; the worktree was clean before
  modernization edits. Work is now on `feature/learnlens-2.0`.
- Python: 3.13.7; existing virtual environment has Streamlit 1.67.0, RAGAS
  0.4.3, and the application's remaining dependencies installed.
- Hardware observed: Intel i7-13700HX, 15.6 GiB visible RAM (about 3 GiB free
  at audit time), NVIDIA RTX 4060 Laptop GPU (about 4 GiB reported), and about
  62 GiB free on C:.
- Ollama 0.40.16 is installed. Existing local models include `llama3.2:1b`
  (1.3 GB), `llama3.2:latest` (2.0 GB), `qwen2.5:latest` (4.7 GB),
  `qwen2.5-coder:7b` (4.7 GB), `glm-4.7-flash:latest` (19 GB), and
  `llava:7b` (4.7 GB). Text and vision models were confirmed through Ollama's
  local API.
- Original app required Gemini for generation, embeddings, image/video
  processing, tagging and RAGAS judging. PDF and PowerPoint text extraction
  existed, but did not operate without an API key because those paths called
  Gemini.
- MIT license and original attribution remain in place. The `.env` file was
  not manually inspected, printed, or edited. It is git-ignored.

## Milestone 1 — local-only provider and startup

- Removed Gemini SDK use and the mandatory Gemini startup dependency.
- Added `local_ai.py`: Ollama text generation restricted to loopback addresses,
  bounded generation settings, actionable unavailable-model errors, and
  deterministic 768-dimensional local lexical feature-hashing vectors.
- Uses the already installed `llama3.2:1b` by default. Local settings can be
  configured with `OLLAMA_HOST` and `LEARNLENS_OLLAMA_MODEL`; no key is needed.
- App status reports whether the configured local model is installed.
- Added a citation-preservation fallback that appends only citations from
  retrieved PDF/slide passages when the local model omits them. It does not
  append citations to recognized refusals.
- PDF and PowerPoint text extraction, retrieval and local text Q&A are
  supported. Video speech is transcribed locally with Faster-Whisper and
  indexed as timestamped transcript chunks. Image Q&A uses the installed
  local Ollama vision model; no uploaded image/video is sent to a hosted
  service.
- RAGAS judging is configured for the local Ollama OpenAI-compatible endpoint;
  its loopback OpenAI-compatible chat endpoint was confirmed to return `OK`,
  but the complete RAGAS scoring pipeline has not yet been validated end to end.
- Updated README and `.env.example` for local-only configuration. Removed
  `google-genai` from requirements. The `openai` package remains only for
  RAGAS's Ollama-compatible local endpoint.

## Validation completed

- `.venv\Scripts\python.exe -m py_compile app.py local_ai.py tests\test_local_ai.py`
  — passed before app-level tests were added.
- `python -m unittest discover -s tests -v` — 5 local provider tests passed
  (deterministic vector hashing, loopback restriction, mocked local generation,
  JSON mode and unreachable-service error).
- Direct Ollama client call to `http://127.0.0.1:11434` using the installed
  `llama3.2:1b` — returned `OK`.
- Streamlit `AppTest` with an empty Gemini key — 9 tabs rendered, 0 app
  exceptions.
- Streamlit `AppTest` uploaded and indexed `sample_materials\kmeans_notes.pdf`
  (2 chunks, 768-dimensional vectors) and
  `sample_materials\Clustering_Lecture.pptx` — both had 0 app exceptions.
- Streamlit `AppTest` asked “What does k-means minimize?” against the sample PDF
  using the local model — 0 app exceptions and no UI errors. The model's
  response was verbose and omitted a citation; the app then appended citations
  from the retrieved pages. This confirms the path but also shows local answer
  quality still needs evaluation.
- `.venv\Scripts\python.exe -m pytest -q` — **24 tests passed**, including
  app startup without a key, local PDF indexing/answer citation preservation,
  refusal for an unrelated query without invoking the model, and PPTX text
  indexing, plus mocked timestamped video transcription.
- Sample `hierarchical_clustering_lecture.mp4` — **17 timestamped transcript
  segments** produced locally. GPU was attempted and automatically fell back
  to CPU because the installed CUDA runtime lacks `cublas64_12.dll`.
- `.venv\Scripts\python.exe -m py_compile app.py local_ai.py tests\test_local_ai.py tests\test_local_app.py`
  — passed.
- `.venv\Scripts\python.exe -m pip check` and `git diff --check` — passed.
- Source scan found no Gemini SDK imports, key references, hosted AI endpoints,
  or Files API calls in Python source or dependency manifests.

## Current gaps and next work

- Rerun all tests, validate PPT Q&A and local RAGAS calls, and verify that the
  app server continues to start without any API key.
- Verify/adjust answer grounding and refusal behavior; the small model may be
  verbose or add unsupported examples despite prompt constraints. Citations are
  currently appended as a retrieved-source list if the model omits them;
  sentence-level citation attribution is not guaranteed.
- Video transcription is available locally; the first run
  downloads the Faster-Whisper `tiny` model and subsequent runs reuse it.
  The model, beam size and CPU thread count are configurable for speed versus
  accuracy.
- Unified retrieval now combines deterministic local vector similarity with
  BM25-style lexical matching; no hosted or additional embedding service is
  required.
- Knowledge graph JSON can be exported locally, and sequence-model readiness
  is gated on measured sample/topic counts rather than producing unsupported
  DNN/LSTM claims.
- Semantic model embeddings are not implemented. Current feature hashing is a
  deterministic lexical baseline, not semantic embeddings.
- PyTorch CPU DNN and LSTM baselines are available behind the measured
  readiness gate; production deployment packaging remains outside this local
  milestone.
- No claim is made that LearnLens AI 2.0 is complete or that all original
  multimodal features have been preserved.
