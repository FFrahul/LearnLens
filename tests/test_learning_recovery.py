import unittest

from learning_recovery import build_recovery_plan


class LearningRecoveryTests(unittest.TestCase):
    def test_prioritizes_review_topics(self):
        plan = build_recovery_plan(
            [
                {
                    "topic": "Clustering",
                    "accuracy": 40,
                    "status": "🔴 Needs Review",
                },
                {
                    "topic": "Regression",
                    "accuracy": 90,
                    "status": "🟢 Mastered",
                },
            ]
        )

        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["topic"], "Clustering")
        self.assertIn("Review the cited material", plan[0]["step"])

    def test_uses_graph_prerequisite_for_review_topic(self):
        plan = build_recovery_plan(
            [{
                "topic": "Clustering",
                "accuracy": 40,
                "status": "🔴 Needs Review",
            }],
            graph={
                "edges": [{
                    "source": "prerequisite:Distance metrics",
                    "target": "topic:Clustering",
                    "relation": "precedes",
                }]
            }
        )
        self.assertIn("Distance metrics", plan[0]["step"])


if __name__ == "__main__":
    unittest.main()
