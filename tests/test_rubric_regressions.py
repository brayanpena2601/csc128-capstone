"""Independent paraphrases and fault injection from the rubric review."""
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace
from chatbot import Conversation, respond
from classifier import classify
from llm import generate, ModelReply


class RubricRegressionTests(unittest.TestCase):
    def test_software_disclosure_requirement_is_exact(self):
        def forbidden(*args):
            self.fail("Assignment requirements must not be reinterpreted by Groq")
        answer = respond("What is required for the capstone?", Conversation(), generator=forbidden)
        self.assertIn("Disclose to the user that the chatbot is software", answer)
        self.assertNotIn("license", answer.lower())
        self.assertIn("Response mode: verified_source", answer)

    def test_intent_explanation_includes_working_examples(self):
        answer = respond("Explain intents with examples", Conversation())
        examples = {
            "Find notes about slot filling.": "resource_lookup",
            "How does slot filling work?": "concept_help",
            "What is required for the capstone?": "assignment_guidance",
            "When is the capstone due?": "course_logistics",
        }
        for example, intent in examples.items():
            with self.subTest(example=example):
                self.assertIn(example, answer)
                self.assertEqual(classify(example), intent)

    def test_assignment_paraphrases(self):
        for text in ("What is required for the capstone?", "What do I need to include in the capstone?", "Capstone checklist"):
            with self.subTest(text=text):
                self.assertEqual(classify(text), "assignment_guidance")
                self.assertIn("capstone-requirements", respond(text, Conversation()))

    def test_concept_paraphrases(self):
        for text in ("How does slot filling work?", "Describe grounding", "Define intents", "Explain intents with examples"):
            with self.subTest(text=text):
                self.assertEqual(classify(text), "concept_help")
                self.assertIn("**Sources**", respond(text, Conversation()))

    def test_explicit_lookup_still_wins(self):
        self.assertEqual(classify("Where can I find capstone instructions?"), "resource_lookup")

    def test_cross_intent_followup_keeps_topic(self):
        state = Conversation()
        respond("Capstone requirements", state)
        answer = respond("When is it due?", state)
        self.assertIn("capstone-deadline", answer)
        self.assertEqual(state.slots, {"topic": "capstone"})

    def test_fresh_pronoun_does_not_guess_topic(self):
        self.assertIn("Which CSC-128 topic", respond("When is it due?", Conversation()))

    def test_explicit_topic_overrides_context(self):
        state = Conversation()
        respond("Capstone requirements", state)
        self.assertIn("grounding-notes", respond("Explain grounding", state))
        self.assertEqual(state.slots, {"topic": "grounding"})

    def test_source_storage_failures_are_actionable(self):
        for content in (None, "broken json", "{}", '[{"id":"bad"}]'):
            with self.subTest(content=content), patch("retriever.DATA_PATH") as path:
                if content is None:
                    path.read_text.side_effect = FileNotFoundError("PRIVATE DETAILS")
                else:
                    path.read_text.return_value = content
                answer = respond("Explain grounding", Conversation())
                self.assertIn("sources are temporarily unavailable", answer)
                self.assertIn("LMS", answer)
                self.assertNotIn("PRIVATE DETAILS", answer)

    def test_unexpected_turn_error_restores_state(self):
        state = Conversation()
        respond("Find a resource", state)
        def broken(*args):
            raise RuntimeError("PRIVATE DETAILS")
        answer = respond("Explain grounding", state, generator=broken)
        self.assertIn("try again or reset", answer)
        self.assertNotIn("PRIVATE DETAILS", answer)
        self.assertEqual(state.intent, "resource_lookup")
        self.assertEqual(state.pending, "topic")

    def test_empty_choices(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(choices=[])
        answer = generate("question", [{"text":"Verified text"}], client=client)
        self.assertEqual(answer.status, "empty")
        self.assertIn("Verified text", answer.text)

    def test_truncated_answer_replaced_with_complete_source(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(choices=[
            SimpleNamespace(finish_reason="length", message=SimpleNamespace(content="HALF SENTENCE"))])
        answer = generate("question", [{"text":"Complete verified text."}], client=client)
        self.assertEqual(answer.status, "truncated")
        self.assertNotIn("HALF SENTENCE", answer.text)
        self.assertIn("Complete verified text.", answer.text)

    def test_malformed_response(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(choices=None)
        self.assertEqual(generate("question", [{"text":"Source"}], client=client).status, "empty")
        client.chat.completions.create.return_value = SimpleNamespace()
        self.assertEqual(generate("question", [{"text":"Source"}], client=client).status, "unexpected_error")

    def test_unexpected_sdk_error_does_not_leak_details(self):
        client = Mock()
        client.chat.completions.create.side_effect = RuntimeError("PRIVATE DETAILS")
        answer = generate("question", [{"text":"Source"}], client=client)
        self.assertEqual(answer.status, "unexpected_error")
        self.assertNotIn("PRIVATE DETAILS", answer.text)


if __name__ == "__main__":
    unittest.main()
