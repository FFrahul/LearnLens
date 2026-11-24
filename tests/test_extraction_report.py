import unittest
from pathlib import Path

from extraction_report.reporters import build_pdf_report, build_pptx_report
from ingestion.pipeline import clean_text, file_signature, split_text


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "sample_materials"


class ExtractionReportTests(unittest.TestCase):
    def test_pdf_report_contains_real_counts(self):
        report = build_pdf_report(
            "kmeans_notes.pdf",
            (SAMPLES / "kmeans_notes.pdf").read_bytes(),
        )
        self.assertEqual(report["type"], "pdf")
        self.assertGreater(report["page_count"], 0)
        self.assertGreaterEqual(report["total_words"], 0)
        self.assertEqual(len(report["pages"]), report["page_count"])

    def test_pptx_report_contains_slides(self):
        report = build_pptx_report(
            "Clustering_Lecture.pptx",
            (SAMPLES / "Clustering_Lecture.pptx").read_bytes(),
        )
        self.assertEqual(report["type"], "pptx")
        self.assertGreater(report["slide_count"], 0)
        self.assertEqual(len(report["slides"]), report["slide_count"])

    def test_chunk_helpers_are_deterministic(self):
        text = "  Hierarchical clustering\n\ncreates  a dendrogram.  "
        chunks = split_text(text, chunk_size=20, overlap=4)
        self.assertTrue(chunks)
        self.assertEqual(clean_text(text), "Hierarchical clustering\n\ncreates a dendrogram.")
        first = file_signature("notes.pdf", b"sample")
        self.assertEqual(first, file_signature("notes.pdf", b"sample"))
