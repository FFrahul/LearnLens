# Privacy and Data Handling

## Local-first behavior

The application is designed to keep learner data, uploaded material, retrieval,
and inference on the local machine. `OllamaLocalAI` rejects remote HTTP hosts;
accepted hosts are loopback addresses and `host.docker.internal` for the
documented local Docker setup. No API key is required.

PDF and PowerPoint extraction happens in Python. Video speech is transcribed by
Faster-Whisper. Optional image Q&A sends the image to the locally running
Ollama vision model. The first Whisper model download is an external model
download, not hosted inference; review model licenses and network policy before
using it.

## Local files

- `learnlens.db`: learner profiles and cached video transcript chunks.
- `knowledge_tags.json`: locally cached knowledge tags.
- `evaluation_results.json` / `.csv`: locally saved evaluation output.
- Temporary video files are created for transcription.
- `.env` contains local configuration and is git-ignored.

An existing `learner_state.json` can be migrated into SQLite on first run.
Uploaded material is session-scoped and normally must be uploaded again after a
refresh. The default profile is `local`; set `LEARNLENS_PROFILE_ID` to isolate
local profiles.

## Limits and user responsibility

This is single-user local software, not an authenticated or encrypted service.
Anyone with access to the machine or these files may be able to read them.
Back up or delete `learnlens.db`, caches, temporary files, and evaluation
exports as appropriate. Do not upload confidential material to a machine whose
access you do not control. LearnLens supports study and does not replace
official course information or a teacher.
