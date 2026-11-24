import unittest

from agent_workflow import plan_learning_query, verify_retrieved_sources


class AgentWorkflowTests(unittest.TestCase):
    def test_planner_normalizes_question(self):
        plan = plan_learning_query("  What   is clustering? ")
        self.assertEqual(plan["question"], "What is clustering?")
        self.assertIn("clustering?", plan["terms"])

    def test_verifier_rejects_weak_sources(self):
        decision = verify_retrieved_sources(
            [{"score": 0.01}, {"score": 0.20}],
            minimum_score=0.05
        )
        self.assertEqual(len(decision.accepted_sources), 1)
        self.assertEqual(decision.reason, "grounded")


if __name__ == "__main__":
    unittest.main()
