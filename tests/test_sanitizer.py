"""Tests for secret detection and sanitization."""

import unittest
from codepack.sanitizer import SecretSanitizer


class TestSecretSanitizer(unittest.TestCase):
    def setUp(self):
        self.sanitizer = SecretSanitizer()

    def test_clean_text_remains_unchanged(self):
        text = "def hello_world():\n    return 'Hello, World!'\n"
        res = self.sanitizer.sanitize(text)
        self.assertEqual(res.sanitized_text, text)
        self.assertEqual(res.total_redactions, 0)

    def test_redact_openai_key(self):
        text = 'api_key = "sk-abcdef1234567890abcdef1234567890"'
        res = self.sanitizer.sanitize(text)
        self.assertNotIn("sk-abcdef1234567890abcdef1234567890", res.sanitized_text)
        self.assertIn("[REDACTED: OpenAI API Key]", res.sanitized_text)
        self.assertEqual(res.redactions["OpenAI API Key"], 1)

    def test_redact_github_token(self):
        text = 'github_pat = "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"'
        res = self.sanitizer.sanitize(text)
        self.assertNotIn("ghp_1234567890", res.sanitized_text)
        self.assertIn("[REDACTED: GitHub Token]", res.sanitized_text)
        self.assertEqual(res.redactions["GitHub Token"], 1)

    def test_redact_aws_access_key(self):
        text = 'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"'
        res = self.sanitizer.sanitize(text)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", res.sanitized_text)
        self.assertIn("[REDACTED: AWS Access Key]", res.sanitized_text)

    def test_empty_string_handling(self):
        res = self.sanitizer.sanitize("")
        self.assertEqual(res.sanitized_text, "")
        self.assertEqual(res.total_redactions, 0)


if __name__ == "__main__":
    unittest.main()
