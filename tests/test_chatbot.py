import unittest
from chatbot import Conversation, respond
from classifier import classify, INTENTS
from entities import extract
from retriever import retrieve
from llm import ModelReply


class ConversationTests(unittest.TestCase):
    def test_intent_explanation_preserves_exact_names_without_model(self):
        def forbidden(*args):
            self.fail("Verified intent definitions must not be rewritten by the model")
        for question in ("Explain intents", "Find notes about intents"):
            with self.subTest(question=question):
                answer = respond(question, Conversation(), generator=forbidden)
                for intent in INTENTS:
                    self.assertIn("**" + intent + "**", answer)
                self.assertNotIn("assignment_help", answer)
                self.assertNotIn("textbook", answer)
                self.assertNotIn("lecture slide", answer)
                self.assertIn("[intents-notes]", answer)
                self.assertIn("Response mode: verified_source", answer)


    def test_natural_submission_phrase(self):
        self.assertEqual(classify("What do I need to turn in for capstone?"), "assignment_guidance")

    def test_memory_alias(self):
        self.assertIn("state-notes", respond("Help me understand conversation memory", Conversation()))

    def test_multiple_topics_request_clarification(self):
        state = Conversation()
        self.assertIn("one topic", respond("Explain intents and grounding", state))
        self.assertEqual(state, Conversation())

    def test_four_intents(self):
        examples = {
            "Find notes about intents": "resource_lookup",
            "Explain slot filling": "concept_help",
            "Capstone requirements": "assignment_guidance",
            "When is the capstone due?": "course_logistics",
        }
        for text, expected in examples.items():
            with self.subTest(text=text):
                self.assertEqual(classify(text), expected)

    def test_two_slots_across_three_turns(self):
        state = Conversation()
        self.assertIn("Which CSC-128 topic", respond("Find a resource", state))
        self.assertIn("Which resource type", respond("slot filling", state))
        answer = respond("examples", state)
        self.assertEqual(state.slots, {"topic": "slot filling", "resource_type": "examples"})
        self.assertIn("slots-example", answer)
        self.assertIsNone(state.pending)

    def test_instructions_slot_does_not_switch_intent(self):
        state = Conversation()
        respond("Find a resource", state)
        respond("capstone", state)
        self.assertIn("capstone-requirements", respond("instructions", state))
        self.assertEqual(state.intent, "resource_lookup")

    def test_unknown_resource_has_no_model_call(self):
        def forbidden(*args):
            self.fail("No source must mean no model call")
        answer = respond("Find Groq examples", Conversation(), generator=forbidden)
        self.assertIn("do not have a verified source", answer)

    def test_known_source_reaches_model_with_slots(self):
        calls = []
        def fake(*args):
            calls.append(args)
            return ModelReply("A grounded explanation.", "groq")
        answer = respond("Explain slot filling", Conversation(), generator=fake)
        self.assertIn("A grounded explanation.", answer)
        self.assertIn("slots-notes", answer)
        self.assertIn("slot filling", calls[0][0])

    def test_reset(self):
        state = Conversation()
        respond("Find capstone instructions", state)
        respond("reset", state)
        self.assertEqual(state, Conversation())

    def test_sessions_are_isolated(self):
        first, second = Conversation(), Conversation()
        respond("Find capstone instructions", first)
        self.assertEqual(second.slots, {})

    def test_switch_intent_clears_old_resource_type(self):
        state = Conversation()
        respond("Find capstone instructions", state)
        answer = respond("Explain grounding", state)
        self.assertEqual(state.slots, {"topic": "grounding"})
        self.assertIn("grounding-notes", answer)

    def test_new_topic_prompts_for_new_resource_type(self):
        state = Conversation()
        respond("Find capstone instructions", state)
        self.assertIn("Which resource type", respond("slot filling", state))

    def test_unknown_slot_preserves_pending(self):
        state = Conversation()
        respond("Find a resource", state)
        respond("pizza", state)
        self.assertEqual(state.pending, "topic")
        self.assertEqual(state.slots, {})

    def test_refusal_and_handoff(self):
        self.assertIn("cannot complete graded", respond("Write my assignment", Conversation()))
        self.assertIn("instructor", respond("Can I get an extension?", Conversation()))

    def test_scope_and_limits(self):
        self.assertIn("only help with CSC-128", respond("Tell me the weather", Conversation()))
        self.assertIn("1,500", respond("a" * 1501, Conversation()))
        self.assertIn("Please enter", respond(" ", Conversation()))

    def test_entity_boundaries(self):
        self.assertEqual(extract("capital noteworthy"), {})
        self.assertEqual(extract("CAPSTONE NOTES"), {"topic": "capstone", "resource_type": "notes"})

    def test_retrieval_does_not_mix_topics(self):
        records = retrieve("course_logistics", {"topic": "capstone"})
        self.assertEqual([r["id"] for r in records], ["capstone-deadline"])


if __name__ == "__main__":
    unittest.main()
