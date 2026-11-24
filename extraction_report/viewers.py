"""Interactive Streamlit viewers for extraction reports."""

from __future__ import annotations

from typing import Iterable

import streamlit as st


def render_warnings(warnings: Iterable[str]) -> None:
    for warning in warnings:
        st.warning(warning)


def render_source_summary(items: list[dict]) -> None:
    st.markdown("### What the AI will use")
    source_labels = sorted({
        str(item.get("citation", "")).strip()
        for item in items
        if item.get("citation")
    })
    st.caption(f"{len(items)} chunks from {len(source_labels)} source locations")
    chips = " ".join(
        f'<span class="ll-status-chip">{label}</span>'
        for label in source_labels
    )
    if chips:
        st.markdown(
            f'<div class="ll-status-row">{chips}</div>',
            unsafe_allow_html=True,
        )


def render_knowledge_structure(items: list[dict]) -> None:
    with st.expander("Knowledge Structure", expanded=True):
        grouped: dict[str, dict[str, list[str]]] = {}
        for item in items:
            topic = str(item.get("topic") or "General").strip()
            subtopic = str(item.get("subtopic") or "Core concepts").strip()
            source = str(item.get("citation") or "Source not available").strip()
            grouped.setdefault(topic, {}).setdefault(subtopic, [])
            if source not in grouped[topic][subtopic]:
                grouped[topic][subtopic].append(source)

        if not grouped:
            st.info("Upload a source to build the knowledge structure.")
            return

        for topic, subtopics in grouped.items():
            st.markdown(f"**{topic}**")
            for subtopic, sources in subtopics.items():
                st.markdown(f"- {subtopic}")
                for source in sources:
                    st.caption(f"  Source: {source}")


def render_pdf_report(report: dict, location: str = "upload") -> None:
    st.markdown("### Extraction Report")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pages", report["page_count"])
    col2.metric("Text pages", report["text_pages"])
    col3.metric("Scanned pages", report["scanned_pages"])
    col4.metric("Words", report["total_words"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Headings", report["headings_count"])
    col2.metric("Tables", report["tables"])
    col3.metric("Images", report["images"])
    st.caption(
        "OCR used: " + ("Yes" if report["ocr_used"] else "No")
    )
    render_warnings(report["warnings"])

    if not report["pages"]:
        st.info("No PDF pages were extracted.")
        return
    page_number = st.selectbox(
        "Page",
        [page["number"] for page in report["pages"]],
        format_func=lambda number: f"Page {number}",
        key=f"pdf_report_page_{location}_{report['name']}",
    )
    page = next(page for page in report["pages"] if page["number"] == page_number)
    left, right = st.columns([1, 1.35], gap="large")
    with left:
        st.image(page["thumbnail"], caption=f"{report['name']} — Page {page_number}")
    with right:
        st.markdown("**Detected headings**")
        if page["headings"]:
            for heading in page["headings"]:
                st.markdown(f"- {heading}")
        else:
            st.caption("No headings detected.")
        st.markdown("**Extracted text**")
        st.text_area(
            "Page text",
            page["text"] or "No text extracted.",
            height=320,
            label_visibility="collapsed",
            key=f"pdf_page_text_{location}_{report['name']}_{page_number}",
        )


def render_pptx_report(report: dict, location: str = "upload") -> None:
    st.markdown("### Extraction Report")
    col1, col2, col3 = st.columns(3)
    col1.metric("Slides", report["slide_count"])
    col2.metric("Images", report["images"])
    col3.metric("Charts", report["charts"])
    render_warnings(report["warnings"])

    if not report["slides"]:
        st.info("No slides were extracted.")
        return
    slide_number = st.selectbox(
        "Slide",
        [slide["number"] for slide in report["slides"]],
        format_func=lambda number: f"Slide {number}",
        key=f"pptx_report_slide_{location}_{report['name']}",
    )
    slide = next(
        slide for slide in report["slides"] if slide["number"] == slide_number
    )
    st.markdown(f"#### {slide['title']}")
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        st.markdown("**Bullets / body text**")
        if slide["bullets"]:
            for bullet in slide["bullets"]:
                st.write(bullet)
        else:
            st.caption("No body text extracted.")
    with right:
        st.markdown("**Speaker notes**")
        st.write(slide["speaker_notes"] or "No speaker notes found.")
        st.caption(
            f"{slide['images']} image(s), {slide['charts']} chart(s)"
        )


def render_image_report(report: dict, file_bytes: bytes) -> None:
    st.markdown("### Extraction Report")
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.image(file_bytes, caption=report["name"], width="stretch")
    with right:
        st.markdown("**Vision caption**")
        st.write(report["caption"] or "Caption not available.")
        st.markdown("**OCR text**")
        st.write(report["ocr_text"] or "No text detected.")
        st.markdown("**Detected labels**")
        st.write(
            ", ".join(report["detected_labels"])
            if report["detected_labels"]
            else "No labels detected."
        )
        st.markdown("**Diagram type**")
        st.write(report["diagram_type"])
    render_warnings(report["warnings"])


def render_video_report(
    report: dict,
    video_bytes: bytes,
    location: str = "upload",
) -> None:
    st.markdown("### Extraction Report")
    col1, col2, col3 = st.columns(3)
    col1.metric("Duration", report["duration"])
    col2.metric("Frames sampled", report["frames_sampled"])
    col3.metric("Transcript segments", len(report["segments"]))
    render_warnings(report["warnings"])
    st.video(video_bytes)

    if not report["segments"]:
        st.info("No speech was detected in the video.")
        return

    st.markdown("**Transcript timeline**")
    for segment in report["segments"]:
        if st.button(
            f"{segment['start']}  {segment['text'][:90]}",
            key=(
                f"video_jump_{location}_{report['name']}_"
                f"{segment['start_seconds']}"
            ),
        ):
            st.session_state[f"video_selected_timestamp_{report['name']}"] = (
                segment["start_seconds"]
            )
        st.caption(segment["text"])
