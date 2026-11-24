import unittest

from knowledge_graph import build_knowledge_graph


class KnowledgeGraphTests(unittest.TestCase):
    def test_builds_topic_concept_and_prerequisite_edges(self):
        graph = build_knowledge_graph(
            [
                {
                    "topic": "Clustering",
                    "subtopic": "Hierarchical clustering",
                    "key_concepts": ["Dendrogram"],
                    "prerequisites": ["Distance metrics"],
                }
            ]
        )

        labels = {node["label"] for node in graph["nodes"]}
        relationships = {edge["relation"] for edge in graph["edges"]}
        self.assertEqual(
            labels,
            {
                "Clustering",
                "Hierarchical clustering",
                "Dendrogram",
                "Distance metrics",
            }
        )
        self.assertEqual(
            relationships,
            {"contains", "covers", "precedes"}
        )


if __name__ == "__main__":
    unittest.main()
