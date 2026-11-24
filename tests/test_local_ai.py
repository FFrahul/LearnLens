import json
import math
import os
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch

from local_ai import (
    LocalAIError,
    LocalVideoTranscriber,
    OllamaLocalAI,
    TranscriptSegment,
    feature_hash_embedding,
)


class FeatureHashEmbeddingTests(unittest.TestCase):
    def test_embedding_is_deterministic_and_normalized(self):
        first = feature_hash_embedding("Local retrieval uses source text.")
        second = feature_hash_embedding("Local retrieval uses source text.")

        self.assertEqual(first, second)
        self.assertAlmostEqual(
            math.sqrt(sum(value * value for value in first)),
            1.0,
            places=6
        )

    def test_empty_text_returns_zero_vector(self):
        self.assertEqual(
            feature_hash_embedding(""),
            [0.0] * 768
        )


class OllamaLocalAITests(unittest.TestCase):
    def test_rejects_non_loopback_hosts(self):
        with self.assertRaises(ValueError):
            OllamaLocalAI(host="https://example.com")

    def test_allows_docker_host_bridge(self):
        ai = OllamaLocalAI(host="http://host.docker.internal:11434")
        self.assertEqual(ai.host, "http://host.docker.internal:11434")

    def test_generate_uses_local_json_endpoint(self):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps(
            {"response": '{"answer":"local"}'}
        ).encode("utf-8")
        connection = MagicMock()
        connection.getresponse.return_value = response
        ai = OllamaLocalAI(
            model="llama3.2:1b",
            host="http://127.0.0.1:11434"
        )

        with patch(
            "http.client.HTTPConnection",
            return_value=connection
        ) as connection_factory:
            result = ai.generate("Return JSON.", json_mode=True)

        connection_factory.assert_called_once_with(
            "127.0.0.1",
            11434,
            timeout=180
        )
        method, path = connection.request.call_args.args[:2]
        payload = json.loads(connection.request.call_args.kwargs["body"])
        self.assertEqual(method, "POST")
        self.assertEqual(path, "/api/generate")
        self.assertEqual(payload["model"], "llama3.2:1b")
        self.assertEqual(payload["format"], "json")
        self.assertEqual(result, '{"answer":"local"}')

    def test_unreachable_ollama_reports_actionable_error(self):
        ai = OllamaLocalAI(host="http://127.0.0.1:11434")
        with patch(
            "http.client.HTTPConnection",
            side_effect=OSError("offline")
        ):
            with self.assertRaisesRegex(LocalAIError, "Start Ollama"):
                ai.generate("Hello.")

    def test_status_reports_installed_model_names(self):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps({
            "models": [{"name": "llama3.2:1b"}]
        }).encode("utf-8")
        connection = MagicMock()
        connection.getresponse.return_value = response
        ai = OllamaLocalAI()
        with patch(
            "http.client.HTTPConnection",
            return_value=connection
        ):
            status = ai.status()
        self.assertEqual(status["installed_models"], ["llama3.2:1b"])

    def test_generate_with_image_uses_local_vision_payload(self):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps(
            {"response": "The image shows a chart."}
        ).encode("utf-8")
        connection = MagicMock()
        connection.getresponse.return_value = response
        ai = OllamaLocalAI(host="http://127.0.0.1:11434")

        with patch.dict(
            os.environ,
            {"LEARNLENS_OLLAMA_VISION_MODEL": "llava:7b"}
        ), patch(
            "http.client.HTTPConnection",
            return_value=connection
        ):
            result = ai.generate_with_image(
                "Describe the image.",
                b"image-bytes",
                "image/png"
            )

        payload = json.loads(connection.request.call_args.kwargs["body"])
        self.assertEqual(payload["model"], "llava:7b")
        self.assertEqual(result, "The image shows a chart.")
        self.assertTrue(payload["images"][0])


class LocalVideoTranscriberTests(unittest.TestCase):
    def test_transcribe_returns_nonempty_timestamped_segments(self):
        transcriber = LocalVideoTranscriber(use_gpu=False)
        fake_model = MagicMock()
        fake_model.transcribe.return_value = (
            [
                MagicMock(start=1.5, end=4.0, text=" A local lecture segment "),
                MagicMock(start=4.0, end=5.0, text="  ")
            ],
            None
        )

        with patch.object(transcriber, "_load_model", return_value=fake_model):
            segments = transcriber.transcribe("lecture.mp4")

        self.assertEqual(
            segments,
            [
                TranscriptSegment(
                    start=1.5,
                    end=4.0,
                    text="A local lecture segment"
                )
            ]
        )
        fake_model.transcribe.assert_called_once_with(
            "lecture.mp4",
            vad_filter=True,
            beam_size=1
        )


if __name__ == "__main__":
    unittest.main()
