# LearnLens AI Codebase Report

## 1. PROJECT OVERVIEW

LearnLens AI is a local-first Streamlit learning assistant for students. It ingests PDFs, PowerPoint slides, videos, and images; extracts text or transcripts; indexes source units; answers grounded questions with citations; generates adaptive diagnostic and assessment questions; tracks learner mastery; and creates local visual learning resources. Text generation runs through Ollama on the local machine.

**Entry point:** `app.py`

**Local command:**

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

**Docker command and URL:**

```powershell
docker compose up --build
```

```text
http://localhost:8502
```

Docker maps host port `8502` to Streamlit's container port `8501`.

## 2. FOLDER STRUCTURE

```text
learnlens-ai/
├── app.py                         Main Streamlit application and integration layer
├── local_ai.py                    Local Ollama client, embeddings, vision, Whisper
├── persistence.py                 SQLite learner and transcript persistence
├── agent_workflow.py              Query planning and evidence verification
├── assessment_fallback.py         Deterministic diagnostic-question fallback
├── knowledge_graph.py              Knowledge graph generation
├── learning_recovery.py            Weak-topic recovery planning
├── visual_learning.py              SVG, lesson-script, and MP4 generation
├── offline_evaluation.py           Offline retrieval and refusal metrics
├── experiment_readiness.py         Experiment data-readiness checks
├── sequence_experiment.py          PyTorch DNN/LSTM experiments
├── tensorflow_experiment.py        Optional TensorFlow/Keras experiments
├── validate_local.py               Syntax, test, dependency, and Ollama validation
├── run_app.ps1                     Windows validation and Streamlit launcher
├── requirements.txt                Python dependency manifest
├── .env.example                    Local configuration template
├── Dockerfile                      Docker image definition
├── docker-compose.yml               Docker runtime configuration
├── .dockerignore                   Docker build exclusions
├── .gitignore                      Git exclusions
├── README.md                       Setup and feature documentation
├── ARCHITECTURE.md                 Architecture documentation
├── MODEL_CARDS.md                  Model and limitation documentation
├── PRIVACY.md                      Local-processing and privacy documentation
├── TESTING.md                      Testing documentation
├── INSTALLATION_WINDOWS.md         Windows installation documentation
├── FEATURE_COMPARISON.md           Feature comparison
├── IMPLEMENTATION_LOG.md           Implementation history
├── LICENSE                         Project license
├── assets/                         Branding and screenshots
├── sample_materials/               Demo PDFs, slides, video, and test JSON
├── tests/                          Automated tests
└── results/                        Generated benchmark output
```

The tree omits `.git`, `.venv`, `__pycache__`, database files, generated data, and large sample media.

## 3. TECH STACK

### Runtime

- Python `3.10+`
- Tested with Python `3.13`
- Streamlit `>=1.50,<2`
- Windows local process or Docker

### Dependencies

| Library | Role |
|---|---|
| `streamlit` | Web UI, tabs, widgets, session state |
| `pymupdf` | PDF text and embedded-image extraction |
| `python-pptx` | PowerPoint text, tables, and images |
| `numpy` | Vector operations and numerical processing |
| `python-dotenv` | `.env` loading |
| `faster-whisper` | Local video transcription |
| `torch` | Faster-Whisper/PyTorch experiments |
| `ragas` | Local RAG evaluation |
| `openai` | OpenAI-compatible client pointed at local Ollama |
| `langchain-community` | Compatibility dependency for RAGAS |
| TensorFlow/Keras | Optional DNN/LSTM experiments; not in default requirements |

### Models and inference

Default text model:

```text
llama3.2:1b
```

Configured with `LEARNLENS_OLLAMA_MODEL` and `OLLAMA_HOST`. The model is called through Ollama's local `POST /api/generate` endpoint.

```json
{
  "stream": false,
  "options": {
    "num_ctx": 2048,
    "num_predict": 768,
    "temperature": 0.2
  }
}
```

