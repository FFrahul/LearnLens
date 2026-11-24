import unittest

from assessment_fallback import build_deterministic_assessment_question


class AssessmentFallbackTests(unittest.TestCase):
    def test_builds_four_option_grounded_mcq(self):
        question = build_deterministic_assessment_question(
            [
                {
                    "text": (
                        "Hierarchical clustering builds a nested grouping structure. "
                        "It begins with individual points and combines clusters."
                    ),
                    "citation": "[kmeans_notes.pdf, Page 1]",
                }
            ],
            "Easy",
        )

        self.assertIsNotNone(question)
        self.assertEqual(len(question["options"]), 4)
        self.assertIn(question["correct_answer"], question["options"])
        self.assertEqual(
            question["source_citation"],
            "[kmeans_notes.pdf, Page 1]",
        )

    def test_requires_multiple_source_sentences(self):
        question = build_deterministic_assessment_question(
            [
                {
                    "text": "A short passage.",
                    "citation": "[notes.pdf, Page 1]",
                }
            ],
            "Easy",
        )
        self.assertIsNone(question)

    def test_different_indexes_rotate_source_and_question_text(self):
        pool = [
            {
                "text": (
                    "Hierarchical clustering begins with individual data points. "
                    "It repeatedly merges the nearest pair of clusters. "
                    "The process stops when one cluster remains. "
                    "A dendrogram illustrates the merge sequence."
                ),
                "citation": "[clustering.pdf, Page 1]",
            }
        ]
        first = build_deterministic_assessment_question(
            pool, "Easy", question_index=0
        )
        second = build_deterministic_assessment_question(
            pool, "Medium", question_index=1
        )
        self.assertNotEqual(first["question"], second["question"])
        self.assertNotEqual(first["correct_answer"], second["correct_answer"])
        seen = {
            first["correct_answer"].casefold(),
            second["correct_answer"].casefold(),
        }
        third = build_deterministic_assessment_question(
            pool, "Hard", question_index=2, seen_correct_answers=seen
        )
        self.assertNotEqual(third["correct_answer"], first["correct_answer"])
        self.assertNotEqual(third["correct_answer"], second["correct_answer"])
        self.assertNotEqual(
            set(third["options"]),
            set(first["options"]),
        )
