"""Build transparent extraction reports for supported file types."""

from __future__ import annotations

import shutil
from io import BytesIO
from typing import Iterable

import pymupdf as fitz
from PIL import Image
from pptx import Presentation


def _headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        line = " ".join(line.split())
        if not line:
            continue
        words = line.split()
        is_short = len(line) <= 80
        is_title = line.upper() == line or line.istitle()
        if is_short and is_title and 1 <= len(words) <= 12:
            headings.append(line)
    return list(dict.fromkeys(headings))[:8]


def build_pdf_report(file_name: str, file_bytes: bytes) -> dict:
    document = fitz.open(stream=file_bytes, filetype="pdf")
    pages: list[dict] = []
    text_pages = 0
    scanned_pages = 0
    table_count = 0
    image_count = 0
    total_words = 0
    ocr_used = False
    warnings: list[str] = []

    tesseract = shutil.which("tesseract")
    if tesseract:
        try:
            import pytesseract
        except ImportError:
            pytesseract = None
    else:
        pytesseract = None

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()
        if text:
            text_pages += 1
        else:
            scanned_pages += 1
            if pytesseract:
                try:
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                    text = pytesseract.image_to_string(
                        Image.open(BytesIO(pix.tobytes("png")))
                    ).strip()
                    if text:
                        ocr_used = True
                        text_pages += 1
                        scanned_pages -= 1
                except Exception:
                    text = ""

        tables = page.find_tables()
        try:
            page_table_count = len(tables.tables)
        except Exception:
            page_table_count = 0
        table_count += page_table_count

        images = page.get_images(full=True)
        page_image_count = len(images)
        image_count += page_image_count
        total_words += len(text.split())

        pix = page.get_pixmap(matrix=fitz.Matrix(0.8, 0.8), alpha=False)
        pages.append({
            "number": page_number,
            "text": text,
            "headings": _headings(text),
            "tables": page_table_count,
            "images": page_image_count,
            "scanned": not bool(page.get_text("text").strip()),
            "thumbnail": pix.tobytes("png"),
        })

    if scanned_pages:
        if pytesseract:
            warnings.append(
                f"{scanned_pages} page(s) look scanned or contain little text."
            )
        else:
            warnings.append(
                f"{scanned_pages} page(s) look scanned. OCR is not available "
                "because Tesseract is not installed."
            )

    return {
        "type": "pdf",
        "name": file_name,
        "page_count": len(document),
        "text_pages": text_pages,
        "scanned_pages": scanned_pages,
        "headings_count": sum(len(p["headings"]) for p in pages),
        "tables": table_count,
        "images": image_count,
        "total_words": total_words,
        "ocr_used": ocr_used,
        "pages": pages,
        "warnings": warnings,
    }


def build_pptx_report(file_name: str, file_bytes: bytes) -> dict:
    presentation = Presentation(BytesIO(file_bytes))
    slides: list[dict] = []
    image_count = 0
    chart_count = 0
    warnings: list[str] = []

    for slide_number, slide in enumerate(presentation.slides, start=1):
        title = ""
        bullet_text: list[str] = []
        speaker_notes = ""
        slide_images = 0
        slide_charts = 0

        for shape in slide.shapes:
            shape_type = getattr(shape, "shape_type", None)
            if shape_type == 13:
                slide_images += 1
            if shape_type == 3:
                slide_charts += 1
            if getattr(shape, "has_text_frame", False):
                text = " ".join(
                    line.strip()
                    for line in shape.text.splitlines()
                    if line.strip()
                )
                if not text:
                    continue
                try:
                    placeholder_type = shape.placeholder_format.type
                    if placeholder_type and "TITLE" in str(placeholder_type).upper():
                        title = text
                    elif placeholder_type:
                        bullet_text.append(text)
                    else:
                        bullet_text.append(text)
                except Exception:
                    bullet_text.append(text)

            if getattr(shape, "has_table", False):
                table_lines = []
                for row in shape.table.rows:
                    table_lines.append(
                        " | ".join(cell.text.strip() for cell in row.cells)
                    )
                bullet_text.append("\n".join(table_lines))

        try:
            notes_frame = slide.notes_slide.notes_text_frame
            speaker_notes = " ".join(
                line.strip()
                for line in notes_frame.text.splitlines()
                if line.strip()
            )
        except Exception:
            speaker_notes = ""

        if not title:
            title = f"Slide {slide_number}"
        if not bullet_text and not speaker_notes:
            warnings.append(
                f"Slide {slide_number} appears to contain no extracted text."
            )

        image_count += slide_images
        chart_count += slide_charts
        slides.append({
            "number": slide_number,
            "title": title,
            "bullets": bullet_text,
            "speaker_notes": speaker_notes,
            "images": slide_images,
            "charts": slide_charts,
        })

    return {
        "type": "pptx",
        "name": file_name,
        "slide_count": len(presentation.slides),
        "images": image_count,
        "charts": chart_count,
        "slides": slides,
        "warnings": list(dict.fromkeys(warnings)),
    }


def build_image_report(
    file_name: str,
    file_bytes: bytes,
    mime_type: str,
    caption: str = "",
) -> dict:
    ocr_text = ""
    tesseract = shutil.which("tesseract")
    if tesseract:
        try:
            import pytesseract
            image = Image.open(BytesIO(file_bytes)).convert("RGB")
            ocr_text = pytesseract.image_to_string(image).strip()
        except Exception:
            ocr_text = ""

    lower_caption = caption.lower()
    if any(word in lower_caption for word in ("flow", "diagram", "chart", "graph")):
        diagram_type = "Flowchart or diagram"
    elif any(word in lower_caption for word in ("table", "grid")):
        diagram_type = "Table"
    else:
        diagram_type = "General image"

    warnings = []
    if tesseract is None:
        warnings.append("OCR is not available because Tesseract is not installed.")

    return {
        "type": "image",
        "name": file_name,
        "mime_type": mime_type,
        "caption": caption,
        "ocr_text": ocr_text,
        "detected_labels": [],
        "diagram_type": diagram_type,
        "bytes": file_bytes,
        "warnings": warnings,
    }