The application exposes a compatibility wrapper named `client.models.generate_content(...)`, but it delegates to local Ollama rather than Gemini or another hosted API.

Default vision model:

```text
llava:7b
```

It uses Ollama with base64 image data and:

```json
{
  "num_ctx": 2048,
  "num_predict": 512,
  "temperature": 0.2
}
```

There is no neural embedding model. Embeddings are deterministic 768-dimensional feature-hashing vectors made from words and adjacent bigrams using SHA-256 buckets and L2 normalization.

Video transcription uses Faster-Whisper with the `tiny` model by default. GPU is attempted first, then CPU `int8` fallback is used.

### Persistence

SQLite database:

```text
learnlens.db
```

Tables:

- `learner_state`
- `video_transcripts`

Knowledge tags are cached in `knowledge_tags.json`.

### Environment variables

```text
OLLAMA_HOST
LEARNLENS_OLLAMA_MODEL
LEARNLENS_OLLAMA_VISION_MODEL
LEARNLENS_WHISPER_MODEL
LEARNLENS_WHISPER_GPU
LEARNLENS_WHISPER_BEAM_SIZE
LEARNLENS_WHISPER_CPU_THREADS
LEARNLENS_STATE_DB
LEARNLENS_PROFILE_ID
```

No cloud API key is required.

## 4. DATA PIPELINE

### PDFs

PyMuPDF extracts page text and embedded images. Text is chunked into 1200-character chunks with 200-character overlap. Each chunk stores file name, page number, chunk number, and image metadata, then receives a deterministic embedding.

OCR for scanned PDFs is **not found**.

### PowerPoint slides

`python-pptx` extracts text boxes, tables, and embedded pictures. One knowledge unit is created per slide. Citations use:

```text
[filename.pptx, Slide N]
```

Slide images are extracted as metadata but are not generally sent to the text model in the slide-answer path.

### Videos

Uploaded bytes are written to a temporary file and identified by SHA-256. Faster-Whisper creates timestamped transcript segments. Each segment becomes one knowledge unit containing text, filename, start time, end time, topic, and citation. Segments are cached in SQLite by video hash and Whisper model.

Citations use:

```text
[filename.mp4, 00:01 - 00:08]
```

Speaker diarization is not implemented.

### Knowledge-unit count

The count is dynamically calculated as:

```text
PDF chunks + slide records + video transcript segments
```

Thus:

```text
27 knowledge units
PDF: 2
Slides: 8
Video: 17
```

means 2 PDF chunks, 8 slides, and 17 video transcript segments. It is not hard-coded.

## 5. RETRIEVAL AND ANSWERING FLOW

The user question is converted to a feature-hash embedding. Retrieval combines cosine similarity and a custom BM25-style lexical score:

```text
0.70 * semantic similarity + 0.30 * lexical score
```

The minimum accepted retrieval score is `0.05`.

| Flow | Retrieval limit |
|---|---:|
| PDF | `TOP_K = 4` |
| Slides | `min(3, number_of_slides)` |
| Video | `min(TOP_K, number_of_video_chunks)` |
| Unified Tutor | `min(6, number_of_units)` |

The unified tutor then:

1. Filters sources by selected scope.
2. Retrieves ranked sources.
3. Rejects sources below the threshold.
4. Builds a personalized grounded prompt.
5. Sends the prompt to local Ollama.
6. Ensures citations are present.
7. Displays the answer and retrieved passages.
8. Updates learner mastery for successful answers.

### Exact unified tutor prompt

There is no separate API system-role prompt. The application sends one combined prompt:

