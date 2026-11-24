"""Deterministic source-grounded assessment fallback."""

import random
import re


def build_deterministic_assessment_question(
    pool_items,
    difficulty,
    question_index=0,
    seen_correct_answers=None,
):
    """Build a conservative MCQ without making another model request."""
    seen_correct_answers = {
        str(value).casefold()
        for value in (seen_correct_answers or set())
    }
    sentences = []

    for source in pool_items:
        text = str(source.get("text", "")).strip()
        citation = str(source.get("citation", "")).strip()
        if not text or not citation:
            continue

        for sentence in re.split(r"(?<=[.!?])\s+", text):
            cleaned = sentence.strip()
            if 35 <= len(cleaned) <= 260:
                sentences.append((cleaned, source))

    distinct = []
    for sentence, source in sentences:
        if not any(existing == sentence for existing, _ in distinct):
            distinct.append((sentence, source))

    if len(distinct) < 2:
        return None

    available = [
        item for item in distinct
        if item[0].casefold() not in seen_correct_answers
    ]
    if not available:
        available = distinct

    correct, source = available[
        question_index % len(available)
    ]
    alternatives = []
    candidate_items = distinct + []
    rng = random.Random(
        f"{difficulty}:{question_index}:{correct}".encode("utf-8")
    )
    rng.shuffle(candidate_items)
    for candidate, _ in candidate_items:
        if candidate != correct and candidate not in alternatives:
            alternatives.append(
                f"This claim is not supported by the cited material: "
                f"{candidate}"
            )
        if len(alternatives) == 3:
            break

    while len(alternatives) < 3:
        alternatives.append(
            "The learning material does not state this alternative."
        )

    options = [correct] + alternatives[:3]
    rng.shuffle(options)

    source_words = re.findall(r"[A-Za-z][A-Za-z-]{3,}", correct)
    focus = (
        source_words[0].title()
        if source_words
        else "the material"
    )
    question_prompts = {
        "Easy": f"Which statement presents the core idea about {focus}?",
        "Medium": f"According to the cited material, which {focus} statement is accurate?",
        "Hard": f"Which source-supported statement best explains {focus} or its result?",
    }
    question_text = question_prompts.get(
        difficulty,
        f"Which statement about {focus} is supported by the source?",
    )

    return {
        "question": question_text,
        "question_type": "MCQ",
        "options": options,
        "correct_answer": correct,
        "explanation": (
            "The correct option is stated in the cited source passage."
        ),
        "topic": "Study Material",
        "difficulty": difficulty,
        "source_citation": str(source["citation"]),
    }
