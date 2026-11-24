import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from local_ai import OllamaLocalAI


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_MATERIALS = ROOT / "sample_materials"
APP_FILE = ROOT / "app.py"
LOCAL_MODEL_READY = {
    "available": True,
    "model_installed": True,
    "message": "Local model ready: test-model"
}


class LocalAppTests(unittest.TestCase):
    def run_app(self, app):
        return app.run(timeout=60)

    def create_app(self):
        return AppTest.from_file(str(APP_FILE))

    def test_suggested_tutor_question_updates_text_input_safely(self):
        with patch.object(
            OllamaLocalAI,
            "status",
            return_value=LOCAL_MODEL_READY,
        ):
            app = self.run_app(self.create_app())
            uploader = next(
                item for item in app.get("file_uploader")
                if item.key == "pptx_uploader"
            )
            uploader.upload(
                "Clustering_Lecture.pptx",
                (SAMPLE_MATERIALS / "Clustering_Lecture.pptx").read_bytes(),
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
            app = self.run_app(app)
            suggested = [
                item for item in app.button
                if item.label.startswith("What are the key ideas")
            ]
            if suggested:
                suggested[0].click()
                app = self.run_app(app)

        self.assertEqual(len(app.exception), 0)

    def test_application_starts_without_api_key(self):
        with patch.object(
            OllamaLocalAI,
            "status",
            return_value=LOCAL_MODEL_READY
        ):
            app = self.run_app(self.create_app())

        self.assertEqual(len(app.exception), 0)
        self.assertGreaterEqual(len(app.tabs), 4)
        repeated_limitation = [
            item.value
            for item in app.info
            if "embedded figures" in item.value
        ]
        self.assertEqual(repeated_limitation, [])

    def test_pdf_indexes_and_answers_with_retrieved_citation(self):
        generated_answer = "K-means minimizes within-cluster SSE."
        with patch.object(
            OllamaLocalAI,
            "status",
            return_value=LOCAL_MODEL_READY
        ), patch.object(
            OllamaLocalAI,
            "generate",
            return_value=generated_answer
        ):
            app = self.run_app(self.create_app())
            mode = next(
                item for item in app.get("radio")
                if item.key == "ai_mode"
            )
            mode.set_value("Offline - Llama (local)")
            app = self.run_app(app)
            uploader = next(
                item for item in app.get("file_uploader")
                if item.key == "pdf_uploader"
            )
            uploader.upload(
                "kmeans_notes.pdf",
                (SAMPLE_MATERIALS / "kmeans_notes.pdf").read_bytes(),
                "application/pdf"
            )
            app = self.run_app(app)

            chunks = app.session_state["chunks"]
            self.assertTrue(chunks)
            self.assertEqual(
                app.session_state["embeddings"].shape[1],
                768
            )

            next(
                item for item in app.get("text_input")
                if item.key == "pdf_question"
            ).set_value("What does k-means minimize?")
            next(
                item for item in app.button
                if item.label == "Ask PDF"
            ).click()
            app = self.run_app(app)

        self.assertEqual(len(app.exception), 0)
        self.assertFalse(app.error)
        answer = next(
            item.value for item in app.get("markdown")
            if generated_answer in item.value
        )
        self.assertIn("[kmeans_notes.pdf, Page ", answer)

    def test_powerpoint_extracts_slides_offline(self):
        with patch.object(
            OllamaLocalAI,
            "status",
            return_value=LOCAL_MODEL_READY
        ):
            app = self.run_app(self.create_app())
            uploader = next(
                item for item in app.get("file_uploader")
                if item.key == "pptx_uploader"
            )
            uploader.upload(
                "Clustering_Lecture.pptx",
                (SAMPLE_MATERIALS / "Clustering_Lecture.pptx").read_bytes(),
                "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
            app = self.run_app(app)

        self.assertEqual(len(app.exception), 0)
        self.assertTrue(app.session_state["slide_chunks"])
        self.assertEqual(
            app.session_state["slide_embeddings"].shape[1],
            768
        )

    def test_image_question_uses_local_vision_model(self):
        with patch.object(
            OllamaLocalAI,
            "status",
            return_value={
                **LOCAL_MODEL_READY,
                "installed_models": ["llama3.2:1b", "llava:7b"]
            }
        ), patch.object(
            OllamaLocalAI,
            "generate_with_image",
            return_value="The image contains a lecture interface."
        ) as generate_with_image:
            app = self.run_app(self.create_app())
            uploader = next(
                item for item in app.get("file_uploader")
                if item.key == "image_uploader"
            )
            uploader.upload(
                "lesson.png",
                (ROOT / "assets" / "screenshots" / "learner-profile.png").read_bytes(),
                "image/png"
            )
            app = self.run_app(app)
            next(
                item for item in app.get("text_input")
                if item.key == "image_question"
            ).set_value("What is shown?")
            next(
                item for item in app.button
                if item.label == "Ask Image"
            ).click()
            app = self.run_app(app)

        self.assertEqual(len(app.exception), 0)
        self.assertFalse(app.error)
        self.assertGreaterEqual(generate_with_image.call_count, 1)
        self.assertIn(
            "The image contains a lecture interface.",
            "\n".join(
                item.value for item in app.get("markdown")
            )
        )

    def test_pdf_refuses_unrelated_query_without_model_call(self):
        with patch.object(
            OllamaLocalAI,
            "status",
            return_value=LOCAL_MODEL_READY
        ), patch.object(
            OllamaLocalAI,
            "generate",
            return_value="This should not be used."
        ) as generate:
            app = self.run_app(self.create_app())
            uploader = next(
                item for item in app.get("file_uploader")
                if item.key == "pdf_uploader"
            )
            uploader.upload(
                "kmeans_notes.pdf",
                (SAMPLE_MATERIALS / "kmeans_notes.pdf").read_bytes(),
                "application/pdf"
            )
            app = self.run_app(app)
            next(
                item for item in app.get("text_input")
                if item.key == "pdf_question"
            ).set_value("What is backpropagation in neural networks?")
            next(
                item for item in app.button
                if item.label == "Ask PDF"
            ).click()
            app = self.run_app(app)

        self.assertEqual(len(app.exception), 0)
        generate.assert_not_called()
        rendered_text = "\n".join(
            item.value for item in app.get("markdown")
        )
        self.assertIn(
            "This information was not found in the uploaded learning materials.",
            rendered_text
        )


if __name__ == "__main__":
    unittest.main()
