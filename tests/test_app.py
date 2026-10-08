import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_disclosure_slots_and_reset(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
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
