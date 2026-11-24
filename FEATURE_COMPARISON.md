# Feature Comparison

This comparison describes the current repository, not the original hosted
implementation and not a promise of production readiness.

| Capability | Current LearnLens behavior | Status / limitation |
|---|---|---|
| PDF study | Local PyMuPDF extraction, chunking, retrieval, page citations | Implemented; figures are not semantically interpreted |
| PowerPoint study | Local text/table extraction, retrieval, slide citations | Implemented; embedded pictures are not interpreted |
| Video study | Faster-Whisper transcript chunks and timestamp citations | Implemented; CPU/GPU speed and accuracy vary |
| Image Q&A | Ollama vision model with local image payload | Optional; requires installed vision model |
| Tutor | Ollama generation over retrieved material | Implemented; small-model quality can vary |
| Refusal | Evidence threshold and deterministic refusal handling | Implemented; phrase-based and not a guarantee against every unsupported claim |
| Retrieval | Feature hashing plus BM25-style lexical score | Implemented baseline; no semantic embedding model |
| Adaptive assessment | Verified MCQ, short, and numerical questions with difficulty updates | Implemented; text-only questions |
| Learner model | EMA mastery, topic performance, conversations, recovery suggestions | Implemented heuristic; not psychometrically validated |
| Persistence | SQLite profiles and transcript cache | Implemented; local single-user storage |
| Knowledge graph | Topic/subtopic/concept/prerequisite graph and JSON export | Implemented; graph quality depends on tags |
| Agent workflow | Deterministic planner and retrieval-evidence verifier | Implemented; not distributed agents |
| Evaluation | Local RAGAS configuration, benchmark, refusal/source checks | Optional; full RAGAS run remains unverified |
| DNN/LSTM | Guarded local CPU experiments | Optional exploratory baseline, not predictive validation |
| Docker | Dockerfile and Compose host-Ollama wiring | Packaged; container health/build must be verified per machine |
| Cloud inference | None in the application path | Deliberately not provided |
| Authentication / multi-user hosting | None | Limitation |

The original application depended on hosted Gemini services. The current path
removes that runtime dependency in favor of local Ollama, local extraction,
local transcription, and local persistence. Optional model downloads and
machine-specific resource requirements still apply.
