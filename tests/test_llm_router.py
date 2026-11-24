import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import streamlit as st

from llm_router import HybridClient


class OfflineModel:
    def __init__(self):
        self.calls = []
        self.models = SimpleNamespace(generate_content=self.generate_content)

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(text="local answer")


class HybridClientTests(unittest.TestCase):
    def setUp(self):
        for key in ("ai_mode", "ai_backend_used"):
            if key in st.session_state:
                del st.session_state[key]

    def test_auto_falls_back_to_ollama_without_key(self):
        st.session_state["ai_mode"] = "Auto (recommended)"
        offline = OfflineModel()
        client = HybridClient(offline)

        with patch.dict(os.environ, {}, clear=True):
            result = client.models.generate_content(
                contents="source-grounded prompt"
            )

        self.assertEqual(result.text, "local answer")
        self.assertEqual(client.last_backend, "ollama")
        self.assertEqual(st.session_state["ai_backend_used"], "ollama")
        self.assertEqual(len(offline.calls), 1)

    def test_offline_never_calls_gemini_or_internet(self):
        st.session_state["ai_mode"] = "Offline - Llama (local)"
        offline = OfflineModel()
        client = HybridClient(offline)

        with patch("llm_router.internet_available") as internet_check:
            result = client.models.generate_content(
                contents="source-grounded prompt"
            )

        internet_check.assert_not_called()
        self.assertEqual(result.text, "local answer")

    def test_online_mode_falls_back_to_ollama_when_gemini_unavailable(self):
        st.session_state["ai_mode"] = "Online - Gemini"
        offline = OfflineModel()
        client = HybridClient(offline)

        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "test-key"},
            clear=True,
        ), patch(
            "llm_router.internet_available",
            return_value=False,
        ):
            result = client.models.generate_content(
                contents="source-grounded prompt"
            )

        self.assertEqual(result.text, "local answer")
        self.assertEqual(st.session_state["ai_backend_used"], "ollama")
        self.assertEqual(len(offline.calls), 1)


if __name__ == "__main__":
    unittest.main()
