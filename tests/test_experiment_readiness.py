import unittest

from experiment_readiness import assess_sequence_readiness


class ExperimentReadinessTests(unittest.TestCase):
    def test_rejects_small_or_single_topic_history(self):
        result = assess_sequence_readiness(
            [{"topic": "Clustering"} for _ in range(3)],
            minimum_samples=5,
            minimum_topics=2
        )
        self.assertFalse(result["ready"])
        self.assertEqual(result["samples"], 3)
        self.assertEqual(result["topics"], 1)
        self.assertEqual(len(result["reasons"]), 2)

    def test_accepts_sufficient_labeled_history(self):
        result = assess_sequence_readiness(
            [
                {"topic": "Clustering"},
                {"topic": "Regression"},
                {"topic": "Clustering"},
                {"topic": "Regression"},
            ],
            minimum_samples=4,
            minimum_topics=2
        )
        self.assertTrue(result["ready"])


if __name__ == "__main__":
    unittest.main()
