import unittest
import importlib.util
import sys

from sequence_experiment import run_dnn_experiment, run_lstm_experiment


class SequenceExperimentTests(unittest.TestCase):
    def test_tensorflow_is_not_imported_with_sequence_experiment(self):
        sys.modules.pop("tensorflow", None)
        sys.modules.pop("tensorflow_experiment", None)
        import sequence_experiment
        self.assertNotIn("tensorflow", sys.modules)
        self.assertFalse(hasattr(sequence_experiment, "_tensorflow_loaded"))

    def test_requires_enough_history(self):
        result = run_lstm_experiment(
            [{"topic": "Clustering", "is_correct": True}],
            minimum_samples=20
        )
        self.assertFalse(result["ready"])
        self.assertIn("required", result["message"])

    def test_dnn_requires_enough_history(self):
        result = run_dnn_experiment(
            [{"topic": "Clustering", "is_correct": True}],
            minimum_samples=20
        )
        self.assertFalse(result["ready"])


if __name__ == "__main__":
    unittest.main()
