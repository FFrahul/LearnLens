# Testing

## Verified baseline

From the repository root, the current environment completed:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# 29 passed
```

Python compilation also completed for `app.py`, `local_ai.py`, persistence,
knowledge, recovery, workflow, experiment, visual-learning, and validation
modules. The test suite covers local AI behavior, app-level PDF/PPTX paths,
mocked video transcription, SQLite persistence, knowledge/recovery logic,
experiments, visual helpers, and validation helpers.

## Windows validation command

```powershell
.\.venv\Scripts\python.exe validate_local.py
```

This checks required imports, compiles core files, runs pytest, runs `pip check`,
and probes Ollama on loopback. Ollama reachability is reported separately so
the offline unit tests can still run when Ollama is stopped.

## Manual smoke test

1. Start Ollama and confirm the configured model appears in `ollama list`.
2. Run `streamlit run app.py` or `.\run_app.ps1`.
3. Upload `sample_materials\kmeans_notes.pdf` and
   `sample_materials\Clustering_Lecture.pptx`.
4. Ask a covered question and confirm a page/slide citation; ask an unrelated
   question and confirm refusal.
5. Upload the sample MP4 and confirm timestamped transcript citations.
6. If `llava:7b` is installed, exercise Image Understanding.

## Known gaps

The full RAGAS scoring pipeline and a completed Docker container health check
are not part of the verified 29-test baseline. Model quality, GPU use, and
download behavior require machine-specific smoke tests.
