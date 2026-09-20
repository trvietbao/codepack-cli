"""Tests for tokenizer and metrics engine."""

import unittest
from codepack.tokenizer import estimate_tokens, compute_file_stats, format_bytes, format_tokens


class TestTokenizer(unittest.TestCase):
    def test_estimate_tokens_empty(self):
        self.assertEqual(estimate_tokens(""), 0)

    def test_estimate_tokens_words(self):
        text = "def calculate_total(items, discount=0.1):"
        tokens = estimate_tokens(text)
        self.assertGreater(tokens, 5)
        self.assertLess(tokens, 20)

    def test_compute_file_stats(self):
        content = "line 1\nline 2\nline 3\n"
        stats = compute_file_stats("example.py", content)
        self.assertEqual(stats.path, "example.py")
        self.assertEqual(stats.lines, 3)
        self.assertGreater(stats.size_bytes, 0)
        self.assertGreater(stats.tokens, 0)

    def test_format_bytes(self):
        self.assertEqual(format_bytes(500), "500 B")
        self.assertEqual(format_bytes(2048), "2.0 KB")
        self.assertEqual(format_bytes(1048576 * 3), "3.00 MB")

    def test_format_tokens(self):
        self.assertEqual(format_tokens(500), "500")
        self.assertEqual(format_tokens(1500), "1.5k")
        self.assertEqual(format_tokens(2500000), "2.50M")


if __name__ == "__main__":
    unittest.main()
