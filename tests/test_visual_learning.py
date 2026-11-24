import tempfile
import unittest
from pathlib import Path

from visual_learning import (
    generate_concept_map,
    generate_explainer_video,
    generate_flowchart,
    generate_narrated_lesson_script,
    generate_revision_infographic,
)
from visuals.builder import build_visual
from visuals.renderer import (
    render_concept_map,
    render_flowchart,
    render_revision_sheet,
)
from visuals.schema import repair_json, validate_nodes_edges


class VisualLearningTests(unittest.TestCase):
    def test_generators_write_viewable_local_resources(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [
                generate_concept_map("Clustering", ["Points", "Centroids"], directory),
                generate_flowchart("Study", ["Read", "Practice"], directory),
                generate_revision_infographic("Clustering", ["Recall"], directory),
                generate_narrated_lesson_script("Clustering", ["Recall"], directory),
            ]
            self.assertTrue(all(Path(path).exists() for path in paths))
            self.assertIn("<svg", Path(paths[0]).read_text(encoding="utf-8"))
            self.assertIn("Lesson: Clustering", Path(paths[-1]).read_text(encoding="utf-8"))

    def test_explainer_video_is_assembled_when_tools_are_available(self):
        with tempfile.TemporaryDirectory() as directory:
            try:
                path = generate_explainer_video("Clustering", ["Recall"], directory)
            except RuntimeError as error:
                self.skipTest(str(error))
            self.assertTrue(Path(path).exists())
            self.assertGreater(Path(path).stat().st_size, 0)

    def test_structured_visual_schema_rejects_bad_data(self):
        with self.assertRaises(ValueError):
            validate_nodes_edges({"nodes": [], "edges": []})

    def test_json_repair_and_svg_renderers(self):
        data = repair_json(
            '```json\n{"nodes":[{"id":"topic","label":"Clustering","group":"Core"}],'
            '"edges":[]}\n```'
        )
        data = validate_nodes_edges(data)
        concept = render_concept_map(data, "Clustering", "Source: PDF Page 1")
        flow = render_flowchart(
            build_visual("flow", "Clustering", ["Points", "Distance"]),
            "Clustering",
            "Source: Slide 2",
        )
        revision = render_revision_sheet(
            build_visual("revision", "Clustering", ["Points", "Distance"]),
            "Source: Video 00:20",
        )
        self.assertIn("<svg", concept)
        self.assertIn("<svg", flow)
        self.assertIn("<svg", revision)