```text
You are LearnLens AI, a personalized multimodal
learning tutor.

The student has uploaded learning materials such as
PDFs, lecture slides and videos.

A retrieval system selected the most relevant content
from the unified knowledge base.

LEARNER PROFILE:

Current level:
{learner_level}

Learning goal:
{learning_goal if learning_goal else "No specific goal provided"}

Preferred explanation style:
{explanation_style}

Topics currently needing more practice:
{weak_topics_text}

PERSONALIZATION INSTRUCTIONS:

1. Adapt the complexity of the explanation to the
   student's current level.

2. Follow this level instruction:
   {level_instruction}

3. Follow this explanation-style instruction:
   {style_instruction}

4. When relevant to the student's question, connect the
   explanation to the student's learning goal.

5. If the question relates to a weak topic, give slightly
   more explanatory support.

6. Personalization must NEVER cause you to add facts that
   are not supported by the retrieved learning material.

STRICT GROUNDING RULES:

1. Answer ONLY using the retrieved material.
2. Never invent course information.
3. Keep the answer concise (1-3 direct sentences). Do not greet
   the student or add analogies/examples absent from the source.
4. If the material does not contain enough information,
   clearly say:
   "Bu bilgi yüklenen ders materyallerinde bulunamadı."
5. Write the whole answer in the language of the STUDENT
   QUESTION below (an English question gets an English
   answer), even if the retrieved material or the learning
   goal is in another language. Only the refusal sentence
   in rule 3 is always written exactly as given.
6. Every important claim must contain its source citation.
7. Preserve the exact citation supplied below.
8. PDF sources must cite page numbers.
9. Slides must cite slide numbers.
10. Videos must cite timestamps.
11. If several sources support the answer, combine them.

RETRIEVED MATERIAL:

{context}

STUDENT QUESTION:

{question}

Answer in the language of the student question above.
```

### Exact PDF prompt

```text
You are LearnLens AI, a personalized learning assistant.

The student asked a question about uploaded learning
materials.

You have been given only the most relevant sections
retrieved by a local lexical search system.

IMPORTANT RULES:

1. Answer ONLY using the retrieved sources below.
2. Do not add outside information.
3. If the answer cannot be determined from these sources,
   clearly say that the information was not found in the
   uploaded learning material.
4. Answer in 1-3 direct sentences; do not greet the student,
   add an analogy, or invent an example.
5. Answer in the same language as the student's question.
6. Cite source(s) from the retrieved material using:

   [File name, Page X]

7. Do not invent page numbers, sources, or facts.

RETRIEVED SOURCES:

{context}

STUDENT QUESTION:

{question}
```

### Exact slide prompt

```text
You are LearnLens AI, a local text-based personalized
learning assistant.

Answer the student's question using ONLY the extracted
text from the retrieved PowerPoint slides.

RULES:

1. Use only the provided slide text.
2. Do not invent information.
3. Answer in the same language as the student's question.
4. Answer in 1-3 direct sentences; no greeting, analogy, or
   example unless the retrieved text contains it.
5. Cite relevant slides using:

   [File name, Slide X]

6. If the information cannot be found, say so. Do not invent
   facts or citations.

RETRIEVED SLIDES:

{context}

STUDENT QUESTION:

{question}
```

### Exact image prompt

```text
You are a local-only visual learning assistant.
Answer the student's question using only the supplied image.
If the image does not contain enough information, say so clearly.
Answer in 1-3 direct sentences and use the question's language.

Student question:
{question}
```

Sources are displayed as:

```text
" · ".join(source["citation"] for source in retrieved_sources)
```

## 6. LEARNER MODEL AND ADAPTIVE FEATURES

### Level

Stored in `learner_profile["level"]`:

```text
Beginner
Intermediate
Advanced
```

The level changes explanation complexity in the unified prompt.

### Diagnostic

The starting diagnostic has three source-grounded questions:

```text
Question 1: Easy
Question 2: Medium
Question 3: Hard
```

Scoring:

```text
0–1 correct -> Beginner / Easy
2 correct   -> Intermediate / Medium
3 correct   -> Advanced / Hard
```

### Next Difficulty

- Two correct answers in a row increase difficulty.
- One incorrect answer decreases difficulty.
- Values are `Easy`, `Medium`, and `Hard`.

### Topic performance

`topic_performance` stores quiz attempts, correct answers, accuracy, and history. Topics below 70% accuracy are weak topics.

