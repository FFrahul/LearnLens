"""Reusable LearnLens UI components."""

from __future__ import annotations

import html

import streamlit as st


def escape_text(value: object) -> str:
    return html.escape(str(value), quote=True)


def hero(compact_status: list[str]) -> None:
    chips = "".join(
        f'<span class="ll-chip">{escape_text(label)}</span>'
        for label in compact_status
    )
    st.markdown(
        """
<div class="ll-hero">
  <div>
    <div class="ll-hero-title">LearnLens AI</div>
    <div class="ll-hero-copy">Upload. Review. Learn. Practice — with grounded, adaptive help.</div>
  </div>
  <div class="ll-hero-chips">"""
        + chips
        + """
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def stepper(current_step: int, completed_steps: set[int]) -> None:
    steps = [
        ("Upload", "Add learning materials"),
        ("Review Extraction", "Check what was found"),
        ("Learn", "Tutor and visual aids"),
        ("Practice", "Assess and track mastery"),
    ]
    markup = ['<div class="ll-stepper">']
    for number, (name, hint) in enumerate(steps, start=1):
        state = "active" if number == current_step else ""
        if number in completed_steps:
            state = "done"
        if number > current_step and number not in completed_steps:
            state = "locked"
        marker = "✓" if number in completed_steps else str(number)
        if number > current_step and number not in completed_steps:
            hint = "Upload a file first"
        markup.append(
            '<div class="ll-step '
            + state
            + '"><span class="ll-step-number">'
            + marker
            + '</span><span class="ll-step-name">'
            + escape_text(name)
            + '</span><div class="ll-step-hint">'
            + escape_text(hint)
            + "</div></div>"
        )
    markup.append("</div>")
    st.markdown("".join(markup), unsafe_allow_html=True)


def card(title: str, copy: str, kind: str = "info") -> None:
    if kind not in {"info", "success", "warning", "error"}:
        kind = "info"
    st.markdown(
        '<div class="ll-card '
        + kind
        + '"><strong>'
        + escape_text(title)
        + "</strong><br>"
        + escape_text(copy)
        + "</div>",
        unsafe_allow_html=True,
    )


def empty_state(title: str, copy: str, action_label: str) -> bool:
    st.markdown(
        '<div class="ll-card ll-empty"><div class="ll-empty-title">'
        + escape_text(title)
        + '</div><div class="ll-empty-copy">'
        + escape_text(copy)
        + "</div></div>",
        unsafe_allow_html=True,
    )
    return st.button(action_label, type="primary", width="stretch")


def status_chips(labels: list[str]) -> None:
    markup = ['<div class="ll-status-row">']
    for label in labels:
        markup.append(
            '<span class="ll-status-chip">'
            + escape_text(label)
            + "</span>"
        )
    markup.append("</div>")
    st.markdown("".join(markup), unsafe_allow_html=True)
