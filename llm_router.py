"""Hybrid Gemini / Ollama text-generation router for LearnLens AI."""

from __future__ import annotations

import os
import socket
import time
from types import SimpleNamespace

import streamlit as st


GEMINI_HOST = "generativelanguage.googleapis.com"
MODES = [
    "Auto (recommended)",
    "Online - Gemini",
    "Offline - Llama (local)",
]


_net_cache = {"t": 0.0, "ok": False}


def internet_available(timeout: float = 1.5, ttl: float = 15.0) -> bool:
    """Check Google API reachability over TCP."""
    now = time.time()
    if now - _net_cache["t"] < ttl:
        return _net_cache["ok"]
    try:
        socket.create_connection((GEMINI_HOST, 443), timeout=timeout).close()
        ok = True
    except OSError:
        ok = False
    _net_cache.update(t=now, ok=ok)
    return ok


class HybridClient:
    """Compatibility wrapper for the app's existing client.models interface."""

    def __init__(self, offline_client, offline_model=None):
        self.offline = offline_client
        self.offline_model = (
            offline_model
            or os.getenv("LEARNLENS_OLLAMA_MODEL", "llama3.2:1b")
        )
        self.gemini_model = os.getenv(
            "LEARNLENS_GEMINI_MODEL",
            "gemini-2.5-flash",
        )
        self._gemini = None
        self.last_backend = "none"
        self.last_error = ""
        self.models = SimpleNamespace(generate_content=self.generate_content)

    @staticmethod
    def mode():
        return st.session_state.get("ai_mode", MODES[0])

    def gemini_ready(self):
        return bool(
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

    def _get_gemini(self):
        if self._gemini is None:
            from google import genai

            self._gemini = genai.Client()
        return self._gemini

    def _call_gemini(self, contents):
        from google.genai import types

        response = self._get_gemini().models.generate_content(
            model=self.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.2),
        )
        return SimpleNamespace(text=(response.text or "").strip())

    def _call_offline(self, contents, config=None):
        kwargs = {
            "model": self.offline_model,
            "contents": contents,
        }
        if config is not None:
            kwargs["config"] = config
        return self.offline.models.generate_content(**kwargs)

    def generate_content(
        self,
        model=None,
        contents=None,
        config=None,
        **kwargs,
    ):
        mode = self.mode()
        want_online = mode.startswith(("Auto", "Online"))
        force_online = mode.startswith("Online")

        if want_online:
            if self.gemini_ready() and internet_available():
                try:
                    result = self._call_gemini(contents)
                    if result.text:
                        self.last_backend = "gemini"
                        self.last_error = ""
                        st.session_state["ai_backend_used"] = "gemini"
                        return result
                except Exception as error:
                    self.last_error = f"{type(error).__name__}: {error}"
            else:
                self.last_error = (
                    "No GEMINI_API_KEY set"
                    if not self.gemini_ready()
                    else "No internet connection"
                )

            if force_online:
                st.session_state["fallback_notice"] = (
                    "Gemini is unavailable. LearnLens automatically "
                    "switched to local Ollama for this answer."
                )
        else:
            st.session_state.pop("fallback_notice", None)

        try:
            result = self._call_offline(contents, config)
            self.last_backend = "ollama"
            st.session_state["ai_backend_used"] = "ollama"
            return result
        except Exception as error:
            self.last_backend = "error"
            self.last_error = f"{type(error).__name__}: {error}"
            st.session_state["ai_backend_used"] = "error"
            return SimpleNamespace(
                text=(
                    "Local Ollama is unavailable. Start Ollama and ensure "
                    "llama3.2:1b is installed, then try again."
                )
            )


def render_mode_selector(client):
    st.markdown("**AI Engine**")
    st.radio(
        "Engine mode",
        MODES,
        key="ai_mode",
        label_visibility="collapsed",
    )
    online = internet_available()
    key_ok = client.gemini_ready()
    mode = client.mode()
    if mode.startswith("Offline"):
        engine_status = "Offline"
        text_model = client.offline_model
    elif mode.startswith("Online"):
        text_model = client.gemini_model
        engine_status = (
            "Online"
            if online and key_ok
            else "Gemini unavailable"
        )
    else:
        if online and key_ok:
            engine_status = "Online / Gemini"
            text_model = client.gemini_model
        else:
            engine_status = "Offline fallback"
            text_model = client.offline_model
    st.markdown(
        "<div class=\"ll-status-row\">"
        f"<span class=\"ll-status-chip\">Engine: {mode.split()[0]}</span>"
        f"<span class=\"ll-status-chip\">Text: {text_model}</span>"
        f"<span class=\"ll-status-chip\">Vision: "
        f"{os.getenv('LEARNLENS_OLLAMA_VISION_MODEL', 'llava:7b')}</span>"
        f"<span class=\"ll-status-chip\">{engine_status}</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    fallback_notice = st.session_state.get("fallback_notice")
    if fallback_notice:
        st.warning(fallback_notice)
