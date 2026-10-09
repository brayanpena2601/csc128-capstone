import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
from retriever import SourceError


class AppTests(unittest.TestCase):
    def test_source_failure_does_not_reach_page_as_exception(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=15).run()
        app.toggle[0].set_value(False).run()
        with patch("chatbot.retrieve", side_effect=SourceError("PRIVATE DETAILS")):
            app.chat_input[0].set_value("Explain grounding").run()
        self.assertEqual(len(app.exception), 0)
        answer = app.session_state["messages"][-1]["content"]
        self.assertIn("sources are temporarily unavailable", answer)
        self.assertNotIn("PRIVATE DETAILS", answer)

    def test_disclosure_slots_and_reset(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=15).run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("software chatbot", app.info[0].value)
        app.toggle[0].set_value(False).run()
        app.chat_input[0].set_value("Find a resource").run()
        app.chat_input[0].set_value("slot filling").run()
        app.chat_input[0].set_value("examples").run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("slots-example", app.session_state["messages"][-1]["content"])
        app.button[0].click().run()
        self.assertEqual(app.session_state["messages"], [])
        self.assertEqual(app.session_state["conversation"].slots, {})


if __name__ == "__main__":
    unittest.main()
