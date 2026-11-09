"""Small deterministic tests; model and corpus are tested separately."""
import unittest
from rag_prototype import answer, chunks, FALLBACK


class Embedder:
    def encode(self, *_args, **_kwargs):
        import numpy as np
        return np.array([[1.0, 0.0]])


class Collection:
    def __init__(self, distance): self.distance = distance
    def count(self): return 1
    def query(self, **kwargs):
        return {"documents":[["Fictional fan evidence"]], "metadatas":[[{"file":"test.pdf", "page":2}]], "distances":[[self.distance]]}


class RagTests(unittest.TestCase):
    def test_chunk_overlap(self):
        self.assertEqual(list(chunks("a b c d e f", size=4, overlap=2)), ["a b c d", "c d e f"])
    def test_sensitive_query_is_blocked(self):
        text, sources = answer("What is the API key?", Collection(.1), Embedder(), lambda _: "bad")
        self.assertIn("does not answer", text); self.assertEqual(sources, [])
    def test_weak_retrieval_abstains(self):
        text, sources = answer("What happened?", Collection(.9), Embedder(), lambda _: "bad")
        self.assertEqual(text, FALLBACK); self.assertEqual(sources, [])
    def test_source_page_is_returned(self):
        text, sources = answer("What happened?", Collection(.1), Embedder(), lambda _: "A fan issue")
        self.assertEqual(text, "A fan issue"); self.assertEqual(sources[0]["page"], 2)


if __name__ == "__main__": unittest.main()
