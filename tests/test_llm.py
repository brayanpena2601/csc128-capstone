import unittest
from types import SimpleNamespace
from unittest.mock import Mock
import httpx
from groq import APIConnectionError, AuthenticationError, RateLimitError, APITimeoutError, InternalServerError
from llm import generate

RECORDS = [{"id": "test", "text": "Verified source text."}]


class ModelTests(unittest.TestCase):
    def test_missing_key(self):
        self.assertEqual(generate("question", RECORDS).status, "offline")

    def test_success(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Grounded answer"))])
        self.assertEqual(generate("question", RECORDS, client=client).status, "groq")

    def test_empty(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))])
        self.assertEqual(generate("question", RECORDS, client=client).status, "empty")

    def test_failures_are_safe_and_keep_sources(self):
        request = httpx.Request("POST", "https://api.groq.com")
        cases = [
            (RateLimitError("sensitive internal text", response=httpx.Response(429, request=request), body=None), "rate_limit"),
            (AuthenticationError("sensitive internal text", response=httpx.Response(401, request=request), body=None), "api_error"),
            (APIConnectionError(request=request), "api_error"),
            (APITimeoutError(request=request), "api_error"),
            (InternalServerError("sensitive internal text", response=httpx.Response(503, request=request), body=None), "api_error"),
        ]
        for error, status in cases:
            with self.subTest(status=status):
                client = Mock()
                client.chat.completions.create.side_effect = error
                answer = generate("question", RECORDS, client=client)
                self.assertEqual(answer.status, status)
                self.assertIn("Verified source text", answer.text)
                self.assertNotIn("sensitive internal text", answer.text)


if __name__ == "__main__":
    unittest.main()
