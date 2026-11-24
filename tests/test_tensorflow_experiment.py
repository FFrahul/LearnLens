import importlib.util
import unittest

from tensorflow_experiment import (
    run_keras_dnn_experiment,
    run_keras_lstm_experiment,
)


HAS_TENSORFLOW = importlib.util.find_spec("tensorflow") is not None


def labeled_history(count=24):
    topics = ("Clustering", "Linear Models")
    return [
        {
            "topic": topics[index % len(topics)],
            "is_correct": bool(index % 3),
            "difficulty": ("Easy", "Medium", "Hard")[index % 3],
        }
        for index in range(count)
    ]


class TensorFlowExperimentTests(unittest.TestCase):
    def test_dnn_requires_enough_history(self):
        result = run_keras_dnn_experiment(
            [{"topic": "Clustering", "is_correct": True}],
            minimum_samples=20,
        )
        self.assertFalse(result["ready"])

    def test_lstm_requires_enough_history(self):
        result = run_keras_lstm_experiment(
            [{"topic": "Clustering", "is_correct": True}],
            minimum_samples=20,
        )
        self.assertFalse(result["ready"])

    @unittest.skipUnless(HAS_TENSORFLOW, "TensorFlow is an optional dependency")
    def test_dnn_runs_when_tensorflow_is_available(self):
        result = run_keras_dnn_experiment(labeled_history(), epochs=1)
        self.assertTrue(result["ready"])
        self.assertEqual(result["framework"], "tensorflow")
        self.assertEqual(result["epochs"], 1)
        self.assertGreaterEqual(result["next_correct_probability"], 0.0)
        self.assertLessEqual(result["next_correct_probability"], 1.0)

    @unittest.skipUnless(HAS_TENSORFLOW, "TensorFlow is an optional dependency")
    def test_lstm_runs_when_tensorflow_is_available(self):
        result = run_keras_lstm_experiment(labeled_history(), epochs=1)
        self.assertTrue(result["ready"])
        self.assertEqual(result["framework"], "tensorflow")
        self.assertEqual(result["epochs"], 1)
        self.assertGreaterEqual(result["next_correct_probability"], 0.0)
        self.assertLessEqual(result["next_correct_probability"], 1.0)