### Learner mastery

`learner_mastery` stores topic-level EMA mastery. Initial mastery is `0.50`.

Quiz updates use `alpha = 0.30`, with evidence `1.0` for correct and `0.0` for incorrect.

Normal tutoring evidence uses `0.55` with `alpha = 0.05`. Explicit struggle signals use `0.35` with `alpha = 0.08`. Refused answers do not update mastery.

### Tagged units

Knowledge tags contain topic, subtopic, key concepts, and prerequisites. Tags are cached in `knowledge_tags.json`.

### State storage

Transient state is held in `st.session_state`. Learner and transcript state are persisted in `learnlens.db`.

## 7. UI STRUCTURE

Tabs are displayed in this order:

1. **Learner Profile**
   - level selectbox
   - learning-goal text area
   - explanation-style selectbox
   - Save Learning Profile
   - profile metrics
   - Start Diagnostic
   - diagnostic radio answers
   - Submit Diagnostic Answer
   - Next Diagnostic Question
   - Restart Diagnostic

2. **PDF RAG**
   - PDF uploader
   - Retry PDF processing
   - extracted content expander
   - question input
   - Ask PDF
   - retrieved passages expander

3. **Slide Understanding**
   - PowerPoint uploader
   - Retry presentation processing
   - extracted slide-content expander
   - question input
   - Ask Slides
   - retrieved slides expander

4. **Video Understanding**
   - video uploader
   - video preview
   - Retry video processing
   - timestamped-segments expander
   - question input
   - Ask Video

5. **Image Understanding**
   - image uploader
   - image preview
   - question input
   - Ask Image

6. **Unified Tutor**
   - question input
   - search-scope selectbox
   - Ask LearnLens
   - answer/refusal card
   - retrieved passages expander
   - Auto-tag missing units toggle
   - Generate tags
   - knowledge graph metrics
   - graph relationship dataframe
   - Download knowledge graph JSON
   - topic browser selectbox

7. **Adaptive Assessment**
   - assessment source selectbox
   - question type selectbox
   - topic/scope input
   - assessment metrics
   - question-generation and answer controls
   - assessment history
   - misconception displays

8. **Mastery Dashboard**
   - mastery metrics
   - topic performance tables
   - learner mastery visualization
   - misconception and recovery information

9. **Evaluation**
   - readiness metrics
   - DNN/LSTM experiment controls
   - evaluation scope
   - evaluation question
   - reference answer
   - Run Evaluation
   - benchmark scope and mode
   - benchmark execution
   - benchmark metrics and result tables

10. **Visual Studio**
    - topic input
    - key-concepts text area
    - Generate local visual resources
    - SVG downloads
    - lesson-script downloads
    - MP4 preview and download

### Session-state keys

```text
learner_profile
quiz_score
quiz_total
quiz_difficulty
quiz_correct_streak
quiz_question_number
topic_performance
quiz_history
learner_mastery
conversation_counts
persistent_state_loaded
chunks
embeddings
full_text
file_infos
document_signature
pdf_index_failure
slide_chunks
slide_embeddings
pptx_signature
slides_index_failure
video_chunks
video_embeddings
video_signature
video_file_path
video_kb_name
video_kb_failure
diagnostic_active
diagnostic_index
diagnostic_score
diagnostic_question
diagnostic_answered
diagnostic_last_correct
diagnostic_result_applied
fallback_correct_answers
visual_resources
knowledge_tags_cache
knowledge_tag_message
benchmark_report
lstm_experiment
dnn_experiment
```

The sidebar shows total knowledge units, PDF/slide/video counts, learner level, next difficulty, diagnostic status, tagged-unit progress, and the number of topics tracked in the learner model.

## 8. KEY FUNCTIONS AND CLASSES

