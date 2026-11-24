"""Dependency-free offline metrics for retrieval and grounded answers.

The module intentionally uses only the Python standard library.  It is
separate from RAGAS so it can run in local/offline test environments.
"""

import re
import unicodedata


def normalize_label(value):
    text = unicodedata.normalize("NFC", str(value or "")).casefold()
    text = text.replace("[", " ").replace("]", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def precision_at_k(ranked_items, relevant_items, k):
    ranked = list(ranked_items or [])[:max(0, int(k))]
    relevant = {normalize_label(item) for item in (relevant_items or [])}
    if not ranked:
        return 0.0
    hits = sum(normalize_label(item) in relevant for item in ranked)
    return round(hits / len(ranked), 6)


def recall_at_k(ranked_items, relevant_items, k):
    relevant = {
        normalize_label(item)
        for item in (relevant_items or [])
        if normalize_label(item)
    }
    if not relevant:
        return 0.0
    top_items = {
        normalize_label(item)
        for item in list(ranked_items or [])[:max(0, int(k))]
    }
    return round(len(relevant & top_items) / len(relevant), 6)


def reciprocal_rank(ranked_items, relevant_items):
    relevant = {normalize_label(item) for item in (relevant_items or [])}
    for rank, item in enumerate(ranked_items or [], start=1):
        if normalize_label(item) in relevant:
            return round(1.0 / rank, 6)
    return 0.0


def mean_reciprocal_rank(rankings):
    rankings = list(rankings or [])
    if not rankings:
        return 0.0
    return round(
        sum(reciprocal_rank(ranked, relevant)
            for ranked, relevant in rankings) / len(rankings),
        6,
    )


def citation_coverage(answer, citations=None):
    values = [str(item).strip() for item in (citations or []) if str(item).strip()]
    text = str(answer or "")
    return bool(values or re.search(r"\[[^\[\]]+\]", text))


def source_matches(expected_source, citations=None, answer=""):
    expected = normalize_label(expected_source)
    if not expected:
        return False
    candidates = [str(item) for item in (citations or [])]
    candidates.append(str(answer or ""))
    pattern = re.compile(re.escape(expected) + r"(?!\d)")
    return any(pattern.search(normalize_label(candidate)) for candidate in candidates)


def evaluate_refusal(records):
    records = list(records or [])
    if not records:
        return {
            "total": 0,
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "false_positives": 0,
            "false_negatives": 0,
        }

    correct = 0
    true_positive = false_positive = false_negative = 0
    for record in records:
        expected = bool(record.get("should_refuse"))
        actual = bool(record.get("refused"))
        correct += int(expected == actual)
        if expected and actual:
            true_positive += 1
        elif not expected and actual:
            false_positive += 1
        elif expected and not actual:
            false_negative += 1

    return {
        "total": len(records),
        "accuracy": round(correct / len(records), 6),
        "precision": round(
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive else 0.0,
            6,
        ),
        "recall": round(
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative else 0.0,
            6,
        ),
        "false_positives": false_positive,
        "false_negatives": false_negative,
    }


def evaluate_offline(records, k=5):
    """Aggregate all offline metrics for benchmark result dictionaries."""
    records = list(records or [])
    retrieval_records = [
        record for record in records
        if record.get("ranked_citations") is not None
        and record.get("relevant_citations") is not None
    ]

    precision_values = []
    recall_values = []
    rankings = []
    for record in retrieval_records:
        ranked = record["ranked_citations"]
        relevant = record["relevant_citations"]
        precision_values.append(precision_at_k(ranked, relevant, k))
        recall_values.append(recall_at_k(ranked, relevant, k))
        rankings.append((ranked, relevant))

    citations = [
        record for record in records
        if not record.get("should_refuse")
    ]
    citation_hits = sum(
        citation_coverage(
            record.get("answer"),
            record.get("citations"),
        )
        for record in citations
    )

    source_records = [
        record for record in records
        if record.get("expected_source")
        and not record.get("should_refuse")
    ]
    source_hits = sum(
        source_matches(
            record["expected_source"],
            record.get("citations"),
            record.get("answer"),
        )
        for record in source_records
    )

    return {
        f"precision_at_{k}": round(
            sum(precision_values) / len(precision_values), 6
        ) if precision_values else 0.0,
        f"recall_at_{k}": round(
            sum(recall_values) / len(recall_values), 6
        ) if recall_values else 0.0,
        "mrr": mean_reciprocal_rank(rankings),
        "citation_coverage": round(
            citation_hits / len(citations), 6
        ) if citations else 0.0,
        "source_correctness": round(
            source_hits / len(source_records), 6
        ) if source_records else 0.0,
        "refusal": evaluate_refusal(records),
        "retrieval_cases": len(retrieval_records),
        "citation_cases": len(citations),
        "source_cases": len(source_records),
    }
