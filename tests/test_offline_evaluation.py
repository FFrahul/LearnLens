import unittest

from offline_evaluation import (
    citation_coverage,
    evaluate_offline,
    evaluate_refusal,
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    source_matches,
)


class OfflineEvaluationTests(unittest.TestCase):
    def test_precision_recall_and_reciprocal_rank(self):
        ranked = ["Slide 1", "Slide 2", "Slide 3"]
        relevant = ["Slide 2", "Slide 3"]
        self.assertEqual(precision_at_k(ranked, relevant, 2), 0.5)
        self.assertEqual(recall_at_k(ranked, relevant, 2), 0.5)
        self.assertEqual(reciprocal_rank(ranked, relevant), 0.5)
        self.assertEqual(
            mean_reciprocal_rank([(ranked, relevant), (["Slide 1"], ["Slide 1"])]),
            0.75,
        )

    def test_citation_and_source_matching(self):
        self.assertTrue(citation_coverage(
            "The answer [Clustering.pptx, Slide 7]",
        ))
        self.assertFalse(citation_coverage("The answer"))
        self.assertTrue(source_matches(
            "Clustering.pptx, Slide 7",
            ["[Clustering.pptx, Slide 7]"],
            "",
        ))
        self.assertFalse(source_matches(
            "Clustering.pptx, Slide 7",
            ["[Clustering.pptx, Slide 70]"],
            "",
        ))

    def test_refusal_metrics_separate_false_positives_and_negatives(self):
        result = evaluate_refusal([
            {"should_refuse": True, "refused": True},
            {"should_refuse": True, "refused": False},
            {"should_refuse": False, "refused": True},
            {"should_refuse": False, "refused": False},
        ])
        self.assertEqual(result["accuracy"], 0.5)
        self.assertEqual(result["precision"], 0.5)
        self.assertEqual(result["recall"], 0.5)
        self.assertEqual(result["false_positives"], 1)
        self.assertEqual(result["false_negatives"], 1)

    def test_aggregate_evaluation(self):
        result = evaluate_offline([
            {
                "ranked_citations": ["A.pdf, Page 1", "B.pdf, Page 2"],
                "relevant_citations": ["A.pdf, Page 1"],
                "answer": "Answer [A.pdf, Page 1]",
                "citations": ["A.pdf, Page 1"],
                "expected_source": "A.pdf, Page 1",
                "should_refuse": False,
                "refused": False,
            },
            {
                "ranked_citations": ["C.pdf, Page 1"],
                "relevant_citations": [],
                "answer": "Bu bilgi yüklenen ders materyallerinde bulunamadı.",
                "citations": [],
                "expected_source": "",
                "should_refuse": True,
                "refused": True,
            },
        ], k=1)
        self.assertEqual(result["precision_at_1"], 0.5)
        self.assertEqual(result["recall_at_1"], 0.5)
        self.assertEqual(result["mrr"], 0.5)
        self.assertEqual(result["citation_coverage"], 1.0)
        self.assertEqual(result["source_correctness"], 1.0)
        self.assertEqual(result["refusal"]["accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