| File | Function/class | Purpose |
|---|---|---|
| `app.py` | `extract_pdf_chunks` | Extracts and chunks PDF text |
| `app.py` | `extract_pptx_slides` | Extracts slide text, tables, and images |
| `app.py` | `create_video_knowledge_chunks` | Converts Whisper segments to source units |
| `app.py` | `build_unified_knowledge_base` | Combines PDF, slide, and video units |
| `app.py` | `retrieve_unified_sources` | Performs hybrid retrieval |
| `app.py` | `answer_unified_question` | Builds and submits grounded tutor prompt |
| `app.py` | `answer_video_question` | Retrieves and answers video questions |
| `app.py` | `answer_slide_question` | Answers slide questions |
| `app.py` | `generate_verified_assessment_question` | Generates validated assessment questions |
| `app.py` | `record_quiz_mastery` | Updates mastery from quiz answers |
| `app.py` | `record_conversation_mastery` | Updates mastery from tutoring interactions |
| `local_ai.py` | `OllamaLocalAI` | Local Ollama HTTP client |
| `local_ai.py` | `feature_hash_embedding` | Creates deterministic embeddings |
| `local_ai.py` | `LocalVideoTranscriber` | Faster-Whisper wrapper |
| `persistence.py` | `SQLiteStateStore` | Persists learner and transcript state |
| `agent_workflow.py` | planner/verifier functions | Plans questions and validates evidence |
| `assessment_fallback.py` | fallback generator | Creates deterministic source-grounded MCQs |
| `knowledge_graph.py` | graph builder | Builds topics, concepts, and prerequisite edges |
| `learning_recovery.py` | recovery planner | Creates weak-topic study steps |
| `visual_learning.py` | visual generators | Creates local SVG, scripts, and MP4 resources |

## 9. KNOWN PROBLEMS

### Video summaries return only four source chunks

The dedicated video path calls:

```python
retrieved_sources = retrieve_unified_sources(
    question,
    video_chunks,
    video_embeddings,
    min(TOP_K, len(video_chunks))
)
```

`TOP_K` is `4`, so the Video Understanding tab can provide at most four transcript segments, even when the video has 17 segments.

### Copyright refusal for “summarize the video”

The source code contains no copyright-specific refusal branch or copyright message. The application's own refusal is:

```text
Bu bilgi yüklenen ders materyallerinde bulunamadı.
```

The likely cause is:

1. “Summarize the video” retrieves only four highest-scoring segments.
2. The grounded prompt requires answers to use only retrieved material.
3. The prompt limits answers to 1–3 sentences.
4. The local Ollama model may independently produce a copyright refusal for a perceived copyrighted-summary request.
5. That model response is returned by `answer_unified_question()`.

There is no dedicated summarization mode that retrieves the full transcript. Summarization is handled like an ordinary question.

### Additional limitations

- PDF and PowerPoint images are extracted, but OCR and complete visual reasoning are not implemented.
- Speaker diarization is not implemented.
- Text-to-speech is not implemented.
- TensorFlow is optional and CPU-only in the current setup.
- The default `llama3.2:1b` model has limited context and reasoning capability.
- The unified prompt requests 1–3 sentences even for broad summary questions.
- Some learner-model update failures are swallowed after the answer is displayed.
- Browser end-to-end testing was blocked because the Playwright browser executable was unavailable.
- Ollama must be running separately.

## 10. SAMPLE DATA

The `sample_materials/` folder contains:

| File | Topic |
|---|---|
| `kmeans_notes.pdf` | K-means clustering, choosing K, elbow method, SSE |
| `Clustering_Lecture.pptx` | Introduction to clustering, distance measures, hierarchical clustering, k-means |
| `hierarchical_clustering_lecture.mp4` | Hierarchical clustering lecture transcript |
| `evaluation_testset_sample.json` | Sample retrieval/evaluation cases |

The sample PDF has 2 pages, the PowerPoint has 8 slides, and the bundled video produces 17 timestamped transcript segments.

## Five most useful files for another AI

1. `app.py`
2. `local_ai.py`
3. `persistence.py`
4. `assessment_fallback.py`
5. `requirements.txt`
